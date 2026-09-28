import asyncio
import hashlib
import json
import os
from pathlib import Path
import signal
import sys
import time
import uuid
import warnings


ACCESS_TOOLS = {
    "none": [],
    "read": ["Read", "Glob", "Grep"],
    "edit": ["Read", "Glob", "Grep", "Edit", "Write"],
}


def emit(base, event_type, **fields):
    print(
        json.dumps({**base, "type": event_type, **fields}, ensure_ascii=False),
        flush=True,
    )


class Clock:
    def __init__(self):
        self.started = time.monotonic()
        self.paused = 0
        self.pause_started = None

    def pause(self):
        self.pause_started = time.monotonic()

    def resume(self):
        self.paused += time.monotonic() - self.pause_started
        self.pause_started = None

    def elapsed(self):
        end = self.pause_started if self.pause_started is not None else time.monotonic()
        return end - self.started - self.paused


class InputLines:
    def __init__(self):
        self.queue = asyncio.Queue()
        self.buffer = b""
        self.loop = asyncio.get_running_loop()
        self.fd = sys.stdin.fileno()
        self.active = False

    def read_ready(self):
        data = os.read(self.fd, 65536)
        if not data:
            self.close()
            self.queue.put_nowait(None)
            return
        self.buffer += data
        while b"\n" in self.buffer:
            line, self.buffer = self.buffer.split(b"\n", 1)
            self.queue.put_nowait(line)

    async def read(self):
        if not self.active and self.queue.empty():
            self.loop.add_reader(self.fd, self.read_ready)
            self.active = True
        return await self.queue.get()

    def close(self):
        if self.active:
            self.loop.remove_reader(self.fd)
            self.active = False


class Approvals:
    def __init__(self, job, clock, sdk):
        self.job = job
        self.clock = clock
        self.sdk = sdk
        self.lock = asyncio.Lock()
        self.input = None
        self.denials = []
        self.ending = None

    async def require_review(self, data, tool_use_id, context):
        return {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "ask" if self.job["workflow"] else "deny",
                "permissionDecisionReason": "Review this workflow through the host approval channel.",
            }
        }

    def snapshot(self, data):
        snapshot = json.loads(json.dumps(data))
        source = snapshot.pop("scriptPath", None)
        if source and not snapshot.get("script"):
            path = Path(source).expanduser()
            if not path.is_absolute():
                path = Path(self.job["cwd"]) / path
            snapshot["script"] = path.read_text(encoding="utf-8")
        if (
            not isinstance(snapshot.get("script"), str)
            or not snapshot["script"].strip()
        ):
            raise ValueError("Workflow supplied no script")
        digest = hashlib.sha256(
            json.dumps(snapshot, sort_keys=True, ensure_ascii=False).encode()
        ).hexdigest()
        return snapshot, digest

    def deny(self, name, context, reason):
        self.denials.append(
            {
                "tool_name": name,
                "tool_use_id": getattr(context, "tool_use_id", None),
                "reason": reason,
            }
        )
        return self.sdk.PermissionResultDeny(message=reason)

    def end(self, name, context, status, reason):
        self.ending = (status, reason)
        return self.deny(name, context, reason)

    async def decide(self, name, data, context):
        if self.ending:
            return self.deny(name, context, self.ending[1])
        if name != "Workflow" or not self.job["workflow"]:
            return self.deny(
                name,
                context,
                "This tool request needs permission outside the workflow approval channel.",
            )
        async with self.lock:
            if self.ending:
                return self.deny(name, context, self.ending[1])
            try:
                snapshot, digest = self.snapshot(data)
            except (OSError, ValueError, UnicodeError) as exc:
                return self.deny(name, context, str(exc))
            request_id = str(uuid.uuid4())
            if self.input is None:
                self.input = InputLines()
            self.clock.pause()
            emit(
                self.job["base"],
                "approval_required",
                request_id=request_id,
                input_sha256=digest,
                title=getattr(context, "title", None) or "Review dynamic workflow",
                tool_input=snapshot,
            )
            try:
                async with asyncio.timeout(self.job["approval_timeout"]):
                    while True:
                        line = await self.input.read()
                        if line is None:
                            return self.end(
                                name,
                                context,
                                "denied",
                                "Approval input closed before a decision.",
                            )
                        try:
                            decision = json.loads(line)
                            matches = (
                                isinstance(decision, dict)
                                and decision.get("type") == "approval"
                                and decision.get("request_id") == request_id
                                and decision.get("input_sha256") == digest
                            )
                        except (ValueError, UnicodeError):
                            matches = False
                        if not matches or decision.get("decision") not in (
                            "approve",
                            "deny",
                        ):
                            emit(
                                self.job["base"],
                                "control_error",
                                error="Decision must match the pending request ID and input hash.",
                            )
                            continue
                        if decision["decision"] == "deny":
                            return self.end(
                                name,
                                context,
                                "denied",
                                "The user declined this workflow.",
                            )
                        emit(
                            self.job["base"],
                            "approval_accepted",
                            request_id=request_id,
                            input_sha256=digest,
                        )
                        return self.sdk.PermissionResultAllow(updated_input=snapshot)
            except TimeoutError:
                return self.end(name, context, "timed_out", "Approval wait expired.")
            except (OSError, ValueError) as exc:
                return self.deny(
                    name, context, "Approval input unavailable: " + str(exc)
                )
            finally:
                self.clock.resume()

    def close(self):
        if self.input is not None:
            self.input.close()


class Results:
    def __init__(self, job, sdk):
        self.job = job
        self.sdk = sdk
        self.latest = None
        self.models = set()
        self.denials = []
        self.tasks = {}
        self.sequence = 0
        self.result_sequence = 0
        self.completion_sequence = 0
        self.last_progress = 0

    def accept(self, message):
        self.sequence += 1
        if isinstance(message, self.sdk.ResultMessage):
            if message.session_id != self.job["base"]["session_id"]:
                raise ValueError("Claude returned a different session ID")
            self.latest = message
            self.result_sequence = self.sequence
            self.models.update(message.model_usage or {})
            self.denials.extend(message.permission_denials or [])
        elif isinstance(message, self.sdk.TaskStartedMessage):
            if message.task_type in ("workflow", "local_workflow"):
                self.tasks[message.task_id] = {
                    "status": "running",
                    "description": message.description,
                }
                emit(
                    self.job["base"],
                    "workflow_started",
                    task_id=message.task_id,
                    description=message.description,
                )
        elif isinstance(message, self.sdk.TaskNotificationMessage):
            if message.task_id in self.tasks:
                self.tasks[message.task_id]["status"] = message.status
                self.completion_sequence = self.sequence
                emit(
                    self.job["base"],
                    "workflow_finished",
                    task_id=message.task_id,
                    status=message.status,
                    summary=message.summary,
                )
        elif isinstance(message, self.sdk.TaskProgressMessage):
            if (
                message.task_id in self.tasks
                and time.monotonic() - self.last_progress >= 2
            ):
                self.last_progress = time.monotonic()
                emit(
                    self.job["base"],
                    "progress",
                    task_id=message.task_id,
                    description=message.description,
                    usage=message.usage,
                )

    def finish(self, approvals, reason=None, error=None):
        latest = self.latest
        fields = {
            "result": latest.result if latest else "",
            "models": sorted(self.models),
            "workflows": self.tasks,
            "permission_denials": self.denials + approvals.denials,
        }
        if reason:
            status = reason
        elif error:
            status = "failed"
        elif approvals.ending:
            status = approvals.ending[0]
        elif fields["permission_denials"]:
            status = "needs_permission"
        elif latest is None or latest.is_error or latest.subtype != "success":
            status = "failed"
            error = (
                getattr(latest, "errors", None)
                or "Claude returned no successful result"
            )
        elif self.job["workflow"] and not self.tasks:
            status, error = "workflow_not_started", "No workflow launch was observed"
        elif (
            any(task["status"] != "completed" for task in self.tasks.values())
            or self.result_sequence < self.completion_sequence
        ):
            status, error = (
                "incomplete",
                "The workflow or its final synthesis did not complete",
            )
        else:
            status = "completed"
        if error:
            fields["error"] = error
        emit(self.job["base"], "result", status=status, **fields)
        return {
            "completed": 0,
            "denied": 3,
            "needs_permission": 3,
            "timed_out": 124,
            "cancelled": 130,
        }.get(status, 1)


async def run(job, sdk):
    clock = Clock()
    approvals = Approvals(job, clock, sdk)
    results = Results(job, sdk)
    tools = list(ACCESS_TOOLS[job["access"]])
    allowed = list(tools)
    if job["allow_command"]:
        tools.append("Bash")
        allowed.extend("Bash(" + rule + ")" for rule in job["allow_command"])
    if job["workflow"]:
        tools.append("Workflow")
    options = sdk.ClaudeAgentOptions(
        cli_path=job["cli_path"],
        cwd=job["cwd"],
        session_id=None if job["resume"] else job["base"]["session_id"],
        resume=job["resume"],
        model=job["model"],
        effort=job["effort"],
        tools=tools,
        allowed_tools=allowed,
        system_prompt={"type": "preset", "preset": "claude_code"},
        setting_sources=["user", "project", "local"],
        permission_mode=job["permission_mode"],
        env=job["claude_env"],
        can_use_tool=approvals.decide,
        hooks={
            "PreToolUse": [
                sdk.HookMatcher(matcher="Workflow", hooks=[approvals.require_review])
            ]
        },
    )

    async def consume():
        async for message in sdk.query(prompt=job["prompt"], options=options):
            results.accept(message)

    task = asyncio.create_task(consume())
    reason = None

    def stop(status):
        nonlocal reason
        if reason is None and not task.done():
            reason = status
            emit(job["base"], "_shutdown", status=status)
            task.cancel()

    async def watch_clock():
        while not task.done():
            if clock.elapsed() >= job["timeout"]:
                stop("timed_out")
                return
            await asyncio.sleep(0.05)

    loop = asyncio.get_running_loop()
    for signum in (signal.SIGTERM, signal.SIGINT, signal.SIGHUP):
        loop.add_signal_handler(signum, stop, "cancelled")
    watch = asyncio.create_task(watch_clock())
    error = None
    emit(job["base"], "started", workflow=job["workflow"])
    try:
        await task
    except asyncio.CancelledError:
        reason = reason or "cancelled"
    except Exception as exc:
        error = str(exc)
    finally:
        watch.cancel()
        await asyncio.gather(watch, return_exceptions=True)
        approvals.close()
    return results.finish(approvals, reason, error)


def main():
    with os.fdopen(int(sys.argv[1]), encoding="utf-8") as request:
        job = json.load(request)
    try:
        import claude_agent_sdk as sdk
        from claude_agent_sdk import types

        for name in (
            "PermissionResultAllow",
            "PermissionResultDeny",
            "HookMatcher",
            "ResultMessage",
            "TaskStartedMessage",
            "TaskNotificationMessage",
            "TaskProgressMessage",
        ):
            setattr(sdk, name, getattr(types, name))
        # file tools are deliberately approved before the workflow callback
        warning = getattr(types, "CanUseToolShadowedWarning", None)
        if warning:
            warnings.filterwarnings("ignore", category=warning)
    except ImportError:
        emit(
            job["base"],
            "result",
            status="dependency_missing",
            error="Run scripts/install_runtime.py to install the pinned Claude Agent SDK.",
        )
        return 2
    try:
        return asyncio.run(run(job, sdk))
    except Exception as exc:
        emit(job["base"], "result", status="failed", error=str(exc))
        return 1


if __name__ == "__main__":
    sys.exit(main())

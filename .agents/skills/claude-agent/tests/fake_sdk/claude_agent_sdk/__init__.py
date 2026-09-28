import asyncio
import json
import os
from pathlib import Path
from types import SimpleNamespace

from .types import ClaudeAgentOptions as ClaudeAgentOptions
from .types import ResultMessage, TaskStartedMessage, TaskNotificationMessage


async def query(prompt, options):
    cwd = Path(options.cwd)
    case = os.environ.get("FAKE_SDK_CASE", "success")
    session = options.resume or options.session_id
    (cwd / "sdk.pid").write_text(str(os.getpid()))
    selected = {
        key: getattr(options, key, None)
        for key in [
            "model",
            "effort",
            "cwd",
            "tools",
            "allowed_tools",
            "permission_mode",
            "system_prompt",
            "setting_sources",
            "env",
            "session_id",
            "resume",
        ]
    }
    (cwd / "sdk-options.json").write_text(json.dumps(selected))
    if case == "stubborn":
        child = await asyncio.create_subprocess_exec(options.cli_path, cwd=cwd)
        try:
            await asyncio.sleep(30)
        finally:
            await asyncio.sleep(20)
            child.kill()
            await child.wait()
    if case.startswith("workflow"):
        hook = options.hooks["PreToolUse"][0].hooks[0]
        gate = await hook({"tool_name": "Workflow"}, "call-1", {})
        assert gate["hookSpecificOutput"]["permissionDecision"] == "ask"
        if case == "workflow_concurrent":

            async def request(index):
                return await options.can_use_tool(
                    "Workflow",
                    {"script": f"return {index}"},
                    SimpleNamespace(tool_use_id=f"call-{index}"),
                )

            requests = [asyncio.create_task(request(index)) for index in range(2)]
            await asyncio.sleep(0)
            (cwd / "concurrent-ready").touch()
            decisions = await asyncio.gather(*requests)
            (cwd / "decisions.json").write_text(
                json.dumps([decision.behavior for decision in decisions])
            )
            yield ResultMessage(session_id=session, result="requests resolved")
            return
        count = 2 if case in ("workflow_twice", "workflow_retry") else 1
        for index in range(count):
            data = {
                "script": "export const meta = {name: 'test'}; return 'done'",
                "args": {"scope": "test"},
            }
            if case == "workflow_file":
                data = {"scriptPath": str(cwd / "workflow.js")}
            decision = await options.can_use_tool(
                "Workflow",
                data,
                SimpleNamespace(
                    tool_use_id=f"call-{index}", title="Review test workflow"
                ),
            )
            if decision.behavior != "allow":
                if case == "workflow_retry":
                    continue
                yield ResultMessage(session_id=session, result="not launched")
                return
            (cwd / f"approved-{index}.json").write_text(
                json.dumps(decision.updated_input)
            )
            task_id = f"task-{index}"
            yield TaskStartedMessage(
                task_id=task_id, task_type="local_workflow", description="test workflow"
            )
            yield ResultMessage(session_id=session, result="launched")
            await asyncio.sleep(0.01)
            if case == "workflow_pending":
                return
            status = "failed" if case == "workflow_failed" else "completed"
            yield TaskNotificationMessage(
                task_id=task_id, status=status, summary=status
            )
            if case == "workflow_no_synthesis":
                return
        yield ResultMessage(session_id=session, result="finished")
        return
    if case == "no_result":
        return
    if case == "wrong_session":
        session = "00000000-0000-0000-0000-000000000000"
    yield ResultMessage(
        session_id=session,
        result=json.dumps({"prompt": prompt, "options": selected}),
        is_error=case == "api_error",
        permission_denials=[{"tool_name": "Bash"}] if case == "denied" else [],
    )

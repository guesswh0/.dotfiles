import json
import importlib.util
import os
from pathlib import Path
import selectors
import signal
import subprocess
import sys
import tempfile
import time
import unittest
from unittest import mock
import uuid


ROOT = Path(__file__).resolve().parents[1]
ADAPTER = ROOT / "scripts" / "claude_task.py"
FAKE_SDK = Path(__file__).resolve().parent / "fake_sdk"


class AdapterTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.project = self.root / "project with spaces"
        self.project.mkdir()
        self.bin = self.root / "bin"
        self.bin.mkdir()
        fake = self.bin / "claude"
        fake.write_text(
            "#!"
            + sys.executable
            + '\nimport os,signal,time\nfrom pathlib import Path\nsignal.signal(signal.SIGTERM,signal.SIG_IGN)\nPath("child.pid").write_text(str(os.getpid()))\ntime.sleep(60)\n'
        )
        fake.chmod(0o755)
        self.env = {
            **os.environ,
            "PATH": str(self.bin) + os.pathsep + os.environ["PATH"],
            "CLAUDE_CONFIG_DIR": str(self.root / "config"),
            "PYTHONPATH": str(FAKE_SDK),
            "PYTHONDONTWRITEBYTECODE": "1",
        }
        self.brief = self.root / "brief.txt"
        self.brief.write_text("Review this project")
        self.command = [
            sys.executable,
            "-B",
            str(ADAPTER),
            "--cwd",
            str(self.project),
            "--prompt-file",
            str(self.brief),
        ]
        self.processes = []
        self.addCleanup(self.cleanup_processes)

    def cleanup_processes(self):
        for process in self.processes:
            if process.poll() is None:
                process.terminate()
            try:
                process.communicate(timeout=6)
            except subprocess.TimeoutExpired:
                process.kill()
                process.communicate(timeout=6)
        for name in ["child.pid", "sdk.pid"]:
            path = self.project / name
            if path.exists():
                try:
                    os.kill(int(path.read_text()), signal.SIGKILL)
                except ProcessLookupError:
                    pass

    def start(self, *args, case="success"):
        process = subprocess.Popen(
            [*self.command, *args],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env={**self.env, "FAKE_SDK_CASE": case},
            start_new_session=True,
            bufsize=0,
        )
        self.processes.append(process)
        return process

    def next_event(self, process, desired, timeout=8):
        deadline = time.monotonic() + timeout
        with selectors.DefaultSelector() as selector:
            selector.register(process.stdout, selectors.EVENT_READ)
            while time.monotonic() < deadline:
                if not selector.select(max(0, deadline - time.monotonic())):
                    break
                line = process.stdout.readline()
                if not line:
                    break
                event = json.loads(line)
                if event["type"] == desired:
                    return event
        self.fail(f"no {desired} event")

    def decision(self, process, event, decision="approve", **overrides):
        message = {
            "type": "approval",
            "request_id": event["request_id"],
            "input_sha256": event["input_sha256"],
            "decision": decision,
            **overrides,
        }
        process.stdin.write((json.dumps(message) + "\n").encode())
        process.stdin.flush()

    def finish(self, process, timeout=8):
        output, errors = process.communicate(timeout=timeout)
        events = [json.loads(line) for line in output.splitlines()]
        results = [event for event in events if event["type"] == "result"]
        self.assertEqual(len(results), 1, (events, errors.decode()))
        self.assertEqual(
            sum(event["type"] == "approval_required" for event in events),
            0,
            events,
        )
        self.assertNotIn(b"Traceback", errors)
        return results[0]

    def wait_for_file(self, name):
        path = self.project / name
        deadline = time.monotonic() + 5
        while not path.exists() and time.monotonic() < deadline:
            time.sleep(0.01)
        self.assertTrue(path.exists())
        return int(path.read_text())

    def assert_stopped(self, pid):
        deadline = time.monotonic() + 3
        while time.monotonic() < deadline:
            try:
                os.kill(pid, 0)
            except ProcessLookupError:
                return
            time.sleep(0.02)
        self.fail(f"process {pid} is still running")

    def test_normal_result_and_literal_prompt(self):
        prompt = "Кедр $(touch injected) `touch injected`"
        self.brief.write_text(prompt)
        result = self.finish(self.start("--model", "opus", "--effort", "low"))
        self.assertEqual(result["status"], "completed")
        returned = json.loads(result["result"])
        self.assertEqual(returned["prompt"], prompt)
        self.assertFalse((self.project / "injected").exists())
        options = returned["options"]
        self.assertEqual(options["cwd"], str(self.project))
        self.assertEqual(options["setting_sources"], ["user", "project", "local"])
        self.assertEqual(
            options["system_prompt"], {"type": "preset", "preset": "claude_code"}
        )
        self.assertIsNone(options["permission_mode"])
        self.assertEqual(options["model"], "opus")
        self.assertEqual(options["effort"], "low")

    def test_model_and_effort_only_override_when_requested(self):
        cases = [
            ([], None, None),
            (["--model", "sonnet"], "sonnet", None),
            (["--effort", "high"], None, "high"),
        ]
        for arguments, model, effort in cases:
            with self.subTest(arguments=arguments):
                result = self.finish(self.start(*arguments))
                self.assertEqual(result["status"], "completed")
                options = json.loads(result["result"])["options"]
                self.assertEqual(options["model"], model)
                self.assertEqual(options["effort"], effort)
                self.assertEqual(result["requested_model"], model)
                self.assertEqual(result["effort"], effort)

    def test_resume_keeps_id(self):
        session = str(uuid.uuid4())
        result = self.finish(self.start("--resume", session))
        options = json.loads(result["result"])["options"]
        self.assertEqual(result["session_id"], session)
        self.assertEqual(options["resume"], session)
        self.assertIsNone(options["session_id"])

    def test_unset_config_directory_stays_unset_for_native_auth(self):
        spec = importlib.util.spec_from_file_location("entrypoint", ADAPTER)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        environment = {
            key: value for key, value in self.env.items() if key != "CLAUDE_CONFIG_DIR"
        }
        with (
            mock.patch.dict(os.environ, environment, clear=True),
            mock.patch.object(module.Path, "home", return_value=self.root),
            mock.patch.object(sys, "argv", [str(ADAPTER), *self.command[3:]]),
        ):
            job = module.prepare(module.parse_args())
        self.assertEqual(job["claude_env"], {})

    def test_tool_profiles_and_shell_rules(self):
        result = self.finish(
            self.start("--access", "edit", "--allow-command", "git diff *")
        )
        options = json.loads(result["result"])["options"]
        self.assertIn("Write", options["tools"])
        self.assertIn("Bash(git diff *)", options["allowed_tools"])
        self.assertNotIn("Bash", options["allowed_tools"])
        self.assertNotIn("Workflow", options["tools"])

    def test_none_profile_and_mode_override(self):
        result = self.finish(
            self.start("--access", "none", "--permission-mode", "auto")
        )
        options = json.loads(result["result"])["options"]
        self.assertEqual(options["tools"], [])
        self.assertEqual(options["permission_mode"], "auto")

    def test_errors_are_not_success(self):
        for case in ["api_error", "wrong_session", "no_result"]:
            with self.subTest(case=case):
                self.assertEqual(self.finish(self.start(case=case))["status"], "failed")
        self.assertEqual(
            self.finish(self.start(case="denied"))["status"], "needs_permission"
        )

    def test_empty_brief_does_not_start_sdk(self):
        self.brief.write_text(" \n")
        self.assertEqual(self.finish(self.start())["status"], "invalid_input")
        self.assertFalse((self.project / "sdk.pid").exists())

    def test_history_preflight_does_not_start_sdk(self):
        Path(self.env["CLAUDE_CONFIG_DIR"]).write_text("not a directory")
        self.assertEqual(self.finish(self.start())["status"], "history_unwritable")
        self.assertFalse((self.project / "sdk.pid").exists())

    def test_workflow_waits_for_exact_approval_and_final_synthesis(self):
        process = self.start("--workflow", case="workflow")
        event = self.next_event(process, "approval_required")
        self.assertFalse((self.project / "approved-0.json").exists())
        self.decision(process, event, request_id="wrong")
        self.next_event(process, "control_error")
        self.assertFalse((self.project / "approved-0.json").exists())
        self.decision(process, event, input_sha256="wrong")
        self.next_event(process, "control_error")
        self.decision(process, event)
        result = self.finish(process)
        self.assertEqual(result["status"], "completed")
        self.assertEqual(result["result"], "finished")
        self.assertEqual(result["workflows"]["task-0"]["status"], "completed")

    def test_workflow_denial_never_launches(self):
        process = self.start("--workflow", case="workflow")
        event = self.next_event(process, "approval_required")
        self.decision(process, event, "deny")
        result = self.finish(process)
        self.assertEqual(result["status"], "denied")
        self.assertFalse((self.project / "approved-0.json").exists())

    def test_closed_approval_input_never_launches(self):
        process = self.start("--workflow", case="workflow")
        self.next_event(process, "approval_required")
        result = self.finish(process)
        self.assertEqual(result["status"], "denied")
        self.assertFalse((self.project / "approved-0.json").exists())

    def test_approval_cannot_be_reused(self):
        process = self.start("--workflow", case="workflow_twice")
        first = self.next_event(process, "approval_required")
        self.decision(process, first)
        second = self.next_event(process, "approval_required")
        self.assertNotEqual(first["request_id"], second["request_id"])
        self.decision(process, first)
        self.next_event(process, "control_error")
        self.assertFalse((self.project / "approved-1.json").exists())
        self.decision(process, second)
        self.assertEqual(self.finish(process)["status"], "completed")

    def test_script_path_is_frozen_before_approval(self):
        script = self.project / "workflow.js"
        script.write_text("return 'original'")
        process = self.start("--workflow", case="workflow_file")
        event = self.next_event(process, "approval_required")
        script.write_text("return 'changed'")
        self.decision(process, event)
        self.assertEqual(self.finish(process)["status"], "completed")
        approved = json.loads((self.project / "approved-0.json").read_text())
        self.assertEqual(approved["script"], "return 'original'")
        self.assertNotIn("scriptPath", approved)

    def test_approval_wait_does_not_consume_execution_timeout(self):
        process = self.start("--workflow", "--timeout", "0.25", case="workflow")
        event = self.next_event(process, "approval_required")
        time.sleep(0.45)
        self.assertIsNone(process.poll())
        self.decision(process, event)
        self.assertEqual(self.finish(process)["status"], "completed")

    def test_approval_wait_expires_without_launching(self):
        process = self.start(
            "--workflow", "--approval-timeout", "0.15", case="workflow"
        )
        self.next_event(process, "approval_required")
        time.sleep(0.25)
        result = self.finish(process)
        self.assertEqual(result["status"], "timed_out")
        self.assertEqual(
            result["permission_denials"][0]["reason"], "Approval wait expired."
        )
        self.assertFalse((self.project / "approved-0.json").exists())

    def test_closed_approval_channel_rejects_retries(self):
        for ending in ("deny", "eof", "timeout"):
            with self.subTest(ending=ending):
                process = self.start(
                    "--workflow", "--approval-timeout", "0.3", case="workflow_retry"
                )
                event = self.next_event(process, "approval_required")
                if ending == "deny":
                    self.decision(process, event, "deny")
                elif ending == "timeout":
                    process.wait(timeout=3)
                result = self.finish(process)
                self.assertEqual(
                    result["status"], "timed_out" if ending == "timeout" else "denied"
                )
                self.assertEqual(process.returncode, 124 if ending == "timeout" else 3)
                self.assertEqual(len(result["permission_denials"]), 2)
                self.assertEqual(
                    result["permission_denials"][0]["reason"],
                    result["permission_denials"][1]["reason"],
                )
                self.assertFalse((self.project / "approved-1.json").exists())

    def test_queued_requests_observe_closed_approval_channel(self):
        for ending in ("deny", "eof", "timeout"):
            with self.subTest(ending=ending):
                ready = self.project / "concurrent-ready"
                ready.unlink(missing_ok=True)
                process = self.start(
                    "--workflow",
                    "--approval-timeout",
                    "0.5",
                    case="workflow_concurrent",
                )
                event = self.next_event(process, "approval_required")
                deadline = time.monotonic() + 3
                while not ready.exists() and time.monotonic() < deadline:
                    time.sleep(0.01)
                self.assertTrue(ready.exists())
                if ending == "deny":
                    self.decision(process, event, "deny")
                elif ending == "timeout":
                    process.wait(timeout=3)
                result = self.finish(process)
                self.assertEqual(
                    result["status"], "timed_out" if ending == "timeout" else "denied"
                )
                self.assertEqual(process.returncode, 124 if ending == "timeout" else 3)
                self.assertEqual(
                    json.loads((self.project / "decisions.json").read_text()),
                    ["deny", "deny"],
                )

    def test_pending_failed_and_unsynthesized_workflows_are_incomplete(self):
        for case in ["workflow_pending", "workflow_failed", "workflow_no_synthesis"]:
            with self.subTest(case=case):
                process = self.start("--workflow", case=case)
                event = self.next_event(process, "approval_required")
                self.decision(process, event)
                self.assertEqual(self.finish(process)["status"], "incomplete")

    def test_plain_answer_does_not_satisfy_workflow_request(self):
        self.assertEqual(
            self.finish(self.start("--workflow"))["status"], "workflow_not_started"
        )

    def test_parent_signals_stop_sdk_and_claude(self):
        for signum in [signal.SIGTERM, signal.SIGHUP, signal.SIGKILL]:
            with self.subTest(signal=signum):
                for name in ["sdk.pid", "child.pid"]:
                    (self.project / name).unlink(missing_ok=True)
                process = self.start(case="stubborn")
                child = self.wait_for_file("child.pid")
                sdk = self.wait_for_file("sdk.pid")
                if signum == signal.SIGKILL:
                    os.killpg(process.pid, signum)
                else:
                    process.send_signal(signum)
                result = self.finish(process)
                self.assertEqual(result["status"], "cancelled")
                self.assert_stopped(child)
                self.assert_stopped(sdk)

    def test_signal_during_timeout_cleanup_keeps_json_and_stops_children(self):
        process = self.start("--timeout", "1", case="stubborn")
        child = self.wait_for_file("child.pid")
        time.sleep(1.2)
        process.send_signal(signal.SIGTERM)
        result = self.finish(process)
        self.assertEqual(result["status"], "timed_out")
        self.assert_stopped(child)


if __name__ == "__main__":
    unittest.main()

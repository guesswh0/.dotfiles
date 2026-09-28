#!/usr/bin/env python3

import argparse
import json
import math
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import tempfile
import uuid


SCRIPTS = Path(__file__).resolve().parent


def positive_seconds(value):
    number = float(value)
    if not math.isfinite(number) or number <= 0:
        raise argparse.ArgumentTypeError("must be a positive finite number")
    return number


def session_uuid(value):
    try:
        return str(uuid.UUID(value))
    except ValueError as exc:
        raise argparse.ArgumentTypeError("session ID must be a UUID") from exc


def parse_args():
    parser = argparse.ArgumentParser(
        description="Run Claude Code through its SDK; return JSON events."
    )
    parser.add_argument("--cwd", required=True, type=Path)
    parser.add_argument("--prompt-file", default="-", help="UTF-8 brief; - reads stdin")
    parser.add_argument("--resume", type=session_uuid)
    parser.add_argument("--model", help="override Claude's configured model")
    parser.add_argument(
        "--effort",
        choices=["low", "medium", "high", "xhigh", "max"],
        help="override Claude's configured effort",
    )
    parser.add_argument("--access", choices=["none", "read", "edit"], default="read")
    parser.add_argument("--allow-command", action="append", default=[], metavar="RULE")
    parser.add_argument(
        "--permission-mode",
        choices=["manual", "auto", "dontAsk", "acceptEdits", "plan"],
    )
    parser.add_argument(
        "--workflow",
        action="store_true",
        help="enable workflows with per-call approval on stdin",
    )
    parser.add_argument(
        "--timeout",
        type=positive_seconds,
        default=900,
        help="execution seconds, excluding approval waits",
    )
    parser.add_argument("--approval-timeout", type=positive_seconds, default=3600)
    args = parser.parse_args()
    if args.access == "none" and args.allow_command:
        parser.error("--allow-command requires read or edit access")
    if any(not rule.strip() for rule in args.allow_command):
        parser.error("command rules must not be empty")
    if args.workflow and args.prompt_file == "-":
        parser.error(
            "--workflow requires --prompt-file; stdin carries approval decisions"
        )
    if args.workflow and args.permission_mode == "dontAsk":
        parser.error("dontAsk cannot handle workflow approvals")
    return args


def emit_error(base, status, error):
    print(
        json.dumps(
            {**base, "type": "result", "status": status, "error": error},
            ensure_ascii=False,
        ),
        flush=True,
    )
    return 2


def prepare(args):
    cwd = args.cwd.expanduser().resolve()
    base = {
        "session_id": args.resume or str(uuid.uuid4()),
        "cwd": str(cwd),
        "requested_model": args.model,
        "effort": args.effort,
    }
    if not cwd.is_dir():
        raise ValueError("project directory does not exist")
    if args.prompt_file == "-":
        if sys.stdin.isatty():
            raise ValueError("provide a brief file or stdin")
        prompt = sys.stdin.read()
    else:
        prompt = Path(args.prompt_file).expanduser().read_text(encoding="utf-8")
    if not prompt.strip():
        raise ValueError("brief must not be empty")
    executable = shutil.which("claude")
    if not executable:
        raise ValueError("claude was not found in PATH")
    config = (
        Path(os.environ.get("CLAUDE_CONFIG_DIR", str(Path.home() / ".claude")))
        .expanduser()
        .resolve()
    )
    history = config / "projects"
    try:
        history.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryFile(dir=history):
            pass
    except OSError as exc:
        raise PermissionError("Claude history needs write access: " + str(exc)) from exc
    runtime = SCRIPTS.parent / ".venv" / "bin" / "python"
    return {
        **vars(args),
        "cwd": str(cwd),
        "base": base,
        "prompt": prompt,
        "cli_path": executable,
        "claude_env": {"CLAUDE_CONFIG_DIR": str(config)}
        if "CLAUDE_CONFIG_DIR" in os.environ
        else {},
        "python": str(runtime) if runtime.is_file() else sys.executable,
    }


def launch(job):
    lease_read, lease_write = os.pipe()
    job_read, job_write = os.pipe()
    closed = False

    def release(signum=None, frame=None):
        nonlocal closed
        if not closed:
            closed = True
            os.close(lease_write)

    handlers = {}
    process = None
    try:
        process = subprocess.Popen(
            [
                sys.executable,
                str(SCRIPTS / "_supervisor.py"),
                str(lease_read),
                str(job_read),
            ],
            pass_fds=(lease_read, job_read),
            start_new_session=True,
        )
        for signum in (signal.SIGTERM, signal.SIGINT, signal.SIGHUP):
            handlers[signum] = signal.signal(signum, release)
        os.close(lease_read)
        os.close(job_read)
        lease_read = job_read = None
        with os.fdopen(job_write, "w", encoding="utf-8") as request:
            job_write = None
            json.dump(job, request, ensure_ascii=False)
        return process.wait()
    finally:
        release()
        for fd in (lease_read, job_read, job_write):
            if fd is not None:
                os.close(fd)
        for signum, handler in handlers.items():
            signal.signal(signum, handler)
        if process is not None and process.poll() is None:
            process.wait()


def main():
    if sys.version_info < (3, 11):
        return emit_error({}, "unavailable", "Python 3.11 or newer is required")
    args = parse_args()
    try:
        job = prepare(args)
    except PermissionError as exc:
        return emit_error({}, "history_unwritable", str(exc))
    except (ValueError, OSError, UnicodeError) as exc:
        return emit_error({}, "invalid_input", str(exc))
    try:
        return launch(job)
    except (OSError, ValueError) as exc:
        return emit_error(job["base"], "failed", str(exc))


if __name__ == "__main__":
    sys.exit(main())

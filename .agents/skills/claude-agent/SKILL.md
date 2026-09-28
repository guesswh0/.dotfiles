---
name: claude-agent
description: Delegate a task to Claude Code, get a second opinion, continue a Claude session, or run a dynamic workflow with approval and progress reporting through the local SDK adapter.
---

# Claude Agent

Run [scripts/claude_task.py](scripts/claude_task.py).

## Run a task

Use the current project's directory unless the task names another directory or worktree. Give Claude the task, relevant context from this chat, allowed changes, and expected result. Claude loads its native project and global `CLAUDE.md` files, including symlink targets; leave those files for Claude to discover.

Write a UTF-8 brief in the task's work directory, then invoke the adapter:

```sh
python3 /absolute/path/to/claude-agent/scripts/claude_task.py \
  --cwd /absolute/path/to/project \
  --access read \
  --prompt-file /absolute/path/to/work/claude-task.txt
```

`--model` and `--effort` are independent optional overrides. Omitted values use Claude Code's native defaults.

`--access none`, `read`, and `edit` select built-in tools; shell access uses repeatable `--allow-command` rules such as `--allow-command 'git diff *'`. These profiles are not a filesystem sandbox: native hooks, connectors, and permission rules remain active. Claude's configured permission mode is used unless `--permission-mode` is supplied.

For a dynamic workflow, read [references/workflows.md](references/workflows.md) before starting. This branch adds an approval channel and keeps the process open while the user decides.

## Read the result or continue

Output is newline-delimited JSON. Read until the single final `type: result` event; earlier events are not the answer. Only `status: completed` means success. Verify the returned work against the task, relevant diff, or tests.

Keep `session_id`, `cwd`, any explicit model/effort overrides, and a brief task summary in this chat and any context handoff. Continue with the same directory and `--resume SESSION_ID`; calls to one session must be sequential. Separate sessions can handle independent tasks. The final `models` field reports the actual models used.

`needs_permission` reports an unresolved tool request; `denied` reports a declined workflow. For cancellation, timeout, or an ambiguous failure, inspect project changes before resuming. A returned ID on a failed call does not prove the history was saved.

## Runtime

The adapter requires Python 3.11+ and the installed Claude CLI. It automatically uses this skill's `.venv`. If the runtime is missing, run [scripts/install_runtime.py](scripts/install_runtime.py) once. Dependencies are pinned in `scripts/requirements.txt`; invocation itself never installs packages.

Claude needs write access to its own history directory. The preflight checks this before contacting the model. If the host sandbox blocks that write, use the host's normal permission mechanism for the invocation. Claude's selected tool access stays unchanged.

`--timeout` defaults to 900 execution seconds. Approval waits are excluded. The process supervisor stops the SDK worker and its process group on timeout, cancellation, or loss of the calling process. It runs only for the duration of this invocation.

---
name: breakdown
description: Break a plan or the current conversation into TASKS.md backlog entries - tracer-bullet tasks with blocking edges. For repos without an issue tracker.
disable-model-invocation: true
---

# Breakdown

Break a plan, or the current conversation (typically a finished grilling session), into tasks in `TASKS.md` at the repo root.
Synthesize what has already been discussed - do not re-interview the user.
If the user passes a reference (a doc path, a topic) as an argument, read it fully first.

## Rules for tasks

- Each task is a vertical slice: a narrow but COMPLETE path through every layer, demoable or verifiable on its own.
- Sized to fit a single fresh agent session.
- Blocking edges are explicit - the tasks that must complete before this one can start.
- The title plus acceptance criteria must be enough for a cold session to pick the task up without archaeology.
- Use the project's glossary vocabulary (`CONTEXT.md`) and respect ADRs.
- No file paths or code snippets in task text - they go stale fast.

## Process

1. Draft the slices and present them as a numbered list: title, blocked by, what it delivers.
   Ask whether the granularity and the blocking edges are right (via the structured question tool, e.g. `AskUserQuestion`, if available).
   Iterate until the user approves.
2. Create or update `TASKS.md`. Use the format in [TASKS-FORMAT.md](./TASKS-FORMAT.md).
3. Write a spec only if needed: if the conversation settled decisions that neither fit a backlog line nor landed in ADRs, save them to `docs/specs/YYYY-MM-DD-<slug>.md` and reference it in the section header.
   Otherwise skip it - a task's contour is defined when it is picked up, in that session.

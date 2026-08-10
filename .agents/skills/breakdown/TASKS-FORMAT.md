# TASKS.md Format

`TASKS.md` lives at the repo root, one section per feature.

## Template

```markdown
# TASKS

## Feature: <slug>

- [ ] T01 - <title>: <end-to-end behaviour this task makes work>
      Blocked by: none
      - [ ] acceptance criterion 1
      - [ ] acceptance criterion 2
- [ ] T02 - <title> (blocked by: T01)
```

If a spec exists for the feature, reference it in the section header: `## Feature: <slug> (spec: docs/specs/YYYY-MM-DD-<slug>.md)`.

## Conventions for working the file

- Work the **frontier**: any task whose blockers are all done.
- Tick criteria and the task checkbox as work completes.
- Strike through completed tasks with the completion date instead of deleting them; git holds the history.

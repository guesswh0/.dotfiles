# Dynamic workflows

Add `--workflow` and use a brief that explicitly asks Claude to use a dynamic workflow. Keep the host process's stdin open: in Codex, launch `exec_command` with `tty: true`, then retain its process handle. `--prompt-file` is required because stdin carries decisions.

```sh
python3 /absolute/path/to/claude-agent/scripts/claude_task.py \
  --cwd /absolute/path/to/project \
  --access read --workflow \
  --prompt-file /absolute/path/to/work/workflow-task.txt
```

The adapter loads Claude's normal configuration, including its `ask` and `deny` rules. A per-invocation hook routes Workflow calls to the SDK permission callback; it never grants permission or changes saved settings. An explicit `dontAsk` override is incompatible with workflow approval.

## Approval exchange

On `type: approval_required`, inspect `tool_input.script` and the remaining tool input, then present its actual pipeline for the user's decision. The event also contains `request_id` and `input_sha256`. The pending Claude tool call is suspended; no workflow agents have launched from it yet.

After the user's answer, send one JSON line to the same process with `write_stdin`:

```json
{"type":"approval","request_id":"ID_FROM_EVENT","input_sha256":"HASH_FROM_EVENT","decision":"approve"}
```

Use `"decision":"deny"` for refusal. Include a trailing newline. The request ID and hash must match that pending event exactly. A mismatch produces `control_error` and leaves the call waiting. The matching decision applies only once, to the complete reviewed tool input. A saved script is read before approval and passed inline afterward, so an on-disk edit cannot replace the reviewed script.

A later Workflow call produces a new request. There is no pre-approved or always-allow option. The adapter's protocol describes how to transmit a decision; the user's workflow rules remain in their own instructions.

Keep the process handle, pending request ID, hash, and pipeline in the current chat or context handoff. Approval state exists only in the running process. Closing stdin returns `denied`; an expired approval wait returns `timed_out`. Either event, or an explicit refusal, closes approvals for this invocation, including requests already waiting for review. Later requests are denied immediately with the original reason. `--approval-timeout` defaults to 3600 seconds and can be changed separately from the execution timeout.

## Completion and interruption

After `approval_accepted`, expect `workflow_started`, periodic `progress`, and `workflow_finished`. Continue reading until `type: result`; a workflow completion event alone does not include the coordinator's final synthesis.

A plain answer without an observed workflow is `workflow_not_started`. A failed, unfinished, or unsynthesized workflow is `incomplete`. No automatic retry is performed by the adapter.

Use the host's normal process interruption to cancel. If the calling process disappears, the supervisor stops the SDK worker and its process group. To continue after interruption, inspect any changes and use Claude's saved session ID; the adapter has no task registry to recover pending approval requests.

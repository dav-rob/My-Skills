---
name: cli-cursor
description: Run Cursor Agent CLI tasks from another AI or script, discover model parameters and efforts, and return reliable completion, authentication and usage-limit feedback.
---

# Cursor Agent CLI

Use `cursor-agent` (also distributed as `agent`), not the `cursor` editor launcher.
Resolve the binary, read `--version` and `--help`, then run `cursor-agent status`
and `cursor-agent models` or `cursor-agent --list-models`. The tested version was
2026.10.01-e373342 on 2026-10-08. Authentication failure is a caller-visible
`auth_required` result, not an empty model list. Don't start an unattended login.

## Models and effort

Choose a returned model ID, not its display label. The installed help supports
quoted parameter overrides inside `--model`, for example
`'claude-opus-4-8[context=1m,effort=high,fast=false]'`. This is syntax, not a claim
that the example model is available to this account. There is no standalone
`--effort` flag in this build. Older catalogs may expose effort as part of a model
ID; use the exact offered ID in that case.

Use the model listing and picker to discover available variants. For automation
needing an explicit parameter catalog, Cursor's official SDK `Cursor.models.list()`
exposes model IDs, `parameters[].values` and `variants[].params`; use it only if
that SDK is available and authenticated. See the [SDK documentation](https://cursor.com/docs/sdk/typescript).
Validate the requested effort against that model's returned parameter choices.
If discovery isn't available, report that constraint rather than inventing
support. Do not mechanically turn a Codex label into a Cursor ID. Preserve the
user's exact model/effort; report unsupported pairs instead of changing them.

## Invocation

```sh
cursor-agent --print --workspace "$workdir" --model "$model_spec" \
  --output-format stream-json --force "$prompt" </dev/null
```

`--force` (alias `--yolo`) allows unattended commands unless explicitly denied.
Use it when that execution scope is authorized. For questions/reviews use
`--mode ask` or `--mode plan`; `--sandbox enabled` is separately available.
`--trust` trusts a workspace without a dialog; add it only for a workspace already
trusted by the user. `--approve-mcps` is separate and not needed for every task.
Use `--resume "$session_id"` for a specific follow-up after checking current help.

Pass argument arrays from programs and close stdin when no input is intended.
Capture stdout and stderr separately, give the process a deadline, and terminate
and reap owned children on timeout. Never discard stderr or merge it into JSON.

## Completion and limits

Parse stream-json as NDJSON and require exit code 0 plus a terminal
`type: "result"`, `subtype: "success"`, `is_error: false` result. Read its `result`
text and `session_id`; `system/init` may describe the actual model. If using
`--output-format json`, expect one success object. Failures can produce no JSON,
a nonzero exit, and only stderr. Missing terminal results are `incomplete`.

For a final answer, read only the terminal result. If displaying incremental
text, see [the output protocol](https://cursor.com/docs/cli/reference/output-format)
before enabling `--stream-partial-output`, because some assistant flushes repeat
text already emitted. Don't count duplicate text as extra work or usage.

Return `status`, `exit_code`, `model`, requested `effort`, `session_id`, `answer`,
`usage` when actually supplied, and error details to the invoking process. Include
`timed_out` and retry timing when applicable. Do not fabricate token totals or
remaining quota: this CLI's basic result contract doesn't guarantee those fields.

Classify explicit authentication, unsupported-model, rate-limit/429, credit/quota,
context-length, and transport errors using the actual error payload/stderr.
Quota exhaustion and a context limit require different recovery; ambiguous errors
remain `unknown_error`. The account's usage page can clarify allowance; token
counts alone don't establish it. Don't deliberately burn tokens to test limits.
Bound any retry and inspect partial edits before repeating a mutating task.

## Sources and verified scope

[Official parameters](https://cursor.com/docs/cli/reference/parameters),
[output protocol](https://cursor.com/docs/cli/reference/output-format), and
[configuration](https://cursor.com/docs/cli/reference/configuration).
Local help, version, model-list failure and headless auth failure were verified.
This machine reported authentication required, so successful inference and this
account's model/effort catalog remain unverified until login.

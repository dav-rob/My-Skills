---
name: cli-antigravity
description: Run Google Antigravity CLI (agy) from another AI or script, discover available model and effort combinations, and return structured completion, quota and error feedback.
---

# Antigravity CLI

Use `agy`, not an editor launcher or `gemini`. Inspect `command -v agy`,
`agy --version`, `agy --help`, `agy models`, and `agy agents` as needed.
The latest tested binary was 1.3.3 on 2026-10-12. Inference uses cached authentication;
report an auth error to the caller instead of opening an unattended login flow.

## Model and effort

`agy models` returns model slugs and display names. Many slugs already include
the effort, for example `gemini-3.8-flash-high`. Choose an offered combination,
then use `--model "$model_slug"`; `--effort "$effort"` can also express the
requested effort. Don't combine contradictory suffix/effort values. Verify the
pair with a small non-mutating headless request when exact support is uncertain.

The installed parser advertises `low`, `medium`, `high`, `xhigh`, `max`, while
the fetched catalog here offered low/medium/high variants (some families only
low/high). Parser acceptance is not model support. Do not infer GPT-6.1 Sol
availability from a Codex/Cursor catalog or invent model variants. Reject or
report unsupported pairs rather than silently falling back. Report the selected
slug and effort separately to the caller.

## Headless invocation

```sh
agy --print "$prompt" --model "$model_slug" --effort "$effort" \
  --output-format json --print-timeout 10m --dangerously-skip-permissions </dev/null
```

Run in the intended working directory. The bypass flag supports authorized YOLO
work and approves all tools, including writes and commands. `--mode plan` adds
planning instructions; don't treat it as an enforced read-only boundary.
`--sandbox` restricts terminal execution and does not grant browser/tool approval.
Use permissions appropriate to the authorized task; don't silently widen global
allow rules to fix a headless denial. Successful inference alone doesn't establish
authenticated browser, Keychain or locked-screen GUI access.

For progress, use `--output-format stream-json`. To send prompts over stdin,
also set `--input-format stream-json`, omit `--print`, and serialize one NDJSON
message per turn with a JSON encoder:

```json
{"event":"user","message":{"content":"Reply with exactly: CLI_SMOKE_OK"}}
```

For one turn, write the message plus a newline and close stdin; the CLI finishes
that turn before exiting. For multiple turns, consume the current `result` before
sending the next message. Drain stdout and stderr while running; permission
notices can appear on stderr even when a response succeeds.

Set `--print-timeout` explicitly: this installed help reports default `0s`
(unbounded), despite documentation describing five minutes. Also enforce an
external deadline and reap owned children on cancellation. Pass arguments as an
array, not interpolated shell code. Close stdin unless intentionally maintaining
a streaming session.

Save `conversation_id` durably as soon as it appears on an `init` event, in
`step_update.conversation_id`, or in the terminal `result`, together with the working
directory, selected model/effort and active CLI profile. Retain it on timeout,
cancellation or parser failure; missing later metadata must not erase it.
Resume that exact ID with `--conversation`, after inspecting partial work.
Read [follow-up.md](references/follow-up.md) for web access or schema-based resume.

## Feedback and limits

For JSON require exit 0 and `status: "SUCCESS"`. Extract `response`,
`conversation_id`, `usage` and any `error`. Other statuses, missing/malformed
JSON, cancellation and deadline expiry are failures or incomplete runs.
For stream-json the terminal envelope is `event: "result"` with the result under
`result`; this differs from Claude/Cursor's `type: "result"`. Intermediate
`step_update` events are progress only. Also inspect `denied_actions` and stderr:
1.3.3 returned exit 0 and `SUCCESS` with an empty response when required web reads
were denied. Preserve the provider outcome separately and report the task as
blocked/incomplete when a required action was denied. Assess unrelated denials
against the requested outcome rather than failing every warning automatically.

Return `status`, `exit_code`, `model`, `effort`, `session_id` (conversation ID),
`usage`, `answer`, `error`, and retry/reset timing when reported. In a continued
session counters may be cumulative; don't sum cumulative results or double-count
thinking tokens included in output. Missing counters are unknown, not zero.

Read allowance with a separate `agy --print /usage` invocation when supported.
It is a CLI text report, not a normal model JSON result. Don't send CLI-handled
slash commands in `--input-format stream-json`. Treat token usage and remaining
model quota/credits separately. Classify explicit quota/resource-exhausted,
rate-limit, context/output limit, invalid-model/effort, authentication, and
network errors; preserve unknown errors rather than diagnosing every failure as
“out of tokens”. Honor reset/backoff and bound retries. Inspect partial edits
before another attempt; don't induce exhaustion, spend credits or switch accounts
to test recovery.

## Sources and verified scope

[Official headless guide](https://antigravity.google/docs/cli/headless/)
and [CLI reference](https://antigravity.google/docs/cli/reference).
Verified model listing, a `gemini-3.8-flash-high`/`high` JSON success, and invalid
effort returning exit 1 plus `status: "ERROR"`. Streaming success, `/usage`, and
a contradictory model/effort pair failing before inference were also verified.
On 1.3.3, stdin streaming, exact-ID resume in a fresh process, denied web actions,
authorized public web reads, and temporary/persistent web follow-up were verified.
See the follow-up reference for the limited structured-output observation.
Actual exhaustion and locked-screen GUI operation weren't verified.

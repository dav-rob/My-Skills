---
name: cli-antigravity
description: Run Google Antigravity CLI (agy) from another AI or script, discover available model and effort combinations, and return structured completion, quota and error feedback.
---

# Antigravity CLI

Use `agy`, not an editor launcher or `gemini`. Inspect `command -v agy`,
`agy --version`, `agy --help`, `agy models`, and `agy agents` as needed.
The tested binary was 1.3.1 on 2026-10-08. Inference uses cached authentication;
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
work. `--mode plan` and `--sandbox` are available for narrower tasks. For progress,
use `--output-format stream-json`. Capture stdout and stderr separately; notices
about denied tools can appear on stderr even when a response succeeds.

Set `--print-timeout` explicitly: this installed help reports default `0s`
(unbounded), despite documentation describing five minutes. Also enforce an
external deadline and reap owned children on cancellation. Pass arguments as an
array, not interpolated shell code. Close stdin unless intentionally maintaining
a streaming session. Resume the exact `conversation_id` with `--conversation`.

## Feedback and limits

For JSON require exit 0 and `status: "SUCCESS"`. Extract `response`,
`conversation_id`, `usage` and any `error`. Other statuses, missing/malformed
JSON, cancellation and deadline expiry are failures or incomplete runs.
For stream-json the terminal envelope is `event: "result"` with the result under
`result`; this differs from Claude/Cursor's `type: "result"`. Intermediate
`step_update` events are progress only. Check outcome and denied-tool notices
before declaring the requested task complete.

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
Actual exhaustion wasn't induced.

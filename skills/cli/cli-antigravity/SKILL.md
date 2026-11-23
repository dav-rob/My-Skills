---
name: cli-antigravity
description: Run Google Antigravity CLI (agy) from another AI or script, discover available model and effort combinations, and return structured completion, quota and error feedback.
---

# Antigravity CLI

Use `agy`, not an editor launcher or `gemini`. Inspect `command -v agy`,
`agy --version`, `agy --help`, `agy models`, and `agy agents` as needed.
Most behaviour below was verified on 1.3.3 (2026-10-12). The stream-json protocol, model
listing, exit statuses and `--json-schema` behaviour were re-checked on 1.4.0 on 2026-10-16.
The CLI updates itself between runs, so record `agy --version` with every run and re-verify
after a change. Inference uses cached authentication; report an auth error to the caller
instead of opening an unattended login flow.
On 2026-11-23, 1.5.11 help and published release notes were checked; `agy models`
required sign-in, so current catalog and inference checks were blocked. The newer
behaviors identified below are release-reported, not newly exercised live.

## Model and effort

`agy models` returns model slugs and display names. Many slugs already include
the effort, for example `gemini-3.8-flash-high`. Choose an offered combination,
then use `--model "$model_slug"`; `--effort "$effort"` can also express the
requested effort. Don't combine contradictory suffix/effort values: the CLI rejects
that itself, with exit 1 and an `ERROR` envelope before any inference (re-checked on
1.4.0). From 1.3.4 the changelog says `--model` also accepts a base model name without
`--effort` and picks that model's default thinking level; report that effort as unknown
unless the result states it. Verify the pair with a small non-mutating headless request
when exact support is uncertain.

The installed parser advertises `low`, `medium`, `high`, `xhigh`, `max`, while
the 1.4.0 catalog offered low/medium/high variants (some families only low/high).
Newer catalogs can offer more: the 1.5.8 release notes add Hydrogen through xhigh
for specified authentication routes. Discover the active route rather than
assuming either catalog applies. Parser acceptance is not model support. Do not infer GPT-6.1 Sol
availability from a Codex/Cursor catalog or invent model variants. Reject or
report unsupported pairs rather than silently falling back. Report the selected
slug and effort separately to the caller.

## Headless invocation

```sh
agy --print "$prompt" --model "$model_slug" --effort "$effort" \
  --output-format json --print-timeout 10m --dangerously-skip-permissions </dev/null
```

Run in the intended working directory. The bypass flag supports authorized YOLO
work and approves all tools, including writes and commands. `--mode` offers `plan`,
`accept-edits` and (from 1.3.5, per the changelog) `auto`, which approves edits and safe
commands but reviews commands that would leave the sandbox; `auto` was not tested
headless. `--mode plan` adds planning instructions; don't treat it as an enforced
read-only boundary.
The 1.5.7 release notes make Auto the default where available, including headless
runs without a saved mode. Select the mode explicitly when its behavior matters.
`--sandbox` restricts terminal execution and does not grant browser/tool approval.
Use permissions appropriate to the authorized task; don't silently widen global
allow rules to fix a headless denial. Successful inference alone doesn't establish
authenticated browser, Keychain or locked-screen GUI access.
Explicit deny rules and enterprise requirements for human review can still block
actions under the bypass flag (1.5.2); it is not authority to override them.

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
Read [follow-up.md](references/follow-up.md) for web access or schema-based resume, and
[structured-output.md](references/structured-output.md) before passing `--json-schema` or
relying on `structured_output`: a schema Gemini rejects fails every run.

## Feedback and limits

For JSON require exit 0 and `status: "SUCCESS"`. Extract `response`,
`conversation_id`, `usage`, `finished_reason` and any `error`. From 1.4.11,
`finished_reason` identifies an early stop: `print_timeout`, `interrupted`, or
`error`; it is omitted on normal completion. An early-stop reason makes a partial
answer timed out, interrupted or failed even if another field looks successful.
Preserve unknown reasons as incomplete rather than assuming success.
Other statuses, missing/malformed
JSON, cancellation and deadline expiry are failures or incomplete runs.
For stream-json the terminal envelope is `event: "result"` with the result under
`result`; this differs from Claude/Cursor's `type: "result"`. Intermediate
`step_update` events are progress only. Also inspect `denied_actions` and stderr:
1.3.3 returned exit 0 and `SUCCESS` with an empty response when required web reads
were denied. Preserve the provider outcome separately and report the task as
blocked/incomplete when a required action was denied. Assess unrelated denials
against the requested outcome rather than failing every warning automatically.

Exit statuses seen on 1.4.0: 0 success; 1 a rejection by the CLI before any request
(invalid or contradictory model/effort, unknown `--agent`); 2 a print-mode usage error
such as `--print` with `--prompt-interactive`; 3 a provider request error returned with
an `ERROR` envelope (for example an invalid schema). Read the envelope, not the code alone.
The changelog (`agy changelog`, checked 2026-11-23) adds that 1.3.3 reports an
individual quota limit at once and words an expired sign-in as `Authentication expired.
Please log back in.`, that 1.3.6 cancels and retries a model request that stalls for five
minutes (so a run can take longer without failing), and that headless `-p` runs skip
subagent questions.
The published 1.5.0 notes report exit 3 plus an `AGY_ERROR` line and stderr
diagnostic when `--print-timeout` terminates background tasks; without an explicit
timeout print mode waits for that work. Exit 3 alone therefore does not establish
a provider error. In 1.5.5, shutdown after printing a result is bounded to 30
seconds; retain the external deadline and require process exit as well as a result.

Return `status`, `exit_code`, `model`, `effort`, `session_id` (conversation ID),
`usage`, `answer`, `error`, `finished_reason`, and retry/reset timing when reported. In a continued
session counters may be cumulative; don't sum cumulative results or double-count
thinking tokens included in output. Missing counters are unknown, not zero.

Read allowance with a separate `agy --print /usage` invocation when supported.
It is a CLI text report, not a normal model JSON result. Don't send CLI-handled
slash commands in `--input-format stream-json`. Treat token usage and remaining
model quota/credits separately. Classify explicit quota/resource-exhausted,
rate-limit, context/output limit, invalid-model/effort, invalid request or schema
(`INVALID_ARGUMENT`, code 400: no retry helps until the request changes), authentication,
and network errors; preserve unknown errors rather than diagnosing every failure as
“out of tokens”. Honor reset/backoff and bound retries. Inspect partial edits
before another attempt; don't induce exhaustion, spend credits or switch accounts
to test recovery.

## Sources and verified scope

[Official headless guide](https://antigravity.google/docs/cli/headless/)
and [CLI reference](https://antigravity.google/docs/cli/reference).
Release-reported updates checked 2026-11-23: [1.4.11, 30 October](https://antigravity.google/docs/changelog/#rel-cli-1.4.11),
[1.5.0, 4 November](https://antigravity.google/docs/changelog/#rel-cli-1.5.0),
[1.5.2, 6 November](https://antigravity.google/docs/changelog/#rel-cli-1.5.2),
[1.5.5, 10 November](https://antigravity.google/docs/changelog/#rel-cli-1.5.5),
[1.5.7, 12 November](https://antigravity.google/docs/changelog/#rel-cli-1.5.7),
and [1.5.8, 13 November 2026](https://antigravity.google/docs/changelog/#rel-cli-1.5.8).
Verified model listing, a `gemini-3.8-flash-high`/`high` JSON success, and invalid
effort returning exit 1 plus `status: "ERROR"`. Streaming success, `/usage`, and
a contradictory model/effort pair failing before inference were also verified.
On 1.3.3, stdin streaming, exact-ID resume in a fresh process, denied web actions,
authorized public web reads, and temporary/persistent web follow-up were verified.
See the follow-up reference for the limited structured-output observation.
On 1.4.0 (2026-10-16), model listing, stdin streaming with `--json-schema` through a real
eight-minute research run, the exit statuses above and the schema behaviour in the
structured-output reference were verified. `/usage`, exact-ID resume, denied-action
handling and remote control were not re-checked on 1.4.0.
Actual exhaustion and locked-screen GUI operation weren't verified.

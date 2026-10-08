---
name: cli-opencode
description: Invoke OpenCode CLI from another AI or script, resolve provider/model and reasoning variants, and report completion, usage, provider errors and timeouts to the caller.
---

# OpenCode CLI

Inspect `command -v opencode`, `opencode --version`, `opencode run --help`,
`opencode models --help`, and `opencode providers list` (older releases use
`opencode auth list`). Avoid logging credentials. The tested binary was 1.18.35
on 2026-10-08. Use headless `run`, not the default TUI, for process invocation.

## Models and reasoning variants

Run `opencode models` or `opencode models "$provider" --verbose`. Invocation
uses `provider/model`, not a display name. A listing is configuration discovery,
not proof that the remote service or account is currently usable.

Effort is `--variant "$variant"`; there is no common effort vocabulary across
providers. For an exact list, use an existing local OpenCode server's
`GET /config/providers`, or start a temporary `opencode serve` bound explicitly
to `127.0.0.1`, query it, then stop/reap it. See
[the server API](https://opencode.ai/docs/server/). Use the configured server's
authentication if required; don't log credentials or full configuration.

Find the matching provider's `models[model_id]`, inspect `capabilities.reasoning`
and keys of `variants`, and choose a returned variant. Empty variants do not mean
every effort is supported. Local model backends may have no reasoning variants.
Provider config can override variants; consult the effective catalog rather than
assuming the general model database is exact. Treat unsupported requested pairs
as caller-visible errors, not a reason to silently substitute a model.

For example, GPT-6.1 Sol High would require an actually configured GPT-6.1 Sol
provider/model and a `high` variant. This machine had no `openai` provider during
verification. Do not claim that Codex account access configures OpenCode access.

## Run

```sh
opencode run --dir "$workdir" --model "$provider_model" \
  --variant "$variant" --format json --auto "$prompt" </dev/null
```

Omit `--variant` if the selected model has none. `--auto` auto-approves permissions
that aren't explicitly denied and supports authorized YOLO work. `--agent plan`
is available for analysis; inspect agent behavior rather than treating its name
as a filesystem sandbox. `--pure` excludes external plugins when the task doesn't
need them. Follow up using the captured session ID with `--session`; don't use
`--continue` if it could pick somebody else's work.

Pass argument arrays, close unused stdin, capture stdout/stderr independently,
and impose a deadline. A free model can wait in a queue, and a local backend can
be unavailable. Emit progress without claiming success, then terminate/reap the
owned process group on timeout. A silent process does not prove quota exhaustion.

## Result and error feedback

`--format json` emits JSONL events, not a single answer object. Collect `text`
parts, `sessionID`, and `step_finish.part` usage (`tokens`, `cost`, `reason`) where
present. Multiple steps can include tools: `tool-calls` is not final completion.
Require exit 0, no terminal `error`, and evidence of the final completed response
(normally a finishing step with reason `stop`); validate the requested outcome.
A start event, partial text, or missing final step is `incomplete`.

On failure retain the `error.name` and `error.data` payload. The tested invalid
provider returned exit 1 and a generic `UnknownError`; keep it unknown unless
provider logs establish a more specific cause. Provider `APIError` data can expose
status, response body, retryability and headers. Handle explicit 429/rate limits,
quota/credit exhaustion, authentication, model rejection, context/output limits,
transport errors, and timeout separately. Never fabricate remaining tokens from
`opencode stats`; stats describes usage, not account entitlement.

Return `status`, `exit_code`, `model`, `effort` (variant), `session_id`, `answer`,
reported `usage`, `error`, and retry timing to the invoking process. Unknown
usage stays unknown; don't estimate tokens from changed lines. Keep provider
diagnostics private and redact credentials. Bound retries and inspect partial
edits; respect backoff/reset and don't force token exhaustion to test detection.

## Sources and verified scope

[Official CLI](https://opencode.ai/docs/cli/), [models](https://opencode.ai/docs/models/)
and [server API](https://opencode.ai/docs/server/).
Verified installed help, model listing, effective variant catalog from the local
server, and structured invalid-provider failure. The default smoke request emitted
`step_start` but exceeded 55 seconds, so its inference success was not established.
A separately pinned local-model request also exceeded its 25-second deadline.

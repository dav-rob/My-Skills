# Programmatic model discovery

The CLI's stream-json control protocol backs the official Agent SDK. Prefer that
SDK's `get_server_info()` when it is already installed. Its initialization response
includes `models`. Direct protocol access was checked against Claude 2.1.294;
feature-detect response fields because this interface can change.

For a read-only probe, start this command in a temporary directory, with piped
stdin/stdout, separately drained stderr and an external discovery deadline:

```sh
claude --safe-mode --print --input-format stream-json \
  --output-format stream-json --verbose --tools "" --no-session-persistence
```

Send one newline-terminated request (this is not JSON-RPC):

```json
{"type":"control_request","request_id":"models","request":{"subtype":"initialize"}}
```

Wait for `type: "control_response"` matching `response.request_id == "models"`.
Check `response.subtype` for failure, then read `response.response.models`.
For each model retain only `value`, `resolvedModel`, `displayName`,
`supportsEffort`, and `supportedEffortLevels`. Do not dump the full initialization
payload, which may contain account details. An empty/missing capability list is
unknown, not support for all effort levels.

This probe sends no user prompt, runs no inference and changes no model setting.
After the response, terminate and reap the child. If direct invocation is blocked
inside a nested Claude session, report the restriction or use an authorized
external caller; do not unset the nesting guard just to bypass it.

`--safe-mode` deliberately excludes customizations. When provider mapping or
managed settings matter, compare discovery in the actual authorized environment
and the `/model` picker; don't claim the probe validated an unavailable provider.

On 2026-10-08, aliases `opus`, `sonnet`, `haiku`, `fable` resolved to Opus 5.5,
Sonnet 5.5, Haiku 5.5, Fable 5.1. All four returned five effort levels, `low` through
`max`. Authentication failure still prevented the subsequent inference smoke test.

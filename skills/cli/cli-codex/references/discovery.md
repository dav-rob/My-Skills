# Model and quota discovery

Start the installed `codex app-server --stdio` as a child with piped stdin/stdout
and separately drained stderr. Set a short discovery deadline. This is JSON-RPC
over newline-delimited JSON; match response IDs and ignore unrelated notifications.

Send initialization, then wait for response ID 1 before sending subsequent messages:

```json
{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"clientInfo":{"name":"cli-caller","version":"1.0"},"capabilities":{"experimentalApi":true}}}
```

```json
{"jsonrpc":"2.0","method":"initialized","params":{}}
{"jsonrpc":"2.0","id":2,"method":"model/list","params":{"includeHidden":false}}
{"jsonrpc":"2.0","id":3,"method":"account/rateLimits/read","params":{}}
```

ID 2 returns `result.data`: `model` is the invocation ID; `displayName` is a label;
`supportedReasoningEfforts[].reasoningEffort` contains allowable effort strings;
`defaultReasoningEffort` supplies the model default. If `nextCursor` is non-null,
repeat `model/list` with `cursor` and a new request ID until all pages are read.

ID 3 returns account-wide usage. Prefer `rateLimitsByLimitId` when present; retain
each bucket rather than collapsing unrelated limits. `primary` and `secondary`
may contain `usedPercent`, `windowDurationMins` and Unix-seconds `resetsAt`.
Remaining percent is `max(0, 100-usedPercent)`; null/missing means unavailable.
Also inspect `ordinaryUsageAllowed`, `spendControlReached`, and credit state when
present. Never treat a null bucket as unlimited entitlement. This method is a
read, not a purchase or reset. Filter account IDs and other account details out
of logs and user-facing results.

No conversation or turn needs to be started. After collecting both responses,
close/terminate and reap the discovery process. Protocol errors, authentication
errors and timeouts should produce an explicit unavailable result. Don't leave a
discovery process running or infer supported models from API marketing names.

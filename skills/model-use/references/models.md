# Current workhorses

Assessed: 2026-11-18. These are the user's starting choices, with locally
discovered invocation IDs. They are not a claim that one model wins every coding
benchmark. Recheck discovery when an ID stops working or a recommendation is stale.

| Family / role | Preferred route and exact model | Effort | Route fallback |
| --- | --- | --- | --- |
| Sol worker | `codex`: `gpt-6.1-sol` | `high`; `xhigh` for a justified escalation | Other eligible worker, then manager |
| Sonnet worker | `claude`: `claude-sonnet-5-5` | `high` | `agy`: `claude-sonnet-5-5-high`, effort `high`; then other eligible worker, then manager |
| Hydrogen worker | `agy`: `gemini-4-hydrogen-high` | `high` | Other eligible worker, then manager |
| Weekly assessor | `codex`: `gpt-6.1-sol` | `xhigh` | Preserve the previous table and report a blocked maintenance run |

Stronger escalation candidates exposed locally include `gpt-6.2-astra` via
Codex, `claude-opus-5-5` via Claude and `gemini-4-argon-high` via Antigravity.
Discovery alone does not establish that an alternative is stronger for the task
or available under the current plan; verify before selecting it. Escalation
does not replace the user's interactive manager or add ordinary rotation slots.

## Local evidence

Discovery on 2026-11-18 used Codex 0.168.0, Claude Code 2.1.323 and agy 1.5.11.
Codex's app-server exposed Sol 6.1 with `high` and `xhigh`; Claude initialization
resolved Sonnet to `claude-sonnet-5-5` with `high`; `agy models` exposed both
Sonnet 5.5/high and Hydrogen/high. Availability is machine/account-specific.

All four routes completed bounded live smoke requests on that date: Sol/high via
Codex, Sonnet/high via Claude, Sonnet/high via agy, and Hydrogen/high via agy.
Each returned `MODEL_USE_OK`, exit 0 and its successful terminal event/envelope,
with token usage. They ran in temporary workspaces; no quota was deliberately
exhausted. Effective effort is unknown where the result does not echo it.
A smoke response establishes connectivity and terminal parsing, not competence
at building an application. Do not infer remaining subscription allowance from
token usage or API cost.

Independent instruction-based checks covered rotation, alternate Sonnet routing,
manager identity through another CLI, exhausted workers, interrupted sessions,
missing terminal feedback and an unchanged weekly assessment. Recovery precedence
was clarified and rechecked. These checks did not run an application benchmark
or deliberately trigger a provider limit.

## Assessment sources

Start with [Artificial Analysis coding agents](https://artificialanalysis.ai/agents/coding-agents)
and its [current methodology](https://artificialanalysis.ai/methodology/coding-agents-benchmarking).
The observed index was v2.1: FrontierCode-AA 2.0, Terminal-Bench 4.1 and
SWE-Atlas-QnA-AA. Use implementation/bug-fix evidence first, repository
understanding second, and relevant terminal-workflow results where useful.
Compare completion time and token consumption as efficiency signals.

[FrontierCode](https://cognition.com/frontiercode) evaluates mergeability, including
correctness, tests and codebase fit. Its results depend on the model, effort and
agent harness. Use comparable configurations, dates and benchmark versions;
do not combine overlapping scores into a second invented leaderboard. API cost
is not a subscription allowance. The accessed pages did not expose numerical
model rankings in their text view; no ranking values have been guessed.

Keep the metric categories stable while replacing individual benchmarks when
the evidence warrants it. DeepSWE is excluded at the user's request. Retain the
current choices when evidence is missing or inconclusive, and distinguish a
published result, local test, user experience and a recommendation.

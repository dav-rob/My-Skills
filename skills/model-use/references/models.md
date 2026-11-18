# Current workhorses

Assessed: 2026-11-18. Current choices combine the user's experience, existing
subscriptions and verified CLI access. Published scores and the reasons for
keeping these settings are below; the choices are not a ranking by benchmark
score. Recheck discovery when an ID stops working or a recommendation is stale.

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

## Published scores

Checked 18 November 2026 against the [Artificial Analysis coding-agent board](https://artificialanalysis.ai/agents/coding-agents),
Coding Agent Index v2.1. Scores below are published agent runs, not local test
results. Higher scores are better; compare models within a column, not raw
percentages across columns with different tasks and scoring.

### Coding abilities

| Published model / effort / agent | Implementation: FrontierCode-AA 2.0 | Repository understanding: SWE-Atlas-QnA-AA | Terminal work: Terminal-Bench 4.1 |
| --- | --- | --- | --- |
| Sol 6.1 / max / Codex | 42.5% | 59.9% | 54.0% |
| Sonnet 5.5 / max / Claude Code (default fallback) | 39.1% | 64.2% | 65.7% |
| Hydrogen / xhigh / Antigravity | 36.6% | 60.2% | 60.1% |
| Sol 6.2 / high / Codex (candidate) | 38.3% | 50.5% | 53.5% |
| Sol 6.2 / xhigh / Codex (candidate) | 40.4% | 51.3% | 57.6% |

Daily-setting coverage: the retrieved board has no matching rows for Sol 6.1/high
or xhigh, Sonnet 5.5/high, or Hydrogen/high. The max/xhigh rows above are context,
not scores attributed to our daily settings. No matching Sonnet-through-agy row
was retrieved either. Missing means unknown, not zero. Sonnet's published
"default fallback" configuration can finish some attempts with another model;
it is not a pure Sonnet-only result.

### Efficiency and budget

| Same published configuration | Output tokens / task | Agent time / task | API cost / task (USD) |
| --- | --- | --- | --- |
| Sol 6.1 / max / Codex | 56.6k | 21.9 min | $1.51 |
| Sonnet 5.5 / max / Claude Code (default fallback) | 553.8k | 86.8 min | $11.40 |
| Hydrogen / xhigh / Antigravity | 199.1k | 32.1 min | $4.45 |
| Sol 6.2 / high / Codex (candidate) | 20.0k | 10.6 min | $0.76 |
| Sol 6.2 / xhigh / Codex (candidate) | 26.2k | 12.6 min | $0.90 |

These are averages across the same three-benchmark suite; k means 1,000 tokens.
Agent time is wall time, not time to first token. API cost is an efficiency
signal, not what our subscriptions charge, and token totals do not establish
remaining allowance. Different efforts and CLI versions limit direct comparisons.

Source: [AA board](https://artificialanalysis.ai/agents/coding-agents) and
[methodology](https://artificialanalysis.ai/methodology/coding-agents-benchmarking).
The recorded figures are a dated comparison, not a live quota display or an
automatic ranking of the recommended settings.

## Selection reasons

The current rotation is an intentional budget/experience policy, not an automatic
"highest score wins" decision. All three existing subscriptions get useful work.
We have not assigned made-up weights or estimated tasks per subscription.

| Choice | Why it stays in the rotation | What the metrics do and do not support |
| --- | --- | --- |
| Sol 6.1 / high, xhigh for harder work | The user's established workhorse, a working Codex route, and a way to reserve the interactive manager for coordination. | Its published max run is strongest on implementation among the three family reference runs and uses fewer output tokens; that does not establish the same advantage at high. |
| Sonnet 5.5 / high | The user's trusted app builder; the dashboard implementation also completed with manager review and corrections. Claude and agy offer alternative access routes within one slot. | The published max/fallback run leads these reference runs on repository understanding and terminal work, but consumes substantially more output tokens and time. That does not prove Sonnet high is best, or predict its subscription allowance. |
| Hydrogen / high | The user reports strong practical results and wants regular use of the Gemini subscription. It receives alternating tasks, not just fallback work. | The xhigh reference supplies coding evidence and uses more output tokens than the Sol max run. Different benchmark difficulty prevents treating the columns as ability ratios. High remains a practical starting choice; its exact coding-agent score is unknown here. |
| Sol 6.2 / high or xhigh | A candidate to trial, not an unannounced replacement for the user's Sol 6.1 choice. | The published rows show a promising lower-token/lower-time option, with different scores by ability. Effort differences and lack of a matched local app trial prevent a blanket upgrade conclusion. |

Decision for this assessment: keep the selected settings and round robin. A
credible improvement should be tried on a bounded representative app task with
acceptance checks, correction effort and reported usage. Record when experience,
allowance or integration makes our choice differ from the metrics; do not hide
that disagreement by relabelling a preference as a benchmark result.

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
is not a subscription allowance. The published score snapshot above was recovered from the public coding-agent
page's chart data, rather than its text-only view; unknown configurations remain
unscored.

Keep the metric categories stable while replacing individual benchmarks when
the evidence warrants it. DeepSWE is excluded at the user's request. Retain the
current choices when evidence is missing or inconclusive, and distinguish a
published result, local test, user experience and a recommendation.

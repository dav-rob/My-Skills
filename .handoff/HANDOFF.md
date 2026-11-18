# Handoff — rotation clarity and score evidence, 18 November 2026

## Current objective

Clarify that model-use alternates new tasks and publish scores, efficiency and
selection reasons at the bottom of the dashboard's Current recommendations.

## What was done

Pushed `3407c94`: explicit four-task repeating sequences in the canonical skill;
safe nested-section rendering for Published scores and Selection reasons;
capability/efficiency tables and reasoned choices in references/models.md;
a dated public-data snapshot under docs/model-scores; maintenance and README
updates; regression coverage. `1104439` removed one wording-only test assertion.
No selected model/effort or routing policy was changed.

The public Artificial Analysis coding-agent page embeds benchmarkRows in its
server-rendered chart data. Retrieved that public HTML without executing scripts
or using a private API; text-only browsing had hidden the numbers. Snapshot
`docs/model-scores/2026-11-18.json` retains the source URL/hash/retrieval time,
exact fraction-valued scores, mean telemetry and CLI versions for five runs.
Do not substitute cached search snippets or unavailable comparison pages for
this primary evidence. The dashboard still reads canonical markdown live.

The retrieved board has Sol 6.1/max, Sonnet5.5/max with default fallback, Hydrogen/
xhigh, and candidate Sol6.2/high/xhigh. It lacks matched rows for our daily Sol6.1/
high or xhigh, Sonnet/high, Hydrogen/high, and agy Sonnet. Missing means unknown;
none of the published higher-effort scores is assigned to daily high settings.
Sonnet's default fallback can finish attempts on another model. Compare models
within a benchmark column, not percentages across different benchmark difficulties.
API prices and consumed output tokens are not subscription allowance estimates.

## Current state

The updated page is running at http://127.0.0.1:48173/. The existing user service
was reinstalled/restarted for the renderer changes; localhost-only/read-only
boundaries remain. Browser refresh showed explicit repeat sequences, all score
and efficiency tables and selection reasons inside Current recommendations.
The original choices were kept as user/budget/experience defaults, with Sol6.2
listed as a candidate rather than silently selected.

The existing weekly automation was updated via its tool, retaining the local
project, Monday 09:00, Sol6.1/xhigh and ACTIVE status. It now maintains score
coverage/provenance and reasons, including when budget/experience diverges from
metrics. Its first scheduled run remains unobserved.

Used the installed round robin: saved next=Sonnet before assigning the update to
Hydrogen/high through agy. Captured conversation identity early; the worker
finished with exit 0, SUCCESS and no reported denial. The manager reviewed the
code, evidence and claims. Local state remains excluded from Git.

## Verification

- Full suite: 92 passed before removing a wording-only assertion; final current
  dashboard suite: 42 passed with warnings as errors. The 49 existing regression
  tests were unchanged. No runtime change followed the full suite.
- New coverage checks score/reason placement/order, nested headings, labelled
  tables, live source updates, missing/empty optional sections and unsafe content.
- All 30 displayed score/efficiency figures were checked against the exact dated
  primary-source fractions/means. No invented composite or copied max-to-high score.
- Skill-creator validator, gh format dry-run, diff checks and live home/health
  checks passed. Existing recommended-license/tag-protection warnings remain.
- Browser AX inspection confirmed all content and repeating sequences. No separate
  responsive-device viewport test was performed in this update.

## Installation

The model-use skill passed the remote format/static audit and was reinstalled
in all eight paths at `1104439e1a69f6e1c9fda54fdce04e4d2df2e726`, whose skill tree equals
`3407c94`. All 32 files, normalized bodies, reference/UI bytes, flat names and
exact commit/tree pins were verified. The service reads the checkout directly.

## Problems / blockers

None for the live page. Exact daily-setting benchmark coverage is absent in the
retrieved source, not an implementation blocker. Do not claim application
competence or subscription efficiency was proved by these higher-effort runs.

## Files currently being worked on

No implementation work remains. This separate handoff records the completed
delivery; preserve any later unrelated work.

## Relevant recent commits

- `3407c94`: rotation clarity, displayed scores/reasons and evidence snapshot.
- `1104439`: keep tests focused on behavior instead of subtitle wording.
- `32e3c5c`: original dashboard, user service and maintenance integration.
- `5475424`: model-use policy and starting choices.

## Immediate next steps

Delivery is complete. Future weekly runs should maintain the tables and explicit
decision reasons. No repeat inference or unchanged runtime tests are needed for
this delivery.

## Things not to do / re-investigate

Do not confuse round robin with route fallback, duplicate Sonnet's family slot,
rank unlike effort/harness configurations as exact equivalents, or invent
remaining plan tokens from API prices. Do not reintroduce DeepSWE or an elaborate
benchmark manager. Keep the existing service local, read-only and lightweight.

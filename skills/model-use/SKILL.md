---
name: model-use
description: Coordinate app building and debugging with round-robin Sol, Sonnet and Gemini Hydrogen workers, CLI-route failover, and project-manager fallback when workers are unavailable.
---

# Model use

Keep the model the user is talking to as project manager. It owns the goal,
acceptance criteria, integration and final verification. Delegate substantial,
independently testable work; do small edits directly when delegation adds overhead.
An explicit user choice of model or workflow takes precedence over this default.

## Round robin

Read [current models](references/models.md) for the dated model/effort choices.
Alternate new tasks between the other two families. This is round robin, not a
preference or fallback order: task 1 uses the first worker, task 2 the second,
task 3 the first again, and so on. Continue an existing task with its worker;
route failure is handled separately below.

| Project manager | New-task rotation (repeat) |
| --- | --- |
| Codex / OpenAI | Sonnet → Hydrogen → Sonnet → Hydrogen → … |
| Claude / Anthropic | Sol → Hydrogen → Sol → Hydrogen → … |
| Gemini / Google | Sol → Sonnet → Sol → Sonnet → … |

Identify the manager by its model family, not its CLI: Claude in Antigravity is
still a Claude manager. Other managers can cycle Sol → Sonnet → Hydrogen.
Sonnet is one slot with two routes, Claude CLI then Antigravity; two routes do
not give it twice as many turns. Hydrogen gets ordinary work, not just failovers.

Keep the next-family pointer in the project's existing local task ledger, or
use `.model-use/state.json` as local state excluded from commits. Only the manager
writes it. Remember the pointer separately for each manager family so changing
the interactive manager does not restart every rotation. A minimal initial state:

```json
{"next":{"sol":"sonnet","sonnet":"sol","hydrogen":"sol"},"unavailable":{}}
```

After selecting a family for a new assignment, save the other family as next
before launching. A switch to the other family updates the pointer the same way.
Resumes, follow-ups and alternative CLI attempts within the same family do not
advance it. Skip known-unavailable routes; do not consume turns just checking
them. Sequential delegation is sufficient; parallel workers need independent
file ownership or separate worktrees, with the manager serializing assignments.

## Assign and verify

Give the worker the goal, relevant context, working directory, owned files,
acceptance checks and a deadline. Ask for changed files, checks/results and any
blocker. Keep follow-up work with that worker until its task finishes. Workers
should return to the manager rather than recursively delegate or integrate
other workers' changes. Passing a task does not expand its authorized scope.

Use the installed `cli-codex`, `cli-claude` or `cli-antigravity` skill for the
selected route's discovery, invocation and feedback. If unavailable, inspect the
binary's help and official documentation rather than inventing flags. Use native
subagents only when they can select the required model/effort; otherwise use the
corresponding CLI. Do not claim a different model fulfilled an exact selection.

Save the worker's session ID as soon as it appears, along with route, model,
requested/effective effort when known, working directory and task progress in the
local ledger. Use bounded deadlines and drain both output streams. Require the
CLI's successful terminal result and verify the task's acceptance checks; startup
events, exit 0 alone and a worker's assertion are insufficient.

## Fail over once, then use the manager

For an unavailable route, try its configured alternative route, then the other
worker family. Make at most one pass through the eligible routes per task; don't
wrap the CLI's own retries in an endless retry loop. Before resuming or switching,
stop/reap the owned process, inspect partial changes and carry progress forward.
Resume the exact session on the same route when supported; another CLI gets a
handoff, not a foreign session ID.

For an interrupted/incomplete run with a saved resumable session and no known
availability block, prefer one bounded resume after inspecting partial work.
Allow at most one such recovery resume per task, within its overall deadline;
if it fails or makes no progress, continue the single fallback pass. Do not
resume a quota/auth-blocked route merely because it has a saved session.

Record unavailable routes with reason, observed time and retry/reset time if
reported. Quota waits until reset; authentication waits for login. If no reset is
reported, make one bounded availability check on a later user turn/run, not a
polling loop. A passed reset allows a recheck, not an assumption of availability.
Timeouts and unknown errors are not proof of exhausted tokens. A different CLI
is not proof of independent quota: propagate a block to other routes only when
the provider explicitly identifies a shared limit. Missing allowance is unknown.

If all eligible workers are unavailable, the manager does the work directly
using its own available allowance. Do not launch its own family as a pretend
fallback worker. If the manager is also limited, save a checkpoint and explain
the blocker. Do not buy credits, change accounts or enable paid API fallback.
Manager fallback retains the last saved pointer; if no worker was assigned,
leave it unchanged.

A worker making no progress on correctness is different from an unavailable
route. The manager diagnoses it or uses a stronger, discovered model for a
bounded escalation; switching CLI to the same model is not a quality escalation.
Preserve the user's model choice and report any change. Keep prompts focused,
reuse useful sessions and avoid repeating whole-repository context to save
allowance. Round robin distributes work; token counts are not interchangeable
subscription balances.

## Weekly refresh

Read [maintenance](references/maintenance.md) only when reviewing the model table
or maintaining the CLI skills. Ordinary tasks use the current table plus live
availability checks; they do not repeat benchmark research.

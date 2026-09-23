---
name: handoff
description: Create or consume a repository handoff so another AI model, agent, session, host, or machine can continue the work with project context, recent Git history, decisions, dead ends, current state, and next steps.
---

# Handoff

Use this skill when handing a repository from one AI model, agent, session, host, or machine to another.

The handoff exists only to let the next agent understand the project, reconstruct recent work, and continue safely without repeating previous investigation.

All handoff material must live under:

```text
.handoff/
```

Do not create broader agent infrastructure.

## Required structure

```text
.handoff/
├── README.md
├── VISION.md
├── CURRENT.md
├── DECISIONS.md
├── DEAD-ENDS.md
├── CODE-MAP.md
└── HANDOFF.md
```

## README.md

Keep this map at the top level of the handoff:

```text
VISION       where are we going?
CURRENT      what programme of work are we in?
DECISIONS    why does the code look like this?
DEAD-ENDS    what have we learned not to do?
CODE-MAP     where is everything?
Git          how did we actually get here?
HANDOFF      where did the previous model stop?
```

Also state that a receiving agent must read the handoff files and inspect recent Git history before continuing work.

## VISION.md

Describe the durable project direction:

- what the project is
- who or what it is for
- what success looks like
- important architectural or product principles
- major intended capabilities
- explicit non-goals where useful

Do not fill this with current implementation detail.

## CURRENT.md

Describe the current programme of work:

- current objective
- current milestone or theme
- active tasks
- priorities
- known blockers
- work expected immediately afterwards

Keep this current.

Remove completed or obsolete material rather than allowing this file to become a historical log.

## DECISIONS.md

Record decisions that future agents would otherwise be tempted to re-derive.

For each significant decision include:

```text
Decision:
Reason:
Alternatives considered:
Consequences:
```

Prefer concise explanations.

Only record decisions that materially affect future work.

## DEAD-ENDS.md

Record negative knowledge.

Include:

- approaches already tried and rejected
- experiments that failed
- misleading code paths
- obsolete implementations
- dead code that remains in the repository
- assumptions proven false
- tempting changes that should not be retried without new evidence

For each useful entry state:

```text
What was tried:
Why:
What happened:
Conclusion:
```

This file exists specifically to prevent agents wasting time rediscovering failures.

## CODE-MAP.md

Provide a compact map of the relevant repository.

Describe:

- important directories
- important entry points
- major modules
- key configuration
- tests
- scripts
- generated code
- legacy or dead areas
- areas currently being changed

Do not document every file.

Point the next agent toward the code that matters.

## Git

Git is part of the handoff.

Do not rely solely on the previous agent's prose description of recent work.

A receiving agent must inspect the current repository state and recent trajectory.

Start with:

```bash
git status --short
git diff
git diff --cached
git log --graph --decorate --oneline -20
git log -20 --stat
```

Then inspect relevant commits with:

```bash
git show <commit>
```

Twenty commits is a default, not a hard limit.

Read far enough back to understand the current coherent body of work. This may require fewer or substantially more commits.

Use Git to establish:

- what changed
- in what order
- what work is recent
- which areas are under active development
- whether changes were reverted or superseded
- how the current working tree relates to committed work

Treat repository state as authoritative over summaries where they conflict.

## HANDOFF.md

`HANDOFF.md` is the immediate handoff from the outgoing agent.

It should contain the current delta, not duplicate all durable project knowledge.

Use:

```markdown
# Handoff

## Current objective

## What was done

## Current state

## Important discoveries

## Problems / blockers

## Files currently being worked on

## Relevant recent commits

## Immediate next steps

## Things not to do / re-investigate
```

Be concrete.

Include filenames, commands, commit hashes, test results and errors where useful.

Do not include long conversational history.

Do not present speculation as established fact.

## Creating a handoff

Before finishing a session:

1. Inspect the actual working tree and recent Git history.
2. Update `VISION.md` only if project direction changed.
3. Update `CURRENT.md` to reflect the current programme of work.
4. Add durable decisions to `DECISIONS.md`.
5. Add useful failed approaches or negative knowledge to `DEAD-ENDS.md`.
6. Update `CODE-MAP.md` if repository structure or important ownership changed.
7. Replace `HANDOFF.md` with the current handoff.
8. Verify that all paths, commands, hashes and stated test results are accurate.

Do not merely summarise the conversation.

Capture what another competent agent needs in order to continue.

## Receiving a handoff

Before making significant changes:

1. Read `.handoff/README.md`.
2. Read `.handoff/VISION.md`.
3. Read `.handoff/CURRENT.md`.
4. Read `.handoff/DECISIONS.md`.
5. Read `.handoff/DEAD-ENDS.md`.
6. Read `.handoff/CODE-MAP.md`.
7. Read `.handoff/HANDOFF.md`.
8. Inspect Git status, diffs and recent commit history.
9. Inspect relevant commits and source files.
10. Reconcile the written handoff with the actual repository.

Do not blindly execute the previous agent's next-step list.

First understand the project and verify the state.

If the handoff contradicts the repository, trust the repository and explicitly note the discrepancy.

## Principles

A good handoff preserves:

```text
vision
context
trajectory
decisions
negative knowledge
current state
next action
```

A bad handoff preserves conversation.

Prefer pointers to authoritative code and commits over copied material.

Prefer verified facts over recollection.

Prefer concise durable context over exhaustive history.

The objective is simple:

> A new agent with no previous conversation should be able to understand what is happening, why it is happening, what has already been learned, and what to do next.

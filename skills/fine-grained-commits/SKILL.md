---
name: fine-grained-commits
description: Organize and regularly push Git work as coherent, browsable commits with clear intent and safe staging. Use whenever planning, staging, creating, amending, pushing, or reviewing commits, or when a task asks an agent to commit or save repository work.
---

# Fine-grained Commits

Create history that lets a future reader understand the pieces of work without reconstructing the entire session.

This skill governs commit organization and delivery. When a user authorizes creating commits, treat that as authorization to push those new commits promptly to the current branch's existing upstream unless the user explicitly requests local-only commits. It does not grant permission to amend, rebase, force-push, or include unrelated changes.

## Choose commit boundaries

Each commit should represent one coherent outcome or reason for change. Group files that must move together for that outcome to work, even when the resulting commit is substantial. Do not split tightly coupled implementation, tests, migrations, canonical data, or required generated output merely to make commits smaller.

Separate changes when they have independent intent or can be understood and reverted independently. In particular:

- Keep repository handoff or agent-context documents in a follow-up commit, separate from the implementation they describe.
- Keep unrelated documentation, formatting, dependency, configuration, and cleanup work out of a feature or fix commit unless it is required by that change.
- Keep tests with the behavior they validate. Use a separate test-only commit only when the tests are independently useful or describe existing behavior.
- Keep generated artifacts with the source change that requires them when the repository tracks those artifacts.
- Keep a data repair or migration with the code enforcing the same integrity outcome when they form one operational unit.
- Never absorb pre-existing or unrelated user changes just to produce a clean working tree.

A useful test is: could the commit message explain every staged hunk with one clear sentence? If not, split it. Avoid both catch-all commits and artificial file-by-file fragmentation.

## Commit workflow

Before the first commit:

1. Inspect `git status --short`, unstaged and staged diffs, and enough recent history to match the repository's conventions.
2. Inventory the current changes by intent, including untracked files, generated files, tests, data, documentation, and handoff material.
3. Plan the smallest sensible ordered series whose intermediate states remain understandable and, where practical, buildable and testable.

For each commit:

1. Stage only the relevant paths or hunks. Use patch staging when a file contains more than one intent.
2. Review `git diff --cached --stat` and `git diff --cached` before committing.
3. Run the most relevant verification for that unit, or clearly report why it was not run.
4. Write an outcome-focused imperative subject. Add a body only when it preserves rationale, constraints, or migration details that are not apparent from the diff.
5. Commit the unit.
6. Push the verified commit to the current branch's configured upstream immediately, then continue with the next unit. Regular pushes are part of the workflow so progress remains visible remotely.

Afterwards, inspect the resulting log, upstream tracking state, and working tree. Report the commits created and pushed, plus any intentionally uncommitted changes.

## History safety

- Do not amend, squash, reorder, or otherwise rewrite existing history unless the user explicitly asks.
- Never force-push as part of this workflow.
- Before pushing, inspect the commits ahead of the upstream. Do not accidentally publish unrelated pre-existing local commits; stop and report when the push scope is ambiguous.
- If the branch has no upstream and the intended remote and branch are unambiguous, establish it with a normal `git push -u`. Otherwise stop and ask for the missing destination.
- If a push is rejected or authentication/network access fails, do not rewrite history or repeatedly retry. Preserve the local commit and report the failure.
- An explicit user instruction not to push, to keep commits local, or to wait before pushing overrides the regular-push default.
- Do not stage secrets, caches, temporary files, test residue, or ignored artifacts.
- If a clean separation would require risky surgery or would make an intermediate commit invalid, prefer the coherent larger commit and explain the tradeoff.

# Handoff — model use, 18 November 2026

## Current objective

Implement the user's simple round-robin delegation policy and a weekly model/CLI
skill refresh, then install the new skill across configured paths.

## What was done

Pushed `5475424`: `skills/model-use/SKILL.md`, UI metadata, dated
`references/models.md`, conditional `references/maintenance.md`, and README usage.
The manager delegates to the other two families. Sonnet has Claude then agy
routes in one slot; Hydrogen gets routine turns. Preserve session identity and
partial work, prefer at most one bounded resume, make one fallback pass, then
use the manager's own available allowance. No new dispatcher or runtime framework.

Created active local project automation `weekly-model-and-cli-skill-maintenance`
through the Codex automation tool. Stored configuration was checked: My-Skills
project `9e9b9cd8-a65a-40c0-a644-42363e4c551c`, Monday 09:00,
`gpt-6.1-sol`, `xhigh`, local execution. Its prompt reads the maintenance reference,
preserves unrelated work and the routing policy, validates/pushes changes, then
audits/reinstalls only changed installed skills. No arbitrary other skills or
binary upgrades are authorized. The first scheduled execution has not run.

## Current state

Creation, scheduling and installation are complete. The user renewed GitHub CLI
authentication and gh auth status returned exit 0. The explicit
`skillstrap.sh install dav-rob/My-Skills model-use` passed format/static audits
and installed flat copies in all eight configured paths at
`c5f2990b5610840518796cfc26cc14946279f712`. Its skill tree is identical to `5475424`.
All 32 files were verified: normalized SKILL.md bodies, byte-identical references
and UI metadata, exact source/commit/tree metadata, non-symlink flat directories,
and gh listing name/path/pinned/version. Installed skillstrap list succeeds.
The existing weekly automation was rechecked as active with the expected model,
effort and schedule. Its first scheduled execution remains unverified.

## Verification

- Read-only model discovery: Codex 0.168.0 app-server, Claude 2.1.323 stream
  initialization, agy 1.5.11 model list. Sol 6.1/high/xhigh, Sonnet 5.5/high and
  Hydrogen/high are exposed. Newer models are candidates, not automatic upgrades.
- Four live bounded smoke calls: Sol/high via Codex, Sonnet/high via Claude,
  Sonnet/high via agy and Hydrogen/high via agy. All exit 0, expected answer,
  successful terminal result and usage; no required-action denial in agy results.
  Temporary workspaces only; effective effort remains unknown when not echoed.
- Independent instruction-based checks: seven scenarios covering ordinary
  rotation, Sonnet alternate route, manager family through a different CLI,
  exhausted workers, partial edits/timeouts, missing completion event and no-op
  weekly review. Recovery and pointer ambiguities were fixed and rechecked.
- Skill-creator validator, relative links, `gh skill publish . --dry-run`,
  existing local static scanner and diff checks passed. The dry-run has the
  existing recommended-license warnings. PyYAML was installed only in a temporary
  dependency directory for the validator; no project dependency was added.
- No installer/runtime changes: the old 49-test result is historical; it was not
  rerun for this instruction-only addition. No app competence benchmark, real
  provider-limit exhaustion or completed weekly automation run is claimed.

## Problems / blockers

No blocker remains for model-use. The initial invalid GitHub CLI token was
resolved by the user; no credential values were read or logged. Cursor login
remains an earlier unconfirmed item, outside this rotation.

## Files currently being worked on

No implementation files remain in progress. These handoff changes record the
completed installation separately; preserve any later unrelated work.

## Relevant recent commits

- `c5f2990`: initial delivery handoff and source pin used for installation.
- `5475424`: model-use skill, maintained choices/procedure and README.
- `afcc154`: agy structured output and version 1.4.0 guidance.
- `846855a`: durable CLI session identity and Antigravity web follow-up.
- `5cad8bf`: authenticated Claude verification and allowance feedback.

## Immediate next steps

Use model-use explicitly or through compatible skill discovery for subsequent
app work. Weekly maintenance will review the dated table and relevant CLI changes.
No further installation, repeated inference or unchanged runtime tests are needed
for this delivery; assess the first scheduled result when it runs.

## Things not to re-investigate

Do not count two Sonnet routes as two family turns, identify a manager by its CLI,
or launch the manager's family as a pretend worker fallback. Do not infer quota
from timeouts, consumed tokens or API prices; alternate routes have independent
availability only when observed. Exclude DeepSWE. Keep benchmark categories
stable while discovering current individual evaluations through Artificial
Analysis; no invented composite ranking or weekly benchmark framework.

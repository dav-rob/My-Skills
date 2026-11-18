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

Skill creation and scheduling are complete. Installation is blocked by invalid
GitHub CLI authentication, not an audit finding. The attempted
`skillstrap.sh install dav-rob/My-Skills model-use` stopped before any audit or
destination write. The user has an asynchronous request to run
`gh auth login -h github.com`. Git push still succeeds. Do not assume login until
the user confirms and authentication is checked.

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

gh auth status reports the github.com token in its hosts.yml is invalid; no
auth environment override is present. No credential values were read or logged.
Cursor login remains an earlier unconfirmed item, outside this rotation.

## Files currently being worked on

Only the handoff documents are the follow-up to `5475424`. Installation and its
verification remain after GitHub CLI login. Preserve any later unrelated work.

## Relevant recent commits

- `5475424`: model-use skill, maintained choices/procedure and README.
- `afcc154`: agy structured output and version 1.4.0 guidance.
- `846855a`: durable CLI session identity and Antigravity web follow-up.
- `5cad8bf`: authenticated Claude verification and allowance feedback.

## Immediate next steps

After confirmed gh authentication, run the explicit model-use skillstrap install,
verify all active configured destinations against its published source body,
metadata pin and three supporting files, then update this handoff in a separate
commit. No need to rerun inference or unchanged runtime tests.

## Things not to re-investigate

Do not count two Sonnet routes as two family turns, identify a manager by its CLI,
or launch the manager's family as a pretend worker fallback. Do not infer quota
from timeouts, consumed tokens or API prices; alternate routes have independent
availability only when observed. Exclude DeepSWE. Keep benchmark categories
stable while discovering current individual evaluations through Artificial
Analysis; no invented composite ranking or weekly benchmark framework.

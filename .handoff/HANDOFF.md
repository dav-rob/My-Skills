# Handoff

## Current objective

Prepare five CLI skills, verify commands and model/effort/error protocols against
local binaries, and install flat copies in all configured directories. The user
confirmed the duplicated Cursor entry meant Codex, permits YOLO execution, and
asked to prioritize discovery/testing of OpenCode's rotating free models over
local oMLX models.

## What was done

Searched OMGSkills and the web; reviewed candidates at explicit GitHub revisions.
Created independently authored guides rather than importing third-party bodies,
wrappers or installers. Sources and limitations are in `docs/CLI-SKILLS.md`.
Added two discovery protocol references for Codex/Claude. No new runner framework.

Native gh remote install preserves flat folder/frontmatter but lists the source
as `cli/cli-codex`. Fixed skillstrap uninstall to recognize a single safe source
scope while checking the exact requested flat leaf and configured parent. Added
nested-source, scoped-name and path-safety regression coverage. Remote metadata
remains intact. Updated local skillstrap with the requested curl bootstrap;
its bytes match repository source.

## Current state

49 tests passed under sh and dash (40 distribution plus nine credential-helper).
`sh -n`, diff checks, skill-creator validation and gh format dry-run passed.
All five skills passed the existing static scan. Local gh packaging verified flat
names, directories and reference files; pinned remote packaging exposed the scope
identity quirk. Live flat-name uninstall with that metadata preserved an unrelated
skill in a temporary HOME.

Four skills were audited and installed into eight real configured paths at
`6ea908e358878b3509915ea07da0a2368340d5f7`; OpenCode was audited and installed at
`5e51d21`. All 40 copies were verified for flat names/directories, current skill
bodies, intact references, exact github-path and commit pin. Installed skillstrap
list succeeds. Bootstrap did not install unrelated repository skills.

## Important discoveries

- Codex 0.161.0: app-server model/list gives supportedReasoningEfforts; a live
  gpt-6.1-sol/high JSONL request completed. account/rateLimits/read works.
- Cursor Agent 2026.10.01-e373342: bracket model parameter syntax in help;
  model-list and inference both need authentication.
- Claude 2.1.294: stream control initialization gives resolvedModel and
  supportedEffortLevels. Auth failure has exit 1 and is_error true even alongside
  subtype success. Auth status remains loggedIn false.
- Antigravity agy 1.3.1: model list, JSON/streaming Gemini3.8/high inference,
  /usage text quotas and invalid/conflicting effort failures verified. Actual
  timeout default in help is 0s, unlike fetched documentation; set it explicitly.
- OpenCode 1.18.35: refresh free model list; loopback /config/providers exposes
  variants. Space Bunny Free and Ling3.1 Flash Free at low completed with final
  step_finish/stop, tokens and zero cost. oMLX Qwen3.6 completed within 90 seconds;
  Qwen3.8 emitted only a start event by 90 seconds, then was terminated/reaped.
  No OpenAI provider configured; no login needed for the tested free models.

## Problems / blockers

User authentication is needed for Cursor and Claude inference/model-entitlement
verification. They were given cursor-agent login and claude auth login commands
through the asynchronous question tool. Do not interpret silence as login.
Qwen3.8 completion remains unverified; diagnosing or configuring oMLX wasn't the
main task. No quota/context exhaustion was deliberately induced.

## Files currently being worked on

Delivery files: `skills/cli/`, `docs/CLI-SKILLS.md`, README, skillstrap and tests.
Implementation and installation are complete. Handoff is a separate follow-up.

## Relevant recent commits

- `5e51d21`: dynamic OpenCode free/local model discovery and verified outcomes.
- `6ea908e`: flat-name uninstall for remote scoped source identities.
- `3c9c00e`: five verified CLI guides, source review and nested-source regression.
- `29424e8`: configurable install paths and scheduled jobs default.

## Immediate next steps

When the user confirms authentication, recheck Cursor models/parameters and
Cursor/Claude tiny non-mutating inference, update verified scope, commit/push and
explicitly reinstall only any skills whose content changed. Do not re-run all
checks or deliberately consume an account limit to prove exhaustion detection.

## Things not to do / re-investigate

Don't import obsolete --full-auto, discarded-stderr patterns, host-specific
wrappers or token estimates from third-party candidates. Don't remove remote
source metadata to disguise gh's scoped listing. Local gh name matching differs
from remote exact-path selection. Don't infer login failure or quota exhaustion
from a startup-only OpenCode timeout. No implicit all-skills install at bootstrap.

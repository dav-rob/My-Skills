# Handoff — Antigravity skill refresh, 16 October 2026

`afcc154` adds `skills/cli/cli-antigravity/references/structured-output.md` and updates
`SKILL.md`, `references/follow-up.md` and `docs/CLI-SKILLS.md`. Trigger: a Scheduled Jobs
weekly digest failed in ten seconds because its shared report schema had `null` in an
`error_code` enum; Gemini returns exit 3 with `INVALID_ARGUMENT` for that, and every
Antigravity run had failed since 14 October without anyone noticing.

Facts re-checked on agy 1.4.0 (the CLI had auto-updated from 1.3.3): the rejection
shape, accepted schema constructs, Gemini filling required nullable fields with junk,
the result envelope (`structured_output` is independent of `response`), a real eight
minute research run with a schema, and exit statuses 1, 2 and 3. Changelog-only items
are labelled as such. Not re-checked: `/usage`, exact-ID resume, denied-action handling,
remote control, other models and other schema keywords.

Reinstalled with `skillstrap.sh install dav-rob/My-Skills cli-antigravity` into all eight
configured paths. It pinned to `d146697` (the handoff commit after `afcc154`), whose
`skills/cli/cli-antigravity` tree hash `bd060d9` is identical, and every copy's
`github-tree-sha` pin matches it. A read-only comparison found all three files in all
eight copies equal to `afcc154`; `gh skill` only reorders the frontmatter, adds its pin
block and drops the blank line after it, so compare bodies, not whole files. No other
installed skill file changed. This handoff is a separate documentation commit.

## Earlier handoff — provisional gh-chat, 15 October 2026

The requested `gh-chat` skill is created and pushed as `b766765`.
`skills/gh-chat/SKILL.md` is the entrypoint; its conditional reference supplies a
minimal ledger/outbox, wake-up procedure, notification caveats and behavioural
cases for future iterations. `agents/openai.yaml` and the root README make it
discoverable and document explicit installation.

The skill is provisional and currently PR-only, aimed at communication that can
resume after context or account usage-limit interruptions. It records the two
observed PR-monitor patterns without promising universal quota recovery or
silent mobile delivery. Seen/unanswered states are distinct; uncertain posts are
reconciled before retries; review approval does not invent merge/deploy authority.

Validation passed: skill-creator quick validation, relative references, GitHub
skill publish dry-run and remote skillstrap format/static safety audit. The
publish dry-run reported the existing recommended-license/tag-protection warnings.
No live PR/automation/device setting was changed and nothing was installed.
No new runtime, live notification acceptance or induced quota exhaustion is
claimed. Improve this provisional version from subsequent authorised use; issues
and a general chat transport remain explicitly deferred.

This handoff is a separate documentation commit. The existing CLI-skill status
and outstanding provider checks below remain unchanged.

---

# Earlier handoff — CLI resume skills

## Current objective

Update the existing Antigravity and Codex CLI skills with tested scheduled-jobs
lessons, then refresh their installed copies. This request is complete.

## What was done

Pushed `846855a`: early durable session identity and interruption retention for
both CLIs; stdin NDJSON and required-tool soft denial handling for Antigravity;
a conditional `references/follow-up.md` for temporary/persistent web access and
schema resume; safe exact-ID Codex command guidance. Updated the dated verification
record in `docs/CLI-SKILLS.md`. No new runner or installer changes.

## Current state

Both skills passed skill-creator validation, reference-link checks, installed CLI
flag checks and `gh skill publish . --dry-run`. The dry-run reported existing
recommended-license/tag-protection warnings. Default Python lacked PyYAML; the
existing scheduled-jobs `.venv/bin/python3` ran the validator successfully.

Both selected skills passed skillstrap format/static audits and were installed
into all eight configured paths at `846855a9cac574751f1714ffb959a971bca9db09`.
All 16 copies were checked for matching bodies, references, flat names, exact
source paths and commit pins. gh rewrites YAML and a separating blank line;
body comparison normalized only surrounding newlines. Unrelated skills remain
at their earlier pins. Runtime/services and install-path configuration unchanged.

## Important discoveries

The reusable lessons and their evidence are recorded in `docs/CLI-SKILLS.md` and
the skills themselves. The stale Antigravity structured-output result is one
observation, not a reproduced universal behavior. Codex interruption handling
was tested with fake events; no live mutating resume was executed for this update.

## Problems / blockers

None for this request. Prior Cursor authentication/inference checks and Qwen3.8
completion remain unverified; see the earlier verification record. Quota
exhaustion, remote-service reboot/logout recovery and locked-screen GUI capability
were not tested. No extra inference was run merely to update documentation.

## Files currently being worked on

None. Skill implementation is committed/pushed; this handoff is a separate commit.

## Relevant recent commits

- `846855a`: durable CLI resume and Antigravity web follow-up guidance.
- `897de0b`: previous authenticated Claude delivery handoff.
- `5cad8bf`: authenticated Claude parsing and allowance checks.

## Immediate next steps

Use the refreshed skills for future CLI work. Only revisit outstanding provider
checks when relevant and authorized; do not replay live tasks to validate a resume
command or deliberately induce quota exhaustion.

## Things not to do / re-investigate

Don't conflate plan instructions with enforced read-only access, CLI success with
required-tool completion, editor remote instances with CLI history, temporary
remote tunnels with persistent services, or UUID capture with persisted history.
Preserve audited source metadata and the flat-install/scoped-listing behavior.

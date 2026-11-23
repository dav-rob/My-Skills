# Handoff — weekly model and CLI maintenance, 23 November 2026

## Current objective

Maintain model evidence, relevant CLI skills and the existing local dashboard.
This pass is complete; keep the user's round robin and daily settings.

## What was done

Published three reviewed commits to origin/main:

- `57f4669`: Antigravity early-stop/timeout completion contracts, newer default
  mode/review behavior and Claude exact-model refusal-fallback guidance.
- `8e64268`: current discovery, unchanged original scores and explicit smoke/auth
  limitations in the model reference.
- `8b0a32e`: Neon/xhigh challenger scores, selection reason and public snapshot.

AA v2.1 remains FrontierCode-AA 2.0, SWE-Atlas-QnA-AA and Terminal-Bench 4.1.
All five previously retained raw score/telemetry/version rows compare exactly
unchanged. Resolved highlighted chart references to recover Neon/xhigh:
43.0% implementation, 67.7% repository Q&A, 65.2% terminal; 125.6k output tokens,
30.5 agent minutes and $6.86 reported API cost/task. It is a candidate, not a
replacement, subscription saving or a measured Neon/high configuration.
The six-row snapshot preserves raw fractions, means, CLI versions, source hash
and retrieval time. No new app benchmark was run. DeepSWE was excluded.

## Current state

All changes are pushed. No runtime/dashboard hosting code changed. The service
at http://127.0.0.1:48173/ reads the canonical files live, now showing assessment
2026-11-23, the unchanged recommendation table, six score/efficiency rows and
updated selection reasons. The existing listener remains 127.0.0.1 only.
This standalone pass did not delegate or advance the project's rotation pointer.

## Verification and installation

- Codex 0.168.0 app-server discovery exposed Sol 6.1/high/xhigh; quota read succeeded.
- Claude 2.1.323 initialization exposed Sonnet 5.5/high; authentication was present.
  One no-tools smoke with refusal fallback disabled reached requested-model startup
  but missed the 55-second external deadline. Stopped/reaped its owned process group;
  no terminal result, usage or effective-effort measurement. No quota diagnosis.
- agy 1.5.11 help and public release notes reviewed; model listing required sign-in.
  Skipped inference and Neon trial. No login/account/credit/binary changes.
- Relative references, diff checks and gh skill publish . --dry-run passed. The
  skill-creator validator was attempted but PyYAML is absent in available Python
  installations. Did not install it; gh provided format validation. Existing
  recommended-license/tag-protection warnings remain.
- 42 dashboard tests passed with warnings as errors. Live health/home passed;
  date and all four exact model/effort/route rows matched the canonical reference.
  All 36 displayed capability/efficiency figures matched the six-row snapshot.
- Explicit skillstrap installs passed format/static audits for only the three
  changed installed skills. cli-claude / cli-antigravity pinned to
  `8e642689f0ec776df698d1fc3c2d81e4a64583a7`; model-use pinned to
  `8b0a32e90ef05bf190e431ed4c5419cd2530e6ce` in all eight configured paths.
  All 72 files, flat names, normalized bodies, supporting bytes, commit/tree pins
  and all 24 gh listings verified. gh's CLI install preview said it could not
  read the scoped display directory; independent flat-path verification passed.

## Important discoveries

Public chart rows can be RSC references, not objects. In this page some are
`$31:props:children:props:rows:N`, resolved from the same response's section 31
highlighted rows. Resolve these before claiming a model is missing. Across all
41 resolved variants, daily high rows, Sol6.1/xhigh, Neon/high and agy Sonnet are
still absent. Do not assign higher-effort/fallback scores to those settings.

## Problems / blockers

Antigravity sign-in is required before live catalog/route checks or a Neon trial.
Sonnet's current inference success remains unverified after the bounded timeout.
A successful future smoke will establish connectivity, not app competence.
The Python skill-creator validator dependency remains unavailable; gh validation
and skillstrap audits passed. No dashboard failure remains.

## Files currently being worked on

No implementation work remains. This separate handoff records the completed pass.
Preserve any later unrelated changes.

## Relevant recent commits

`57f4669`, `8e64268`, `8b0a32e`; earlier policy/dashboard delivery is in
`3407c94`, `1104439`, `ca91ecc`. Installation pins are intentionally per skill.

## Immediate next steps

On the next weekly run, read automation memory first, then this handoff and Git.
Compare current primary data against the 23 November snapshot. Rediscover routes
without upgrading binaries. If agy sign-in has been restored, a bounded Neon
availability check may be useful; any recommendation change needs a representative
isolated app task. Check dashboard health/home even on a no-change pass.

## Things not to do / re-investigate

Do not change rotation or replace Hydrogen solely from a public xhigh score.
Do not confuse model-provider refusal fallback, CLI availability fallback and
round-robin alternation. Keep exact-model Claude requests on the selected model;
report refusals rather than silently relabelling a fallback model's work.
Do not exhaust quota, switch accounts, enable paid fallback, upgrade binaries or
reinstall unchanged skills. Do not copy around a failed skillstrap audit.

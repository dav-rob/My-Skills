# Current

Weekly maintenance completed on 2026-11-23. The round robin and daily settings
remain Sol 6.1/high (xhigh for justified escalation), Sonnet 5.5/high and Gemini 4
Hydrogen/high. The standalone assessor worked directly; rotation state was not
advanced. The local Monday 09:00 automation is `weekly-model-and-cli-skill-maintenance`,
configured for Sol 6.1/xhigh and this checkout.

Published changes:

- `57f4669`: Antigravity partial-result/timeout contracts, default Auto and review
  constraints; Claude exact-model refusal-fallback handling and verification limits.
- `8e64268`: dated weekly discovery/evidence and route limitations; choices retained.
- `8b0a32e`: Gemini 4 Neon/xhigh candidate scores and a six-row public snapshot at
  `docs/model-scores/2026-11-23.json`. The five prior configurations are unchanged.

Neon/xhigh beats Hydrogen/xhigh on all three AA v2.1 components, using fewer
output tokens and slightly less runtime, but higher API cost. Local access and
Neon/high are unverified. No app trial supports replacing the user's selection.
Matched public rows remain absent for daily high settings and Sonnet via agy.

Codex 0.168.0 and Claude 2.1.323 read-only discovery confirmed selected support.
agy 1.5.11 model discovery required sign-in, blocking both agy route checks and a
Neon trial. The no-tools Sonnet/high smoke with refusal fallback disabled reached
startup but timed out after 55 seconds; process group stopped/reaped, no terminal
result or usage. This does not diagnose quota. No accounts, credits or binaries
were changed. Cursor/OpenCode had no relevant trigger.

All three changed skills passed gh format validation and explicit skillstrap
format/static audits, then were installed into all eight configured paths.
cli-claude and cli-antigravity are pinned to `8e64268`; model-use to `8b0a32e`.
All 72 files, flat names, reference bytes, normalized source bodies, commit/tree
pins and all 24 gh listings were verified. Unchanged installed skills were left
alone. The skill-creator Python validator could not run because PyYAML is absent;
no dependency was installed. gh validation passed with existing advisory warnings.

The read-only dashboard remains at http://127.0.0.1:48173/, reading canonical
Markdown per request. No hosting code, service configuration or policy summary
changed. The 42 dashboard tests passed with warnings as errors. Health/home,
23 November assessment date, all four model/effort/route rows and all 36 score /
efficiency values passed live checks; one existing loopback listener remains.

The remaining programme is bounded weekly model/CLI upkeep using
`skills/model-use/references/maintenance.md`. Before a Neon trial, restore agy
sign-in interactively, rediscover model/effort support and use an isolated app
task with acceptance checks. Do not infer application competence, effective
effort or subscription allowance from startup or higher-effort public rows.

Installer design and stable CLI verification scopes are in README.md,
docs/CLI-SKILLS.md, DECISIONS.md and Git. Eight configured installation roots,
audited exact pins and destination preflight remain in place. The vision remains
any GitHub source and every compatible tool, with safety and security foremost.

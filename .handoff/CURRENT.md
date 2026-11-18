# Current

The current addition is `model-use`, pushed as `5475424` on 2026-11-18. The
interactive model remains project manager and alternates substantial coding
tasks between the other two families: Codex uses Sonnet/Hydrogen; Claude uses
Sol/Hydrogen; Gemini uses Sol/Sonnet. Sonnet's Claude/agy routes share one slot.
Local state records next-family pointers, unavailable routes and resumable work.
There is one bounded recovery resume and a single fallback pass, then the manager
works directly if its own allowance permits. This is an instruction-only skill.

Starting choices are Sol 6.1/high (xhigh when justified), Sonnet 5.5/high, and
Gemini 4 Hydrogen/high. All four CLI routes passed live smoke checks against
Codex 0.168.0, Claude 2.1.323 and agy 1.5.11. Independent behavioral checks covered
rotation, route fallbacks, manager identity, limits, interruption, missing
terminal events and unchanged maintenance. Validation, relative references,
format dry-run, static scan and diff checks passed. No app benchmark or deliberate
quota exhaustion is claimed; no installer/runtime code changed.

The active local Codex automation `weekly-model-and-cli-skill-maintenance` targets
this project on Mondays at 09:00, using `gpt-6.1-sol` / `xhigh`. Its procedure is
`skills/model-use/references/maintenance.md`: use Artificial Analysis's current
coding evaluations, exclude DeepSWE, preserve choices without meaningful new
evidence, maintain only the model table and five CLI skills, and audit/reinstall
only changed skills after validation and publication.

Installation is pending: skillstrap stopped before audit/writes because gh's
saved github.com token is invalid. The user was asked to run
`gh auth login -h github.com`. Git pushes still work. Do not bypass the normal
audited installation; after login, explicitly install model-use into all active
configured paths and verify its body, references and pin.

The prior CLI and installer state is documented in `docs/CLI-SKILLS.md`, Git and
the durable handoff files. The latest Antigravity skill was reinstalled at
`d146697` after agy 1.4.0 schema verification (`afcc154`). The five CLI skills
retain their independently dated verification scopes; discovery/smoke checks
above do not revalidate every feature. Cursor authentication remains unconfirmed.

Configurable paths remain as implemented in `29424e8`: eight defaults including
scheduled jobs, explicit audited commit pins and destination preflight. Removing
a path leaves content in place. Bootstrap installs the command only. The vision
remains any GitHub source and every compatible tool, with safety and security
foremost. Static audits remain incomplete and sequential installs can partially
succeed.

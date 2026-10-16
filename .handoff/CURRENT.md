# Current

The latest update is `afcc154` (16 October 2026): `cli-antigravity` gained
`references/structured-output.md` and refreshed facts for agy 1.4.0. A schema with a
`null` in an enum is rejected by Gemini (exit 3) and had failed every Scheduled Jobs
Antigravity run since 14 October; the reference also covers optional nullable fields,
`structured_output` versus `response`, and a probe recipe. Validated with skill-creator,
relative links, `gh skill publish --dry-run` and the 49 tests. It was then reinstalled
into all eight configured paths (pinned to `d146697`, whose skill tree equals `afcc154`);
all 24 files were verified against `afcc154`, and no other installed skill changed.

The previous addition is provisional `gh-chat`, pushed as `b766765` on 15 October
2026. It covers sustained agent-to-agent PR communication: signed identities on
shared accounts, durable checkpoints/outbox reconciliation, usage-limit recovery,
new/edited and unanswered requests, notification controls, explicit review
approval and authorised closure/integration. Issues and general chat are future
experiments. It is instruction-only; no runner or new automation was deployed.
Skill-creator validation, relative links, `gh skill publish --dry-run`, and the
remote skillstrap format/static audit passed. Nothing was installed. The dry run
retains the repository-wide recommended license/tag-protection warnings.

The previous focused update was `846855a` (2026-10-12): Codex and Antigravity now
save resumable identity early and retain it on interruption. Antigravity also
covers stdin NDJSON, required-tool soft denials, temporary/persistent web access,
and a carefully qualified stale structured-output observation. Source details
and validation limits are in `docs/CLI-SKILLS.md` and the Antigravity follow-up
reference. This is documentation only; no installer/runtime behavior changed.
Both updated skills were audited and reinstalled into all eight configured paths
at that commit; all 16 copies, references and pins were verified.

Five CLI skills are prepared under `skills/cli/`: cli-codex, cli-cursor,
cli-claude, cli-antigravity and cli-opencode. They were researched through
OMGSkills and official sources, independently written, and checked against
installed binaries. They cover native model/effort discovery, authorized YOLO
options, deadlines and caller-visible completion/errors/usage. See
`docs/CLI-SKILLS.md` for pinned candidate sources and verification limits.

Implementation is pushed as `3c9c00e`, `6ea908e` and `5e51d21`. The source grouping
installs flat; all five are installed in all eight configured paths (40 copies).
gh reports remote scope/name identities from source metadata;
uninstall accepts a single safe source scope while retaining exact target/parent
checks. The local skillstrap command was updated by curl bootstrap and matches
the repository. 49 offline tests passed under sh and dash; format/static checks,
nested local/remote packaging and live flat-name uninstall also passed.

Codex (GPT-6.1 Sol/high), Antigravity (Gemini 3.8 Flash/high), two discovered
OpenCode free models at low effort, and oMLX Qwen 3.6 completed smoke requests.
Claude is now authenticated: Sonnet 5.5/high JSON and Haiku 5.5/low streaming
completed, including usage and allowance events. The CLI did not echo effective
effort levels. Its guide was updated in `5cad8bf`. Qwen 3.8 didn't finish within
90 seconds. Cursor still awaits confirmed login and successful inference checks.
Never claim real quota/context exhaustion was induced or verified.

Configurable install paths remain as implemented in `29424e8`: eight defaults
including scheduled jobs, saved active-list configuration, explicit selection,
audited commit pins, and complete destination preflight. Removing a path leaves
its content in place. Bootstrap installs the command only. The vision remains
any GitHub source and every compatible tool, with safety and security foremost.
Static audits remain incomplete and sequential installs may partially succeed.

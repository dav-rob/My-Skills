# Code map

- `skillstrap.sh`: bootstrap, argument checking, clone/validation/static audit,
  pinned installation into configured directories, exact-name uninstall and list.
  `paths` subcommands maintain `~/.config/skillstrap/install-paths`; defaults include
  seven tool directories plus `~/.scheduled-jobs/skills`. Configuration is local
  user data, not tracked in this repository.
- `tests/test_skillstrap.py`: offline CLI regression suite using temporary homes,
  mock commands and real local Git fixtures. `TEST_SHELL` chooses the shell.
- `README.md`: operator commands, audit/deletion limits and verification commands.
- `skills/exact-address/SKILL.md`: canonical renamed address-finding skill.
- `skills/fine-grained-commits/`: commit/push workflow and agent metadata.
- `skills/handoff/SKILL.md`: repository handoff workflow.
- `skills/model-use/`: round-robin worker policy with local project state;
  `references/models.md` contains dated choices/evidence and
  `references/maintenance.md` is the weekly model/CLI refresh procedure. The
  schedule is local Codex automation state, not a repository runtime.
- `dashboard/server.py` and `dashboard/index.html`: read-only loopback dashboard,
  rendered from model-use markdown per request. `dashboard/install_service.py`
  installs its macOS user service; operation commands are in the README.
- `tests/test_model_dashboard.py`: isolated live-update, rendering/escaping,
  source-error and HTTP-boundary checks plus a real-source CLI lifecycle check.
- `docs/model-scores/`: dated selected primary-source score/telemetry snapshots,
  referenced by the model assessment workflow; source fractions and CLI versions
  preserve provenance independently of displayed rounding.
- `skills/gh-chat/`: provisional PR communication skill, UI metadata and conditional
  checkpoint/monitoring reference. No runtime; issues/general chat deferred.
- `skills/cli/cli-*/SKILL.md`: five native CLI invocation/model/effort/feedback
  guides, grouped in source but installed as flat cli-* folders. Codex/Claude
  discovery protocol details are supporting references within each skill.
  Antigravity's `references/follow-up.md` covers remote web access, its lifecycle
  and schema-result consistency after resume.
- `docs/CLI-SKILLS.md`: pinned research candidates, installed-binary checks and
  verification limits for the CLI collection.
- `skills/mac-login/SKILL.md`: scoped Mac Keychain website-login workflow and
  the tested native Chrome paste method. `scripts/credentials.py` inside the
  skill is its standalone setup/check/clipboard helper; nine isolated regressions
  are in `tests/test_mac_login_credentials.py`.
- Former `skills/link-skills.sh`: removed in `be59bd2` after native Antigravity 2.0
  discovery was verified; no repository callers depended on it.
- `.handoff/`: project context, kept separate from implementation commits.

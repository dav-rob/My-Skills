# Handoff

## Current objective

Latest request complete: create and check in a `mac-login` skill describing the
tested Mac Keychain website-login workflow. `b9abc7a` is pushed on main. Its
entrypoint and helper are self-contained; see `skills/mac-login/SKILL.md`.

Corrected the vision to distributing skills from any GitHub repository to every
compatible tool, as safely and securely as possible. Antigravity 2.0 installation
and discovery support was completed beforehand.

## What was done

Updated VISION, README and current/decision context to reflect the user's clarified
scope and security priority. This correction changed documentation only; the
current implementation still supports seven targets and a static pre-install audit.

Added `antigravity2.0` while retaining older Antigravity and CLI targets. Added
`.gemini/config/skills` to the uninstall allowlist and expanded regression coverage
from six to seven destinations. Updated the installed command, installed
exact-address, verified actual app discovery, and retired the legacy linker.

## Current state

- 33 tests pass under sh and dash (24 distribution/nine credential-helper);
  skill format, shell syntax and diff checks pass.
- Bundled credential helper's fresh-process readonly access check passed for
  the previously authorized Rightmove Keychain item. No credential values were
  printed, no item was modified, and no new browser login/import was performed
  while packaging the skill. The daily task remains owned by the auction chat.
- Bootstrap downloaded the pushed script, updated `~/.local/bin/skillstrap.sh`,
  and was verified byte-for-byte against the repository source.
- The updated command installed exact-address for all seven targets at `1988bce`.
- `gh skill list --scope user --agent antigravity2.0` reports the pinned skill at
  `/Users/davidroberts/.gemini/config/skills/exact-address`.
- Antigravity 2.18.1 lists exact-address as a Global skill in Settings → Customizations.
  The app was left on that screen for the user to inspect.
- Skill execution against a property listing was not tested; this verified discovery.

## Important discoveries

GitHub CLI 2.101.0 has separate `antigravity`, `antigravity2.0` and
`antigravity-cli` mappings. The old target uses `.gemini/antigravity/skills`, the
new app uses `.gemini/config/skills`, and the CLI uses `.gemini/antigravity-cli/skills`.
No plugin bundle is needed. The slash picker initially showed no match; the
Customizations screen showed the newly installed skill.

## Problems / blockers

None for the requested installation/discovery work. Static audits remain
intentionally incomplete. Unknown uninstall directories are refused. Sequential
agent installation may leave earlier successful installs when a later one fails.

## Files currently being worked on

Implementation finished: `skillstrap.sh`, `tests/test_skillstrap.py`, `README.md`.
`skills/link-skills.sh` was removed; existing user links/plugin files were not deleted.

## Relevant recent commits

- `b9abc7a`: add mac-login instructions, parameterized Keychain/clipboard helper
  and nine isolated regression checks.

- `1988bce`: add Antigravity 2.0 install/uninstall support, tests and usage docs.
- `be59bd2`: retire linker after native app discovery was confirmed.
- `af29653`: constrain uninstall paths and preflight removals.
- `8b3c391`: preserve audit failures and pin installs to audited commits.
- `ee874dc`: atomic bootstrap and idempotent PATH setup.

## Immediate next steps

No outstanding requested work. Read this handoff, inspect current Git status/diffs
and recent history, and run README checks before further changes.

## Things not to do / re-investigate

Do not restore implicit skill installs, expose checkout content through automatic
symlinks, rename exact-address back, or assume gh installation proves app discovery.
Keep implementation changes focused and dependable while serving the broader
vision. The current wrapper, tool list and audit are not limits on that vision.

# Decisions

Decision: Make mac-login a direct dedicated-Keychain workflow for unattended
website/browser-based tool sign-in when a password manager needs a human unlock.
Reason: The user wants reusable instructions that avoid unsuccessful autofill and
vault exploration. Password-manager protections remain intact.
Consequences: Generic examples only; credential retrieval and browser operation
are verified separately. Native-only tools need their own integration, and
screen-lock/reboot reliability must not be inferred from a retrieval check.

Decision: Define the project around any GitHub source, every compatible tool,
and the safest, most secure distribution possible.
Reason: The user clarified that personal skills and the current supported tools
describe today's implementation rather than the vision.
Alternatives considered: Limiting the goal to dav-rob/My-Skills and seven targets.
Consequences: Future coverage and safeguards should serve this broader goal;
do not describe current static checks as the final security solution.

Decision: Bootstrap only installs the command and its PATH line.
Reason: Skill installation must always be explicit.
Alternatives considered: Implicit installation of all personal skills.
Consequences: `install` requires a name or `--all`, including rejecting empty names.

Decision: Install from the exact audited commit, and exact path for a named skill.
Reason: Default HEAD can change and gh otherwise prefers the latest release tag.
Alternatives considered: Unpinned fetch after audit; copying temporary local files.
Consequences: Remote source metadata is retained; rerun explicit install for updates.

Decision: Use subshell functions for audit helpers.
Reason: POSIX shell function variables otherwise overwrite caller status/state.
Alternatives considered: Non-POSIX `local`; manual global-variable prefixes.
Consequences: Bulk format failures survive successful static scans.

Decision: Preflight all uninstall paths and check physical parent directories.
Reason: String-prefix checks allow traversal and symlink escapes.
Alternatives considered: Removing any reported path containing `/skills/`.
Consequences: Only active configured directories can be removed; leaf symlinks
can be unlinked. Each existing parent component is checked for symlinks.

Decision: Include `antigravity2.0` alongside the older Antigravity and CLI targets.
Reason: gh maps Antigravity 2.0 to `.gemini/config/skills`, while the older target
uses `.gemini/antigravity/skills`. Installation success alone does not prove app discovery.
Alternatives considered: Packaging skills as a plugin; dropping the older target.
Consequences: Default directories include `.gemini/config/skills` alongside both
older Antigravity locations; configurable paths now control placement.

Decision: Retire the legacy linker after verifying native app discovery.
Reason: Antigravity 2.18.1 lists the installed exact-address skill as Global in
Settings → Customizations. The user agreed to retire the duplicate install route.
Alternatives considered: Keeping checkout symlinks and a plugin bundle.
Consequences: `skills/link-skills.sh` is removed; existing user links/plugins are
not deleted. Future skills use explicit audited skillstrap installs.


Decision: Use one persistent active directory list for install, list and uninstall.
Reason: Scheduled jobs and other tools need directories outside gh's built-in
agent scan; the user requested commands to list, add and remove paths.
Alternatives considered: Keeping a separate custom-path append list alongside
hardcoded agent installs, which would make default-path removal ineffective.
Consequences: gh `--dir` preserves remote pinned metadata; defaults map the seven
existing tools plus scheduled jobs. The first add/remove saves the complete list,
including default removals. Empty configuration disables installation. Removing
paths never deletes skills; re-add a path to manage skills left there.

Decision: Treat path configuration as private data and preflight installation too.
Reason: User-selected destinations expand the write/removal boundary. Shell
configuration execution, traversal, overlapping roots and parent/target links
could cause unintended writes or deletion.
Alternatives considered: Accepting arbitrary filesystem paths or following links.
Consequences: Only paths beneath HOME; no traversal/control characters or overlaps.
Atomic mode-0600 config writes; all roots checked before writes/deletion, then
rechecked per destination. Existing skill trees with links cannot be overwritten.
Path removal can still disable a registered root that subsequently became a link.

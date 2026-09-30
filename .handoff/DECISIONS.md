# Decisions

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
Consequences: Custom/unknown directories are refused; leaf symlinks can be unlinked.

Decision: Include `antigravity2.0` alongside the older Antigravity and CLI targets.
Reason: gh maps Antigravity 2.0 to `.gemini/config/skills`, while the older target
uses `.gemini/antigravity/skills`. Installation success alone does not prove app discovery.
Alternatives considered: Packaging skills as a plugin; dropping the older target.
Consequences: Seven install targets; uninstall also recognises `.gemini/config/skills`.

Decision: Retire the legacy linker after verifying native app discovery.
Reason: Antigravity 2.18.1 lists the installed exact-address skill as Global in
Settings → Customizations. The user agreed to retire the duplicate install route.
Alternatives considered: Keeping checkout symlinks and a plugin bundle.
Consequences: `skills/link-skills.sh` is removed; existing user links/plugins are
not deleted. Future skills use explicit audited skillstrap installs.

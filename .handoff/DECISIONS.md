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

Decision: Keep the legacy linker.
Reason: It also creates a separate Gemini plugin; absence of repository callers
cannot establish that manual compatibility use has ended.
Alternatives considered: Deleting it as apparently obsolete.
Consequences: README marks it as manual legacy compatibility, outside skillstrap.

# Current

The configurable installation-path request is complete. `29424e8` is pushed on
main and the local `~/.local/bin/skillstrap.sh` was updated with the requested
curl bootstrap, then verified byte-for-byte against the tested source.

`paths [list]`, `paths add <directory>` and `paths remove <directory>` manage a
complete active list in `~/.config/skillstrap/install-paths`. Without that file,
defaults cover the seven existing tool directories plus `~/.scheduled-jobs/skills`.
Install, list and uninstall use the same active list through gh's `--dir` option.
Removing a path leaves its skills in place and excludes it from future operations.
Bootstrap does not install skills or alter saved path configuration.

45 offline tests pass under sh and dash (36 distribution tests and nine isolated
credential-helper tests). Syntax/diff checks pass. Live GitHub CLI 2.101.0 checks
in a temporary HOME verified eight-directory installation, pinned metadata,
listing, add/remove persistence, excluded-path preservation, and custom-path
install/uninstall. The real installed command lists all eight defaults, including
scheduled jobs; existing real skill installations were not changed in this task.

The vision remains distribution from any GitHub repository to every compatible
tool, with safety and security as the primary goals. Keep explicit skill selection,
compact conservative audits, pinned installs and complete destination preflight.
Registered paths must be beneath HOME without traversal or symlinked components;
existing skill trees containing links are refused during overwrite. Sequential
installation can still leave earlier destinations installed if a later gh call fails.
Static audits remain incomplete; no broader security claim is established.

No outstanding requested work. Other repository skills include exact-address,
fine-grained-commits, handoff and the direct dedicated-Keychain mac-login workflow.

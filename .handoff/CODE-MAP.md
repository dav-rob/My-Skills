# Code map

- `skillstrap.sh`: bootstrap, argument checking, clone/validation/static audit,
  pinned seven-target install, exact-name uninstall and list.
- `tests/test_skillstrap.py`: offline CLI regression suite using temporary homes,
  mock commands and real local Git fixtures. `TEST_SHELL` chooses the shell.
- `README.md`: operator commands, audit/deletion limits and verification commands.
- `skills/exact-address/SKILL.md`: canonical renamed address-finding skill.
- `skills/fine-grained-commits/`: commit/push workflow and agent metadata.
- `skills/handoff/SKILL.md`: repository handoff workflow.
- Former `skills/link-skills.sh`: removed in `be59bd2` after native Antigravity 2.0
  discovery was verified; no repository callers depended on it.
- `.handoff/`: project context, kept separate from implementation commits.

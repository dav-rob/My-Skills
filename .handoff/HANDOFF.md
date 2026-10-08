# Handoff

## Current objective

Completed the user's request to include `~/.scheduled-jobs/skills` in skill
installation/uninstallation and add commands to list, add and remove install paths.
Implementation, tests and README are committed and pushed as `29424e8`.

## What was done

Replaced hardcoded agent install calls with configurable gh `--dir` destinations.
The eight defaults preserve the previous seven install locations and add scheduled
jobs. `paths [list]`, `paths add <directory>` and `paths remove <directory>` persist
the full list in `~/.config/skillstrap/install-paths`. Changes don't install/delete
skills; removed paths are excluded from install, list and uninstall.

Paths are normalized beneath HOME; traversal, controls, overlaps and directory
symlinks are refused. Config is read as data and atomically saved with private
permissions. Preflight covers all install destinations and exact-name removals.
Overwrite also refuses links in existing skill trees. Audited remote commit pins,
exact named repository paths and command-only bootstrap are preserved.

## Current state

- 45 tests pass under sh and dash: 36 distribution and nine credential-helper tests.
- `sh -n skillstrap.sh` and `git diff --check` pass.
- Live gh 2.101.0 in a temporary HOME installed exact-address in eight default
  directories with one pinned version, listed skills, persisted path changes,
  preserved an excluded installation, and installed/uninstalled a custom path.
- After pushing, ran the user-requested command:
  `curl -fsSL https://raw.githubusercontent.com/dav-rob/My-Skills/main/skillstrap.sh | sh`.
- Installed `~/.local/bin/skillstrap.sh` matches repository source byte-for-byte;
  `paths` shows eight defaults including `/Users/davidroberts/.scheduled-jobs/skills`,
  and its `list` command succeeds with the scheduled directory included.
- Existing real skill content was not modified; scheduled jobs becomes a default
  destination for the next explicit audited install. No real custom config was needed.

## Important discoveries

Both gh install and gh list support `--dir`; built-in user-scope listing omits
arbitrary locations. Source tracking and pinned metadata are preserved with remote
custom-directory installs. Default Codex placement remains `~/.agents/skills`.

## Problems / blockers

None. Paths outside HOME are unsupported. Static scanning is conservative and
incomplete. A later installation failure may leave earlier destinations installed.
Shell checks reduce link risks but do not claim filesystem race immunity.

## Files currently being worked on

Implementation complete: `skillstrap.sh`, `tests/test_skillstrap.py`, `README.md`.
Handoff documentation is a separate follow-up commit.

## Relevant recent commits

- `29424e8`: configurable install paths, scheduled jobs default, safety checks,
  regression coverage and operator documentation.
- `81dcbc4`: focus mac-login on direct dedicated-Keychain setup.
- `447a0f2`: universal-source/tool distribution vision with security as primary goal.

## Immediate next steps

No outstanding requested work. Inspect current Git state and the handoff before
continuing. Use README verification commands for subsequent implementation changes.

## Things not to do / re-investigate

Do not silently reinstall skills during bootstrap or path registration. Removing a
path leaves its skills in place; re-add it before uninstalling those skills.
Keep custom paths in the same active list as defaults so default removal works.
Do not restore the retired linker or assume CLI placement proves app discovery.

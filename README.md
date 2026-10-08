# My-Skills

The vision is to distribute all skills from any GitHub repository to every tool that
can use them, as safely and securely as possible. Safety and security are the
primary design goals across auditing, installation, updates and removal.

The current implementation is `skillstrap.sh`, a GitHub CLI wrapper supporting
OpenCode, Codex, Claude Code, Cursor, Antigravity, Antigravity 2.0, Antigravity CLI
and scheduled jobs, with configurable installation directories.
This repository also contains a personal skill collection; it is one source
among the repositories the manager can install from. The current target list
and static audit are an initial implementation of the broader vision.

## Bootstrap

```sh
curl -fsSL https://raw.githubusercontent.com/dav-rob/My-Skills/main/skillstrap.sh | sh
```

This installs or updates only `~/.local/bin/skillstrap.sh` and ensures
`export PATH="$HOME/.local/bin:$PATH"` exists in `~/.zshrc`. Repeating it does
not duplicate the PATH line. Open a new shell or run `source ~/.zshrc` afterwards.

## Commands

Skill operations need GitHub CLI with `gh skill` support; audits and installs
also need Git and `gh auth login`. Tested with GitHub CLI 2.101.0.

```sh
skillstrap.sh --dry-run matt-riley/agent-skills grill-me
skillstrap.sh --dry-run dav-rob/My-Skills              # audit all, install none
skillstrap.sh install dav-rob/My-Skills exact-address # install one skill
skillstrap.sh install dav-rob/My-Skills --all         # explicitly install all
skillstrap.sh uninstall "exact address"              # exact legacy name only
skillstrap.sh list
skillstrap.sh paths                                 # list install directories
skillstrap.sh paths add "$HOME/.other-tool/skills"
skillstrap.sh paths remove "$HOME/.other-tool/skills"
```

Every install validates Agent Skills format and runs a conservative static audit
first. Output lists files and reports suspicious patterns by file and line,
without printing skill bodies or untrusted validator diagnostics. Files over
1 MiB, symbolic links, and filenames containing control characters fail the
audit. This scan catches obvious suspicious patterns; it is not complete malware
detection and needs no installed auditor skill.

Installs overwrite the selected skills in every configured directory and pin
them to the audited commit. Named installs use the exact audited repository path.
Rerun an explicit install to audit and install a newer revision. If installation
in one directory fails, the command stops; earlier installations may remain.

## Installation paths

`skillstrap.sh paths` (or `paths list`) prints the active directories, one per line.
The defaults are:

| Tool | Directory |
| --- | --- |
| OpenCode | `~/.config/opencode/skills` |
| Codex | `~/.agents/skills` |
| Claude Code | `~/.claude/skills` |
| Cursor | `~/.cursor/skills` |
| Antigravity | `~/.gemini/antigravity/skills` |
| Antigravity 2.0 | `~/.gemini/config/skills` |
| Antigravity CLI | `~/.gemini/antigravity-cli/skills` |
| Scheduled jobs | `~/.scheduled-jobs/skills` |

`paths add <directory>` and `paths remove <directory>` save the complete active
list in `~/.config/skillstrap/install-paths`. Adding an existing path is harmless.
You can remove default paths as well as custom ones; command updates preserve the
saved list. Adding a path does not install existing skills there. Removing a path
stops future installs, listing and uninstalls there without deleting its contents.
Re-add it to manage any remaining skills. An empty saved list disables installation.
Path commands need no GitHub CLI or authentication and do not create skill roots.

Use absolute paths or quoted `~/...` paths beneath your home directory. Spaces
are supported. Home itself, paths outside home, traversal, control characters,
overlapping directories and symlinked directory components are refused. Choose
directories dedicated to skills. Configuration is read as data, never shell code,
and saved atomically with private permissions.

Installation uses [GitHub CLI's custom-directory option](https://cli.github.com/manual/gh_skill_install)
and validates all destinations before writing. Existing skill trees containing
symlinks are refused rather than followed during overwrite. `list` and uninstall
scan each active directory using [GitHub CLI's directory listing](https://cli.github.com/manual/gh_skill_list),
including locations its default agent scan would miss.

Antigravity 2.0 uses `~/.gemini/config/skills`; the older Antigravity target uses
`~/.gemini/antigravity/skills`, and the CLI uses `~/.gemini/antigravity-cli/skills`.
The `antigravity2.0` target installs plain skills into the newer directory, without
creating a plugin. See [Google's skill locations](https://www.antigravity.google/docs/skills?tab=ide)
and [GitHub CLI's target mappings](https://github.com/cli/cli/blob/v2.101.0/internal/skills/registry/registry.go).

Uninstall uses the exact installed name reported by `gh skill list --dir <directory>`.
It validates every matching path before removing any installation, allows only
configured skill directories beneath the home directory, rejects traversal and
symlinked parents, and removes a leaf symlink without deleting its target.
`exact address` and `exact-address` are separate names. Unconfigured locations
are not scanned or removed.

## CLI skills

Five CLI skills live under `skills/cli/`, with names `cli-codex`, `cli-cursor`,
`cli-claude`, `cli-antigravity` and `cli-opencode`. They cover headless invocation,
model/effort discovery, YOLO options, completion signals, quota/error handling and
caller deadlines. They were researched with OMGSkills and official documentation,
then checked against the installed binaries. See [research and verification](docs/CLI-SKILLS.md)
for the candidates considered and the limits of those checks.

Install these five explicitly:

```sh
for skill in cli-codex cli-cursor cli-claude cli-antigravity cli-opencode; do
  skillstrap.sh install dav-rob/My-Skills "$skill" || break
done
```

Each installs flat as `<configured-directory>/cli-codex/` and so on; the repository's
`skills/cli/` grouping is not reproduced inside install roots. Each copy retains
its exact audited source path and commit pin. CLI availability/authentication is
separate from installing the instructions; these skills do not install binaries
or sign into accounts.

GitHub CLI may display a scoped source identity such as `cli/cli-codex` in its
listing. The installed folder and skill frontmatter name remain `cli-codex`;
use `skillstrap.sh uninstall cli-codex`. Uninstall recognizes that single source
scope while still requiring the exact flat target in a configured directory.

## Checks

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
TEST_SHELL=/bin/dash PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
sh -n skillstrap.sh
```

The regression suite uses temporary homes, mock `gh`/`curl` commands, and local
Git fixtures. It requires Python 3 and Git, and does not modify real installed
skills. Live network checks and real CLI installs were also verified in temporary
homes; they are not part of the offline suite.

## Retired linker

The former `skills/link-skills.sh` was removed after Antigravity 2.18.1 visibly
loaded `exact-address` as a Global skill from `~/.gemini/config/skills`. Plugins
and checkout symlinks are unnecessary for this installation route.

The linker exposed every skill in a local checkout through individual symlinks in
`~/.agents/skills` and `~/.gemini/config/plugins/My-Skills/skills`, and created a
minimal `plugin.json`. It did not audit content or maintain existing/stale links;
checkout edits became visible immediately. Use explicit `skillstrap.sh` installs
instead. Removing the script does not remove any existing links or plugin files.

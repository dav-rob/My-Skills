# My-Skills

Personal Agent Skills and a small GitHub CLI wrapper for distributing them to
OpenCode, Codex, Claude Code, Cursor, Antigravity and Antigravity CLI.

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
```

Every install validates Agent Skills format and runs a conservative static audit
first. Output lists files and reports suspicious patterns by file and line,
without printing skill bodies or untrusted validator diagnostics. Files over
1 MiB, symbolic links, and filenames containing control characters fail the
audit. This scan catches obvious suspicious patterns; it is not complete malware
detection and needs no installed auditor skill.

Installs overwrite the selected skills at user scope for all six agents and pin
them to the audited commit. Named installs use the exact audited repository path.
Rerun an explicit install to audit and install a newer revision. If an agent's
install fails, the command stops; installations for earlier agents may remain.

Uninstall uses the exact installed name reported by `gh skill list --scope user`.
It validates every matching path before removing any installation, allows only
recognised skill directories beneath the home directory, rejects traversal and
symlinked parents, and removes a leaf symlink without deleting its target.
`exact address` and `exact-address` are separate names. Unknown/custom locations
are refused rather than deleted.

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

## Legacy linker

`skills/link-skills.sh` remains for manual compatibility. It symlinks a local
checkout into `~/.agents/skills` and builds a Gemini plugin under
`~/.gemini/config/plugins/My-Skills`. There are no repository callers and
`skillstrap.sh` does not invoke it. Its plugin creation is separate from current
`gh skill` installation, so it has been retained. Use `skillstrap.sh` for current
audited distribution.

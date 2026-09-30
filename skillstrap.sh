#!/bin/sh
set -eu

REPO_DEFAULT="dav-rob/My-Skills"
SELF_URL="https://raw.githubusercontent.com/dav-rob/My-Skills/main/skillstrap.sh"
BIN_DIR="$HOME/.local/bin"
BIN_PATH="$BIN_DIR/skillstrap.sh"
ZSHRC="$HOME/.zshrc"
AGENTS="opencode codex claude-code cursor antigravity antigravity-cli"

say() {
  printf '%s\n' "$*"
}

fail() {
  printf 'skillstrap: %s\n' "$*" >&2
  exit 1
}

usage() {
  cat <<'USAGE'
Usage:
  skillstrap.sh
  skillstrap.sh --dry-run <owner/repo> [skill|--all]
  skillstrap.sh install <owner/repo> <skill|--all>
  skillstrap.sh uninstall <skill>
  skillstrap.sh list
  skillstrap.sh help

No arguments installs/updates only the skillstrap.sh command itself and ensures
~/.local/bin is on PATH. It never installs skills implicitly.

--dry-run audits without installing.
install audits first, then installs the named skill (or --all) for OpenCode,
Codex, Claude Code, Cursor, Antigravity and Antigravity CLI at user scope.
uninstall removes every user-scope installation with that exact skill name.
USAGE
}

need() {
  command -v "$1" >/dev/null 2>&1 || fail "required command not found: $1"
}

check_gh_skill() {
  need gh
  if ! gh skill --help >/dev/null 2>&1; then
    fail "this GitHub CLI does not support 'gh skill'; upgrade gh first"
  fi
}

ensure_gh_auth() {
  if ! gh auth status >/dev/null 2>&1; then
    fail "GitHub CLI is not authenticated; run: gh auth login"
  fi
}

install_self() {
  need curl
  mkdir -p "$BIN_DIR"

  tmp_self="$(mktemp "${TMPDIR:-/tmp}/skillstrap.XXXXXX")"
  if ! curl -fsSL "$SELF_URL" -o "$tmp_self"; then
    rm -f "$tmp_self"
    fail "could not download $SELF_URL"
  fi
  chmod 0755 "$tmp_self"
  mv "$tmp_self" "$BIN_PATH"

  touch "$ZSHRC"
  if ! grep -Fq '# >>> skillstrap >>>' "$ZSHRC"; then
    cat >> "$ZSHRC" <<'EOF_PATH'

# >>> skillstrap >>>
export PATH="$HOME/.local/bin:$PATH"
# <<< skillstrap <<<
EOF_PATH
  fi

  case ":$PATH:" in
    *":$BIN_DIR:"*) : ;;
    *) PATH="$BIN_DIR:$PATH"; export PATH ;;
  esac

  say "Installed skillstrap.sh -> $BIN_PATH"
  say "No skills were installed."
  say ""
  say "Open a new shell, or run:"
  say "  source ~/.zshrc"
  say ""
  say "Examples:"
  say "  skillstrap.sh --dry-run $REPO_DEFAULT"
  say "  skillstrap.sh install $REPO_DEFAULT exact-address"
  say "  skillstrap.sh install $REPO_DEFAULT --all"
}

clone_repo() {
  repo="$1"
  dest="$2"
  gh repo clone "$repo" "$dest" -- --depth 1 >/dev/null
}

find_skill_dir() {
  root="$1"
  wanted="$2"

  find "$root" -type f -name SKILL.md -not -path '*/.git/*' | while IFS= read -r f; do
    name="$(awk '
      BEGIN { fm=0 }
      NR == 1 && $0 == "---" { fm=1; next }
      fm && $0 == "---" { exit }
      fm && $0 ~ /^name:[[:space:]]*/ {
        sub(/^name:[[:space:]]*/, "", $0)
        gsub(/^['\''\"]|['\''\"]$/, "", $0)
        print $0
        exit
      }
    ' "$f")"
    if [ "$name" = "$wanted" ]; then
      dirname "$f"
      exit 0
    fi
  done
}

scan_dir() {
  root="$1"
  findings=0

  say "Static safety scan: $root"

  symlinks="$(find "$root" -type l -not -path '*/.git/*' -print 2>/dev/null || true)"
  if [ -n "$symlinks" ]; then
    say "[review] symbolic links found:"
    printf '%s\n' "$symlinks"
    findings=1
  fi

  pattern='(curl|wget).*[|][[:space:]]*(sh|bash|zsh|python([0-9.]+)?|perl|ruby)|(^|[[:space:]])(sudo|doas)[[:space:]]|rm[[:space:]]+-[^[:space:]]*r[^[:space:]]*f[[:space:]]+(/|~|\$HOME)|(^|[/[:space:]"'\''`])\.(ssh|aws|gnupg)([/[:space:]"'\''`]|$)|security[[:space:]]+find-(generic|internet)-password|(^|[[:space:]])(printenv|env)[[:space:]]*([|>]|$)|base64[[:space:]]+(-d|--decode)|(^|[[:space:]])eval[[:space:]]|(^|[[:space:]])crontab[[:space:]]|LaunchAgents|LaunchDaemons|\.ssh/authorized_keys|\.zshrc|\.bashrc|\.profile'

  while IFS= read -r file; do
    [ -f "$file" ] || continue
    size="$(wc -c < "$file" | tr -d ' ')"
    [ "$size" -le 1048576 ] || continue

    matches="$(grep -nEi "$pattern" "$file" 2>/dev/null || true)"
    if [ -n "$matches" ]; then
      say "[review] $file"
      printf '%s\n' "$matches"
      findings=1
    fi
  done <<EOF_FILES
$(find "$root" -type f -not -path '*/.git/*' -print)
EOF_FILES

  if [ "$findings" -ne 0 ]; then
    say "Safety scan: REVIEW REQUIRED"
    return 2
  fi

  say "Safety scan: no flagged patterns"
  return 0
}

scan_all_skills() {
  root="$1"
  skill_files="$(find "$root" -type f -name SKILL.md -not -path '*/.git/*' -print)"
  [ -n "$skill_files" ] || fail "no SKILL.md files found"

  rc=0
  while IFS= read -r skill_file; do
    scan_dir "$(dirname "$skill_file")" || rc=$?
  done <<EOF_SKILLS
$skill_files
EOF_SKILLS
  return "$rc"
}

validate_repo_or_skill() {
  clone="$1"
  skill="${2:-}"

  if [ -z "$skill" ] || [ "$skill" = "--all" ]; then
    say "Agent Skills validation: repository"
    gh skill publish "$clone" --dry-run
    scan_all_skills "$clone"
    return $?
  fi

  skill_dir="$(find_skill_dir "$clone" "$skill")"
  [ -n "$skill_dir" ] || fail "skill '$skill' not found in cloned repository"

  tmp_validate="$(mktemp -d "${TMPDIR:-/tmp}/skillstrap-validate.XXXXXX")"
  mkdir -p "$tmp_validate/skills/$skill"
  cp -R "$skill_dir"/. "$tmp_validate/skills/$skill"/

  say "Agent Skills validation: $skill"
  if ! gh skill publish "$tmp_validate" --dry-run; then
    rm -rf "$tmp_validate"
    return 1
  fi
  rm -rf "$tmp_validate"

  scan_dir "$skill_dir"
}

audit() {
  repo="$1"
  skill="${2:-}"

  tmp="$(mktemp -d "${TMPDIR:-/tmp}/skillstrap-repo.XXXXXX")"
  trap 'rm -rf "$tmp"' EXIT HUP INT TERM

  say "Fetching $repo"
  clone_repo "$repo" "$tmp/repo"

  rc=0
  validate_repo_or_skill "$tmp/repo" "$skill" || rc=$?

  if [ -n "$skill" ] && [ "$skill" != "--all" ]; then
    say "Preview: $repo / $skill"
    GH_PROMPT_DISABLED=1 GH_PAGER=cat gh skill preview "$repo" "$skill" || rc=$?
  else
    say "Available skills: $repo"
    GH_PROMPT_DISABLED=1 gh skill install "$repo" | sed -n '1,80p' || true
  fi

  rm -rf "$tmp"
  trap - EXIT HUP INT TERM
  return "$rc"
}

install_for_agents() {
  repo="$1"
  skill="$2"

  for agent in $AGENTS; do
    say "Installing for $agent"
    if [ "$skill" = "--all" ]; then
      gh skill install "$repo" --all --agent "$agent" --scope user --force
    else
      gh skill install "$repo" "$skill" --agent "$agent" --scope user --force
    fi
  done
}

safe_user_skill_path() {
  skill="$1"
  path="$2"

  case "$path" in
    "$HOME"/*) abs="$path" ;;
    "~/"*) abs="$HOME/${path#~/}" ;;
    /*) return 1 ;;
    *) abs="$HOME/${path#./}" ;;
  esac

  [ "$(basename "$abs")" = "$skill" ] || return 1
  case "$abs" in
    "$HOME"/*/skills/*) printf '%s\n' "$abs" ;;
    *) return 1 ;;
  esac
}

uninstall_skill() {
  skill="$1"
  check_gh_skill

  rows="$(mktemp "${TMPDIR:-/tmp}/skillstrap-list.XXXXXX")"
  seen="$(mktemp "${TMPDIR:-/tmp}/skillstrap-seen.XXXXXX")"
  trap 'rm -f "$rows" "$seen"' EXIT HUP INT TERM

  gh skill list --scope user \
    --json skillName,path,sourceURL \
    --template '{{range .}}{{printf "%s\t%s\t%s\n" .skillName .path .sourceURL}}{{end}}' \
    > "$rows"

  found=0
  while IFS="$(printf '\t')" read -r name path source; do
    [ "$name" = "$skill" ] || continue

    abs="$(safe_user_skill_path "$skill" "$path" || true)"
    [ -n "$abs" ] || fail "refusing unsafe uninstall path reported by gh: $path"

    if grep -Fqx "$abs" "$seen" 2>/dev/null; then
      continue
    fi
    printf '%s\n' "$abs" >> "$seen"

    say "Removing $skill"
    say "  $abs"
    [ -n "$source" ] && say "  source: $source"

    if [ -L "$abs" ] || [ -f "$abs" ]; then
      rm -f "$abs"
    elif [ -d "$abs" ]; then
      rm -rf "$abs"
    fi
    found=1
  done < "$rows"

  rm -f "$rows" "$seen"
  trap - EXIT HUP INT TERM

  if [ "$found" -eq 0 ]; then
    fail "no user-scope skill named '$skill' is installed"
  fi

  say "Uninstalled '$skill'."
}

case "${1:-}" in
  "")
    install_self
    ;;
  --dry-run)
    [ "$#" -ge 2 ] && [ "$#" -le 3 ] || fail "usage: skillstrap.sh --dry-run <owner/repo> [skill|--all]"
    check_gh_skill
    ensure_gh_auth
    audit "$2" "${3:-}"
    ;;
  install)
    [ "$#" -eq 3 ] || fail "usage: skillstrap.sh install <owner/repo> <skill|--all>"
    check_gh_skill
    ensure_gh_auth
    if audit "$2" "$3"; then
      install_for_agents "$2" "$3"
    else
      fail "audit failed; nothing was installed"
    fi
    ;;
  uninstall)
    [ "$#" -eq 2 ] || fail "usage: skillstrap.sh uninstall <skill>"
    uninstall_skill "$2"
    ;;
  list)
    check_gh_skill
    gh skill list --scope user
    ;;
  help|-h|--help)
    usage
    ;;
  *)
    usage >&2
    exit 1
    ;;
esac

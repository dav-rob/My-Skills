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

install_self() (
  need curl
  mkdir -p "$BIN_DIR"

  tmp_self="$(mktemp "$BIN_DIR/.skillstrap.XXXXXX")"
  trap 'rm -f "$tmp_self"' 0
  trap 'exit 1' HUP INT TERM
  if ! curl -fsSL "$SELF_URL" -o "$tmp_self"; then
    rm -f "$tmp_self"
    fail "could not download $SELF_URL"
  fi
  sh -n "$tmp_self" || fail "downloaded command is not valid shell syntax"
  chmod 0755 "$tmp_self"
  mv "$tmp_self" "$BIN_PATH"

  touch "$ZSHRC"
  if ! grep -Fqx 'export PATH="$HOME/.local/bin:$PATH"' "$ZSHRC"; then
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
)

clone_repo() {
  repo="$1"
  dest="$2"
  gh repo clone "$repo" "$dest" -- --depth 1 >/dev/null 2>&1
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

list_checked_files() {
  root="$1"

  find "$root" -type f -not -path '*/.git/*' -print | while IFS= read -r file; do
    rel="${file#"$root"/}"
    say "  $rel"
  done
}

append_validation_reasons() {
  log="$1"
  reasons="$2"

  matches="$(grep -Ei '(error|invalid|failed|failure|required|missing)' "$log" 2>/dev/null | sed -n '1,5p' || true)"
  if [ -z "$matches" ]; then
    matches="$(sed -n '1,5p' "$log")"
  fi

  while IFS= read -r line; do
    [ -n "$line" ] || continue
    printf '%s\n' "validator: $line" >> "$reasons"
  done <<EOF_VALIDATION
$matches
EOF_VALIDATION
}

scan_dir() {
  root="$1"
  reasons="$2"
  findings=0

  symlinks="$(find "$root" -type l -not -path '*/.git/*' -print 2>/dev/null || true)"
  if [ -n "$symlinks" ]; then
    while IFS= read -r link; do
      [ -n "$link" ] || continue
      rel="${link#"$root"/}"
      printf '%s\n' "symbolic link: $rel" >> "$reasons"
    done <<EOF_SYMLINKS
$symlinks
EOF_SYMLINKS
    findings=1
  fi

  pattern='(curl|wget).*[|][[:space:]]*(sh|bash|zsh|python([0-9.]+)?|perl|ruby)|(^|[[:space:]])(sudo|doas)[[:space:]]|rm[[:space:]]+-[^[:space:]]*r[^[:space:]]*f[[:space:]]+(/|~|\$HOME)|(^|[/[:space:]"'\''`])\.(ssh|aws|gnupg)([/[:space:]"'\''`]|$)|security[[:space:]]+find-(generic|internet)-password|(^|[[:space:]])(printenv|env)[[:space:]]*([|>]|$)|base64[[:space:]]+(-d|--decode)|(^|[[:space:]])eval[[:space:]]|(^|[[:space:]])crontab[[:space:]]|LaunchAgents|LaunchDaemons|\.ssh/authorized_keys|\.zshrc|\.bashrc|\.profile'

  while IFS= read -r file; do
    [ -f "$file" ] || continue
    size="$(wc -c < "$file" | tr -d ' ')"
    [ "$size" -le 1048576 ] || continue

    first_match="$(grep -nEi "$pattern" "$file" 2>/dev/null | sed -n '1p' || true)"
    if [ -n "$first_match" ]; then
      line="${first_match%%:*}"
      rel="${file#"$root"/}"
      printf '%s\n' "suspicious pattern: $rel:$line" >> "$reasons"
      findings=1
    fi
  done <<EOF_FILES
$(find "$root" -type f -not -path '*/.git/*' -print)
EOF_FILES

  [ "$findings" -eq 0 ]
}

scan_all_skills() {
  root="$1"
  reasons="$2"
  skill_files="$(find "$root" -type f -name SKILL.md -not -path '*/.git/*' -print)"
  [ -n "$skill_files" ] || {
    printf '%s\n' "no SKILL.md files found" >> "$reasons"
    return 1
  }

  rc=0
  while IFS= read -r skill_file; do
    scan_dir "$(dirname "$skill_file")" "$reasons" || rc=1
  done <<EOF_SKILLS
$skill_files
EOF_SKILLS
  return "$rc"
}

list_all_skill_files() {
  root="$1"
  skill_files="$(find "$root" -type f -name SKILL.md -not -path '*/.git/*' -print)"

  while IFS= read -r skill_file; do
    [ -n "$skill_file" ] || continue
    skill_dir="$(dirname "$skill_file")"
    skill_name="$(basename "$skill_dir")"
    say "  [$skill_name]"
    find "$skill_dir" -type f -not -path '*/.git/*' -print | while IFS= read -r file; do
      rel="${file#"$skill_dir"/}"
      say "    $rel"
    done
  done <<EOF_SKILLS
$skill_files
EOF_SKILLS
}

validate_repo_or_skill() {
  clone="$1"
  skill="${2:-}"
  reasons="$3"
  rc=0
  validation_log="$(mktemp "${TMPDIR:-/tmp}/skillstrap-validation.XXXXXX")"

  if [ -z "$skill" ] || [ "$skill" = "--all" ]; then
    say "Files checked:"
    list_all_skill_files "$clone"

    if gh skill publish "$clone" --dry-run >"$validation_log" 2>&1; then
      say "  PASS  Agent Skills format"
    else
      say "  FAIL  Agent Skills format"
      append_validation_reasons "$validation_log" "$reasons"
      rc=1
    fi

    if scan_all_skills "$clone" "$reasons"; then
      say "  PASS  static safety scan"
    else
      say "  FAIL  static safety scan"
      rc=1
    fi

    rm -f "$validation_log"
    return "$rc"
  fi

  skill_dir="$(find_skill_dir "$clone" "$skill")"
  if [ -z "$skill_dir" ]; then
    printf '%s\n' "skill '$skill' not found in repository" >> "$reasons"
    say "  FAIL  locate skill"
    rm -f "$validation_log"
    return 1
  fi

  say "Files checked:"
  list_checked_files "$skill_dir"

  tmp_validate="$(mktemp -d "${TMPDIR:-/tmp}/skillstrap-validate.XXXXXX")"
  mkdir -p "$tmp_validate/skills/$skill"
  cp -R "$skill_dir"/. "$tmp_validate/skills/$skill"/

  if gh skill publish "$tmp_validate" --dry-run >"$validation_log" 2>&1; then
    say "  PASS  Agent Skills format"
  else
    say "  FAIL  Agent Skills format"
    append_validation_reasons "$validation_log" "$reasons"
    rc=1
  fi

  if scan_dir "$skill_dir" "$reasons"; then
    say "  PASS  static safety scan"
  else
    say "  FAIL  static safety scan"
    rc=1
  fi

  rm -rf "$tmp_validate"
  rm -f "$validation_log"
  return "$rc"
}

audit() {
  repo="$1"
  skill="${2:-}"

  tmp="$(mktemp -d "${TMPDIR:-/tmp}/skillstrap-repo.XXXXXX")"
  reasons="$(mktemp "${TMPDIR:-/tmp}/skillstrap-reasons.XXXXXX")"
  trap 'rm -rf "$tmp"; rm -f "$reasons"' EXIT HUP INT TERM

  if [ -n "$skill" ] && [ "$skill" != "--all" ]; then
    say "Audit: $repo / $skill"
  else
    say "Audit: $repo / all skills"
  fi

  if ! clone_repo "$repo" "$tmp/repo"; then
    printf '%s\n' "could not fetch repository" >> "$reasons"
    rc=1
  else
    rc=0
    validate_repo_or_skill "$tmp/repo" "$skill" "$reasons" || rc=$?
  fi

  say ""
  if [ "$rc" -eq 0 ]; then
    say "Audit result: PASS"
    say "  No flagged patterns found."
  else
    say "Audit result: FAIL"
    say "Reasons:"
    sed 's/^/  - /' "$reasons"
  fi

  rm -rf "$tmp"
  rm -f "$reasons"
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
    [ "$#" -eq 0 ] || fail "empty command; use help for usage"
    install_self
    ;;
  --dry-run)
    [ "$#" -ge 2 ] && [ "$#" -le 3 ] || fail "usage: skillstrap.sh --dry-run <owner/repo> [skill|--all]"
    check_gh_skill
    ensure_gh_auth
    if audit "$2" "${3:-}"; then
      say "Dry run only: nothing installed."
    else
      say "Dry run only: nothing installed."
      exit 1
    fi
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
    [ "$#" -eq 1 ] || fail "usage: skillstrap.sh list"
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

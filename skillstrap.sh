#!/bin/sh
set -eu

REPO_DEFAULT="dav-rob/My-Skills"
SELF_URL="https://raw.githubusercontent.com/dav-rob/My-Skills/main/skillstrap.sh"
BIN_DIR="$HOME/.local/bin"
BIN_PATH="$BIN_DIR/skillstrap.sh"
ZSHRC="$HOME/.zshrc"
AGENTS="opencode codex claude-code cursor antigravity antigravity-cli"
GH_PROMPT_DISABLED=1
GH_PAGER=cat
export GH_PROMPT_DISABLED GH_PAGER

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

clone_repo() (
  repo="$1"
  dest="$2"
  gh repo clone "$repo" "$dest" -- --depth 1 >/dev/null 2>&1
)

find_skill_dir() (
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
    fi
  done
)

list_checked_files() (
  root="$1"

  find "$root" -type f -print | LC_ALL=C sort | while IFS= read -r file; do
    rel="${file#"$root"/}"
    say "  $rel"
  done
)

append_validation_reasons() {
  # Validator diagnostics may echo untrusted frontmatter. Keep them private.
  printf '%s\n' "Agent Skills validation failed (check SKILL.md name, directory and required frontmatter)" >> "$2"
}

check_audit_args() {
  case "$1" in
    */*) : ;;
    *) fail "repository must be owner/repo" ;;
  esac
  owner="${1%%/*}"
  repository="${1#*/}"
  case "$owner/$repository" in
    *[!a-zA-Z0-9_./-]*|/*|*/|*/*/*|-*|*/-*) fail "repository must be owner/repo" ;;
  esac
  case "$2" in
    ""|--all) return 0 ;;
    *[!a-z0-9-]*|-*|*-|*--*) fail "skill must be a plain Agent Skills name or --all" ;;
  esac
  [ "${#2}" -le 64 ] || fail "skill name is too long"
}

check_filenames() (
  # Newlines break line-based inventories; controls can spoof terminal output.
  invalid="$(find "$1" -path "$1/.git" -prune -o -exec sh -c '
    for file do
      case "$file" in
        *"
"*) printf "invalid\n"; continue ;;
      esac
      if printf "%s" "$file" | LC_ALL=C grep -q "[[:cntrl:]]"; then
        printf "invalid\n"
      fi
    done
  ' sh {} +)" || return 1
  [ -z "$invalid" ]
)

scan_dir() (
  root="$1"
  reasons="$2"
  findings=0

  symlinks="$(find "$root" -type l -print)" || return 1
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

  pattern='(curl|wget).*[|][[:space:]]*(sh|bash|zsh|python([0-9.]+)?|perl|ruby)|(^|[[:space:]])(sudo|doas)[[:space:]]|rm[[:space:]]+(-[^[:space:]]+[[:space:]]+)+["'\'']*(/|~|\$HOME|\$\{HOME\})|(^|[/[:space:]"'\''`])\.(ssh|aws|gnupg)([/[:space:]"'\''`]|$)|security[[:space:]]+find-(generic|internet)-password|(^|[[:space:]])(printenv|env)[[:space:]]*([|>]|$)|base64[[:space:]]+(-d|-D|--decode)|(^|[[:space:]])eval[[:space:]]|(^|[[:space:]])crontab[[:space:]]|LaunchAgents|LaunchDaemons|\.ssh/authorized_keys|\.zshrc|\.bashrc|\.profile'

  while IFS= read -r file; do
    [ -f "$file" ] || continue
    size="$(wc -c < "$file")" || return 1
    rel="${file#"$root"/}"
    if [ "$size" -gt 1048576 ]; then
      printf '%s\n' "file too large to scan: $rel" >> "$reasons"
      findings=1
      continue
    fi

    # Force text mode for embedded NULs; distinguish no match from scan errors.
    grep_rc=0
    matches="$(LC_ALL=C grep -anEim 1 "$pattern" "$file" 2>/dev/null)" || grep_rc=$?
    if [ "$grep_rc" -gt 1 ]; then
      printf '%s\n' "could not scan file: $rel" >> "$reasons"
      findings=1
      continue
    fi
    first_match="$(printf '%s\n' "$matches" | sed -n '1p')"
    if [ -n "$first_match" ]; then
      line="${first_match%%:*}"
      rel="${file#"$root"/}"
      printf '%s\n' "suspicious pattern: $rel:$line" >> "$reasons"
      findings=1
    fi
  done <<EOF_FILES
$(find "$root" -type f -print | LC_ALL=C sort)
EOF_FILES

  [ "$findings" -eq 0 ]
)

scan_all_skills() (
  root="$1"
  reasons="$2"
  skill_files="$(find "$root" -type f -name SKILL.md -not -path '*/.git/*' -print)"
  [ -n "$skill_files" ] || {
    printf '%s\n' "no SKILL.md files found" >> "$reasons"
    return 1
  }

  rc=0
  # A linked skill directory or SKILL.md is invisible to find -type f.
  symlinks="$(find "$root" -path "$root/.git" -prune -o -type l -print)" || return 1
  if [ -n "$symlinks" ]; then
    while IFS= read -r link; do
      printf '%s\n' "symbolic link: ${link#"$root"/}" >> "$reasons"
    done <<EOF_LINKS
$symlinks
EOF_LINKS
    rc=1
  fi
  while IFS= read -r skill_file; do
    scan_dir "$(dirname "$skill_file")" "$reasons" || rc=1
  done <<EOF_SKILLS
$skill_files
EOF_SKILLS
  return "$rc"
)

list_all_skill_files() (
  root="$1"
  skill_files="$(find "$root" -type f -name SKILL.md -not -path '*/.git/*' -print)"

  while IFS= read -r skill_file; do
    [ -n "$skill_file" ] || continue
    skill_dir="$(dirname "$skill_file")"
    skill_name="$(basename "$skill_dir")"
    say "  [$skill_name]"
    find "$skill_dir" -type f -print | LC_ALL=C sort | while IFS= read -r file; do
      rel="${file#"$skill_dir"/}"
      say "    $rel"
    done
  done <<EOF_SKILLS
$skill_files
EOF_SKILLS
)

validate_repo_or_skill() (
  clone="$1"
  skill="${2:-}"
  reasons="$3"
  rc=0
  validation_log="$clone/../validation.log"

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

  skill_dir="$(find_skill_dir "$clone" "$skill")" || return 1
  case "$skill_dir" in
    *'
'*) printf '%s\n' "ambiguous skill name: $skill" >> "$reasons"; return 1 ;;
  esac
  if [ -z "$skill_dir" ]; then
    printf '%s\n' "skill '$skill' not found in repository" >> "$reasons"
    say "  FAIL  locate skill"
    rm -f "$validation_log"
    return 1
  fi

  if [ "$(basename "$skill_dir")" != "$skill" ]; then
    printf '%s\n' "skill name does not match directory: ${skill_dir#"$clone"/}" >> "$reasons"
    return 1
  fi
  printf '%s\n' "${skill_dir#"$clone"/}/SKILL.md" > "$clone/../selected-skill"
  say "Files checked:"
  list_checked_files "$skill_dir"

  tmp_validate="$clone/../validate"
  mkdir -p "$tmp_validate/skills/$skill" || return 1
  cp -R "$skill_dir"/. "$tmp_validate/skills/$skill"/ || return 1

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
)

audit() (
  repo="$1"
  skill="${2:-}"
  mode="${3:-audit}"

  tmp="$(mktemp -d "${TMPDIR:-/tmp}/skillstrap-repo.XXXXXX")" || fail "could not create audit directory"
  reasons="$tmp/reasons"
  trap 'rm -rf "$tmp"' 0
  trap 'exit 1' HUP INT TERM
  : > "$reasons" || fail "could not create audit log"

  if [ -n "$skill" ] && [ "$skill" != "--all" ]; then
    say "Audit: $repo / $skill"
  else
    say "Audit: $repo / all skills"
  fi

  if ! clone_repo "$repo" "$tmp/repo"; then
    printf '%s\n' "could not fetch repository" >> "$reasons"
    rc=1
  elif ! check_filenames "$tmp/repo"; then
    printf '%s\n' "could not inventory repository or filename contains control characters" >> "$reasons"
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
    [ -s "$reasons" ] || printf '%s\n' "could not complete audit" >> "$reasons"
    sed 's/^/  - /' "$reasons"
  fi

  if [ "$rc" -eq 0 ] && [ "$mode" = install ]; then
    commit="$(git -C "$tmp/repo" rev-parse HEAD)" || fail "could not identify audited commit"
    if [ "$skill" = --all ]; then
      selection=--all
    else
      selection="$(cat "$tmp/selected-skill")" || fail "could not identify audited skill"
    fi
    install_for_agents "$repo" "$selection" "$commit" || return 1
  fi
  return "$rc"
)

install_for_agents() (
  repo="$1"
  skill="$2"
  commit="$3"

  for agent in $AGENTS; do
    say "Installing for $agent"
    if [ "$skill" = "--all" ]; then
      gh skill install "$repo" --all --pin "$commit" --agent "$agent" --scope user --force || fail "installation failed for $agent; earlier agents may already be installed"
    else
      gh skill install "$repo" "$skill" --pin "$commit" --agent "$agent" --scope user --force || fail "installation failed for $agent; earlier agents may already be installed"
    fi
  done
)

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
    check_audit_args "$2" "${3:-}"
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
    [ -n "$3" ] || fail "install requires a skill name or --all"
    check_audit_args "$2" "$3"
    need git
    check_gh_skill
    ensure_gh_auth
    audit "$2" "$3" install || exit 1
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

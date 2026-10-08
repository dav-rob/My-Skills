#!/bin/sh
set -eu

REPO_DEFAULT="dav-rob/My-Skills"
SELF_URL="https://raw.githubusercontent.com/dav-rob/My-Skills/main/skillstrap.sh"
BIN_DIR="$HOME/.local/bin"
BIN_PATH="$BIN_DIR/skillstrap.sh"
ZSHRC="$HOME/.zshrc"
PATHS_FILE="$HOME/.config/skillstrap/install-paths"
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
  skillstrap.sh paths [list]
  skillstrap.sh paths add <directory>
  skillstrap.sh paths remove <directory>
  skillstrap.sh help

No arguments installs/updates only the skillstrap.sh command itself and ensures
~/.local/bin is on PATH. It never installs skills implicitly.

--dry-run audits without installing.
install audits first, then installs the named skill (or --all) in each configured
directory. Defaults cover seven agents plus ~/.scheduled-jobs/skills.
uninstall removes installations with that exact name in configured directories.
list includes skills in configured directories.
paths lists, adds or removes install directories beneath HOME. Changes persist in
~/.config/skillstrap/install-paths. Removing a path does not delete its contents.
USAGE
}

default_install_paths() {
  for directory in .config/opencode/skills .agents/skills .claude/skills \
    .cursor/skills .gemini/antigravity/skills .gemini/config/skills \
    .gemini/antigravity-cli/skills .scheduled-jobs/skills; do
    printf '%s\n' "$HOME/$directory"
  done
}

normalize_install_path() (
  path="$1"
  case "$path" in
    *'
'*) return 1 ;;
  esac
  if printf '%s' "$path" | LC_ALL=C grep -q '[[:cntrl:]]'; then
    return 1
  fi
  home_real="$(cd "$HOME" && pwd -P)" || return 1
  [ "$home_real" != / ] || return 1
  path="${path%/}"
  case "$path" in
    "$HOME"/*) relative="${path#"$HOME"/}" ;;
    "$home_real"/*) relative="${path#"$home_real"/}" ;;
    '~/'*) relative="${path#'~/'}" ;;
    *) return 1 ;;
  esac
  case "/$relative/" in
    *'/../'*|*'/./'*|*'//'*) return 1 ;;
  esac
  [ -n "$relative" ] || return 1
  printf '%s\n' "$HOME/$relative"
)

check_install_directory() (
  path="$(normalize_install_path "$1")" || return 1
  relative="${path#"$HOME"/}"
  current="$HOME"
  # Check each existing component, including the root itself. Missing directories
  # are allowed; installation creates them only after the audit passes.
  while [ -n "$relative" ]; do
    component="${relative%%/*}"
    current="$current/$component"
    [ ! -L "$current" ] || return 1
    if [ -e "$current" ]; then
      [ -d "$current" ] || return 1
    fi
    case "$relative" in
      */*) relative="${relative#*/}" ;;
      *) relative="" ;;
    esac
  done
)

read_install_paths() (
  check_install_directory "${PATHS_FILE%/*}" || fail "unsafe install-path configuration directory"
  [ ! -L "$PATHS_FILE" ] || fail "install-path configuration must not be a symbolic link"
  if [ ! -e "$PATHS_FILE" ]; then
    default_install_paths
    exit
  fi
  [ -f "$PATHS_FILE" ] && [ -r "$PATHS_FILE" ] || fail "could not read install-path configuration"
  controls_rc=0
  LC_ALL=C grep -aq '[[:cntrl:]]' "$PATHS_FILE" || controls_rc=$?
  [ "$controls_rc" -eq 1 ] || fail "could not read install-path configuration or it contains control characters"
  paths=""
  while IFS= read -r entry || [ -n "$entry" ]; do
    path="$(normalize_install_path "$entry")" || fail "invalid configured install path"
    while IFS= read -r existing; do
      [ -n "$existing" ] || continue
      case "$path/" in "$existing/"*) fail "duplicate or overlapping install paths" ;; esac
      case "$existing/" in "$path/"*) fail "overlapping install paths" ;; esac
    done <<EOF_EXISTING_PATHS
$paths
EOF_EXISTING_PATHS
    paths="${paths}${paths:+
}$path"
  done < "$PATHS_FILE"
  [ -z "$paths" ] || printf '%s\n' "$paths"
)

manage_paths() (
  action="$1"
  paths="$(read_install_paths)" || exit 1
  if [ "$action" = list ]; then
    [ -z "$paths" ] || printf '%s\n' "$paths"
    exit
  fi
  path="$(normalize_install_path "$2")" || fail "install path must be a directory beneath HOME without traversal or control characters"
  updated=""
  found=0
  while IFS= read -r existing; do
    [ -n "$existing" ] || continue
    if [ "$existing" = "$path" ]; then
      found=1
      [ "$action" != remove ] || continue
    elif [ "$action" = add ]; then
      case "$path/" in "$existing/"*) fail "install paths must not overlap" ;; esac
      case "$existing/" in "$path/"*) fail "install paths must not overlap" ;; esac
    fi
    updated="${updated}${updated:+
}$existing"
  done <<EOF_PATHS
$paths
EOF_PATHS
  if [ "$action" = add ]; then
    check_install_directory "$path" || fail "install path has a symbolic link or non-directory component"
    if [ "$found" -eq 1 ]; then
      say "Install path already configured: $path"
      exit
    fi
    updated="${updated}${updated:+
}$path"
  else
    [ "$found" -eq 1 ] || fail "install path is not configured"
  fi
  umask 077
  mkdir -p "${PATHS_FILE%/*}"
  tmp_paths="$(mktemp "${PATHS_FILE%/*}/.install-paths.XXXXXX")"
  trap 'rm -f "$tmp_paths"' 0
  trap 'exit 1' HUP INT TERM
  [ -z "$updated" ] || printf '%s\n' "$updated" > "$tmp_paths"
  mv "$tmp_paths" "$PATHS_FILE"
  case "$action" in
    add) say "Added install path: $path" ;;
    remove) say "Removed install path: $path" ;;
  esac
  say "Existing skills were not changed."
)

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
    install_for_paths "$repo" "$selection" "$commit" "$tmp/repo" || return 1
  fi
  return "$rc"
)

check_install_target() (
  directory="$1"
  name="$2"
  check_install_directory "$directory" || return 1
  target="$directory/$name"
  [ ! -L "$target" ] || return 1
  if [ -e "$target" ]; then
    [ -d "$target" ] || return 1
    # gh --force writes into existing trees. Refuse links inside them as well.
    links="$(find "$target" -type l -print)" || return 1
    [ -z "$links" ] || return 1
  fi
)

install_for_paths() (
  repo="$1"
  skill="$2"
  commit="$3"
  clone="$4"
  paths="$(read_install_paths)" || exit 1
  [ -n "$paths" ] || fail "no install paths configured; use paths add <directory>"
  if [ "$skill" = --all ]; then
    names="$(find "$clone" -type f -name SKILL.md -not -path '*/.git/*' -exec dirname {} \; | sed 's|.*/||' | LC_ALL=C sort -u)"
  else
    directory="${skill%/SKILL.md}"
    names="${directory##*/}"
  fi

  # Validate all destinations before the first write, then recheck each one.
  while IFS= read -r path; do
    while IFS= read -r name; do
      check_install_target "$path" "$name" || fail "unsafe install destination: $path"
    done <<EOF_NAMES
$names
EOF_NAMES
  done <<EOF_PATHS
$paths
EOF_PATHS
  while IFS= read -r path; do
    while IFS= read -r name; do
      check_install_target "$path" "$name" || fail "install destination changed: $path"
    done <<EOF_NAMES
$names
EOF_NAMES
    say "Installing in $path"
    if [ "$skill" = "--all" ]; then
      gh skill install "$repo" --all --pin "$commit" --dir "$path" --force || fail "installation failed in $path; earlier paths may already be installed"
    else
      gh skill install "$repo" "$skill" --pin "$commit" --dir "$path" --force || fail "installation failed in $path; earlier paths may already be installed"
    fi
  done <<EOF_PATHS
$paths
EOF_PATHS
)

safe_user_skill_path() (
  skill="$1"
  path="$2"
  paths="$3"
  path="$(normalize_install_path "$path")" || return 1
  [ "${path##*/}" = "$skill" ] || return 1
  parent="${path%/*}"
  printf '%s\n' "$paths" | grep -Fqx "$parent" || return 1
  check_install_directory "$parent" || return 1
  # Check parents, never the leaf: deleting an installed symlink removes it only.
  printf '%s\n' "$path"
)

list_skills() (
  check_gh_skill
  paths="$(read_install_paths)" || exit 1
  [ -n "$paths" ] || { say "No install paths configured."; exit; }
  while IFS= read -r path; do
    check_install_directory "$path" || fail "unsafe install directory: $path"
    [ -d "$path" ] || continue
    say "Skills in $path"
    gh skill list --dir "$path" || fail "could not list installed skills"
  done <<EOF_PATHS
$paths
EOF_PATHS
)

uninstall_skill() (
  skill="$1"
  case "$skill" in
    ""|.|..|*/*) fail "uninstall requires an exact skill name" ;;
  esac
  case "$skill" in
    *'
'*) fail "skill name contains control characters" ;;
  esac
  if printf '%s' "$skill" | LC_ALL=C grep -q '[[:cntrl:]]'; then
    fail "skill name contains control characters"
  fi
  check_gh_skill
  paths="$(read_install_paths)" || exit 1

  tmp_uninstall="$(mktemp -d "${TMPDIR:-/tmp}/skillstrap-uninstall.XXXXXX")" || fail "could not create uninstall directory"
  trap 'rm -rf "$tmp_uninstall"' 0
  trap 'exit 1' HUP INT TERM
  rows="$tmp_uninstall/rows"
  seen="$tmp_uninstall/paths"
  : > "$seen"

  : > "$rows"
  while IFS= read -r path; do
    [ -n "$path" ] || continue
    check_install_directory "$path" || fail "unsafe uninstall directory: $path"
    [ -d "$path" ] || continue
    gh skill list --dir "$path" \
      --json skillName,path \
      --template '{{range .}}{{if or (regexMatch "[[:cntrl:]]" .skillName) (regexMatch "[[:cntrl:]]" .path)}}INVALID{{else}}{{printf "%s\t%s" .skillName .path}}{{end}}{{"\n"}}{{end}}' \
      >> "$rows" || fail "could not list installed skills"
  done <<EOF_PATHS
$paths
EOF_PATHS

  # Validate the complete removal set before deleting the first installation.
  while IFS="$(printf '\t')" read -r name path; do
    [ "$name" != INVALID ] || fail "installed skill list contains control characters"
    [ "$name" = "$skill" ] || continue
    abs="$(safe_user_skill_path "$skill" "$path" "$paths")" || fail "refusing unsafe uninstall path reported by gh"
    if ! grep -Fqx "$abs" "$seen"; then
      printf '%s\n' "$abs" >> "$seen"
    fi
  done < "$rows"
  [ -s "$seen" ] || fail "no skill named '$skill' is installed in configured paths"

  while IFS= read -r abs; do
    # Recheck parents immediately before removal as well as during preflight.
    safe_user_skill_path "$skill" "$abs" "$paths" >/dev/null || fail "uninstall path changed during removal"
    say "Removing $skill"
    say "  $abs"
    if [ -L "$abs" ] || [ -f "$abs" ]; then
      rm -f "$abs" || fail "could not remove $abs"
    elif [ -d "$abs" ]; then
      rm -rf "$abs" || fail "could not remove $abs"
    fi
  done < "$seen"
  say "Uninstalled '$skill'."
)

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
    list_skills
    ;;
  paths)
    case "${2:-list}" in
      list)
        [ "$#" -le 2 ] || fail "usage: skillstrap.sh paths [list]"
        manage_paths list
        ;;
      add|remove)
        [ "$#" -eq 3 ] || fail "usage: skillstrap.sh paths <add|remove> <directory>"
        manage_paths "$2" "$3"
        ;;
      *) fail "usage: skillstrap.sh paths [list|add <directory>|remove <directory>]" ;;
    esac
    ;;
  help|-h|--help)
    usage
    ;;
  *)
    usage >&2
    exit 1
    ;;
esac

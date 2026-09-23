#!/usr/bin/env bash
set -e

skills_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
agents_skills_dir="$HOME/.agents/skills"
plugin_dir="$HOME/.gemini/config/plugins/My-Skills"
plugin_skills_dir="$plugin_dir/skills"

mkdir -p "$agents_skills_dir" "$plugin_skills_dir"

if [ ! -e "$plugin_dir/plugin.json" ] && [ ! -L "$plugin_dir/plugin.json" ]; then
  cat > "$plugin_dir/plugin.json" <<'EOF'
{
  "name": "My-Skills",
  "version": "1.0.0",
  "description": "Local custom skills"
}
EOF
fi

for skill in "$skills_dir"/*; do
  [ -d "$skill" ] || continue
  [ -f "$skill/SKILL.md" ] || continue

  name="$(basename "$skill")"
  [ -e "$agents_skills_dir/$name" ] || [ -L "$agents_skills_dir/$name" ] || ln -s "$skill" "$agents_skills_dir/$name"
  [ -e "$plugin_skills_dir/$name" ] || [ -L "$plugin_skills_dir/$name" ] || ln -s "$skill" "$plugin_skills_dir/$name"
done

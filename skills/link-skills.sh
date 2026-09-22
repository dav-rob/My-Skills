#!/usr/bin/env bash
set -e

mkdir -p "$HOME/.agents/skills"

for skill in "$HOME/projects/quick-scripts/My-Skills/skills"/*; do
  name="$(basename "$skill")"
  [ -e "$HOME/.agents/skills/$name" ] || ln -s "$skill" "$HOME/.agents/skills/$name"
done

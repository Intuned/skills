#!/usr/bin/env bash
# Symlink every skill in this repo into ~/.claude/skills/ (a local alternative to
# `npx skills@latest add intunedhq/skills`). Re-runnable; updates existing links.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEST="${CLAUDE_SKILLS_DIR:-$HOME/.claude/skills}"
mkdir -p "$DEST"

# Find every skill folder (a directory containing SKILL.md) under skills/.
found=0
while IFS= read -r skill_md; do
  skill_dir="$(dirname "$skill_md")"
  name="$(basename "$skill_dir")"
  ln -sfn "$skill_dir" "$DEST/$name"
  echo "linked $name -> $skill_dir"
  found=$((found + 1))
done < <(find "$REPO_ROOT/skills" -name SKILL.md -type f)

echo "Done. Linked $found skill(s) into $DEST"
echo "Restart your agent session to load them."

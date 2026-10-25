#!/usr/bin/env bash
# Scaffold a per-book reading-companion workspace.
#
# Lays down the deterministic structure so the model only has to FILL the
# AGENTS.md placeholders afterwards — it never has to recreate folders or
# re-copy the methodology references by hand.
#
# Usage:  init-workspace.sh <target-workspace-dir>
#
# After running, the model edits <target>/AGENTS.md, replacing every {{...}}
# placeholder with book-specific content (see SKILL.md → "Fill the AGENTS.md").

set -euo pipefail

TARGET="${1:?usage: init-workspace.sh <target-workspace-dir>}"
SKILL_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Existing instructions or authored reading artifacts must be extended in place.
for file in AGENTS.md CLAUDE.md CLAUDE.local.md AGENTS.override.md .claude/CLAUDE.md notes/log.md references/kb-card-specification.md; do
  if [ -e "$TARGET/$file" ] || [ -L "$TARGET/$file" ]; then
    printf 'Refusing to overwrite existing workspace file: %s\n' "$TARGET/$file" >&2
    exit 1
  fi
done
for directory in notes references; do
  if [ -L "$TARGET/$directory" ]; then
    printf 'Refusing to scaffold through a linked directory: %s\n' "$TARGET/$directory" >&2
    exit 1
  fi
done
# Keep concurrent creation from overwriting an entry after the preflight check.
set -o noclobber

mkdir -p "$TARGET"/{notes,cards,rules,scripts,book,references}

# Only the card spec is copied in — the reader takes it as a base and customizes
# it. The reading methodology itself is embedded into the workspace AGENTS.md at
# fill time (see SKILL.md → Step 4), so the methods travel with AGENTS.md and no
# separate methodology file is copied.
cat "$SKILL_ROOT/references/kb-card-specification.md" > "$TARGET/references/kb-card-specification.md"

# Seed the conversation/note-taking config and the live log (placeholders intact).
cat "$SKILL_ROOT/assets/AGENTS.template.md" > "$TARGET/AGENTS.md"
cat "$SKILL_ROOT/assets/log.template.md" > "$TARGET/notes/log.md"

# Keep empty artifact folders under version control if the workspace is a repo.
for d in cards rules scripts; do
  [ -e "$TARGET/$d/.gitkeep" ] || : > "$TARGET/$d/.gitkeep"
done

echo "Workspace scaffolded at: $TARGET"
echo "Next: fill the {{...}} placeholders in $TARGET/AGENTS.md and notes/log.md"
find "$TARGET" -type f | sort
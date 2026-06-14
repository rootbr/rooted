#!/usr/bin/env bash
# Scaffold a per-book reading-companion workspace.
#
# Lays down the deterministic structure so the model only has to FILL the
# CLAUDE.md placeholders afterwards — it never has to recreate folders or
# re-copy the methodology references by hand.
#
# Usage:  init-workspace.sh <target-workspace-dir>
#
# After running, the model edits <target>/CLAUDE.md, replacing every {{...}}
# placeholder with book-specific content (see SKILL.md → "Fill the CLAUDE.md").

set -euo pipefail

TARGET="${1:?usage: init-workspace.sh <target-workspace-dir>}"
SKILL_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

mkdir -p "$TARGET"/{notes,cards,rules,scripts,book,references}

# Only the card spec is copied in — the reader takes it as a base and customizes
# it. The reading methodology itself is embedded into the workspace CLAUDE.md at
# fill time (see SKILL.md → Step 4), so the methods travel with CLAUDE.md and no
# separate methodology file is copied.
cp "$SKILL_ROOT/references/kb-card-specification.md" "$TARGET/references/"

# Seed the conversation/note-taking config and the live log (placeholders intact).
cp "$SKILL_ROOT/assets/CLAUDE.template.md" "$TARGET/CLAUDE.md"
cp "$SKILL_ROOT/assets/log.template.md"    "$TARGET/notes/log.md"

# Keep empty artifact folders under version control if the workspace is a repo.
for d in cards rules scripts; do
  [ -e "$TARGET/$d/.gitkeep" ] || : > "$TARGET/$d/.gitkeep"
done

echo "Workspace scaffolded at: $TARGET"
echo "Next: fill the {{...}} placeholders in $TARGET/CLAUDE.md and notes/log.md"
find "$TARGET" -type f | sort
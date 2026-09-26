#!/usr/bin/env bash
# Build a temporary git repository from the fixture trees so scripts/static-craft.py and the
# finders run on a real diff. Two modes:
#   committed (default): base/ is committed, then head/ replaces the tree and is committed too;
#                        the diff to review is `HEAD~1..HEAD`.
#   --worktree:          base/ is committed, then head/ replaces the tree and stays uncommitted
#                        (edited files unstaged, new files untracked); the diff to review is the
#                        working tree against HEAD, which is the pre-pass's default mode.
# Prints the repository path.
#
# Usage: evals/fixture/make-fixture.sh [--worktree] [<target-dir>]
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
mode=committed
if [ "${1:-}" = "--worktree" ]; then
  mode=worktree
  shift
fi
target="${1:-$(mktemp -d)}"
mkdir -p "$target"
git -C "$target" init -q -b main
export GIT_AUTHOR_NAME=fixture GIT_AUTHOR_EMAIL=fixture@example.com
export GIT_COMMITTER_NAME=fixture GIT_COMMITTER_EMAIL=fixture@example.com
cp -R "$here/base/." "$target/"
git -C "$target" add -A
git -C "$target" commit -q -m "base: the fixture tree before the change"
# head replaces the tree wholesale so a file removed from head/ is removed from the repo
find "$target" -mindepth 1 -maxdepth 1 ! -name .git -exec rm -rf {} +
cp -R "$here/head/." "$target/"
if [ "$mode" = committed ]; then
  git -C "$target" add -A
  git -C "$target" commit -q -m "head: seeded defects and controls"
fi
echo "$target"

#!/usr/bin/env bash
# Build a temporary git repository with two commits — base, then head — from the
# fixture trees, so scripts/static-review.py and the finders run on a real diff_ref.
# Prints the repository path; the diff to review is `main~1..main` (or `HEAD~1..HEAD`).
#
# Usage: evals/fixture/make-fixture.sh [<target-dir>]
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
target="${1:-$(mktemp -d)}"
mkdir -p "$target"
git -C "$target" init -q -b main
export GIT_AUTHOR_NAME=fixture GIT_AUTHOR_EMAIL=fixture@example.com
export GIT_COMMITTER_NAME=fixture GIT_COMMITTER_EMAIL=fixture@example.com
cp -R "$here/base/." "$target/"
git -C "$target" add -A
git -C "$target" commit -q -m "base: shared cache, stats, totals, repo, log scanner, request context"
# head replaces the tree wholesale so a file removed from head/ is removed from the repo
find "$target" -mindepth 1 -maxdepth 1 ! -name .git -exec rm -rf {} +
cp -R "$here/head/." "$target/"
git -C "$target" add -A
git -C "$target" commit -q -m "head: seeded defects and controls"
echo "$target"

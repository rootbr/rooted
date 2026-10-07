#!/usr/bin/env bash
# Finish one series topic whose research runs completed: write the note, the cards, the provenance
# lines and the pending entries from its run outputs, and run the validator.
# Usage: finish-topic.sh <topic-slug> <run output> [<run output> ...]
#   a run output is the Workflow tool's task output (<tasks-dir>/<task id>.output), a snapshot under
#   ../outputs/<slug>.output.json.gz, or the cut-short output research-continue.py --write-output wrote;
#   several outputs are one topic split over a cut-short run and its continuation bundles.
# Run from the repository root. Commit the files it writes afterwards (git add by name).
set -euo pipefail
topic="$1"; shift
[ $# -ge 1 ] || { echo "usage: finish-topic.sh <slug> <run output> [...]"; exit 2; }
ROOT="$(cd "$(dirname "$0")/../../../.." && pwd)"
K="$ROOT/plugins/code-quality/skills/software-craft"
tmp="$ROOT/research/software-craft/.state/.tmp-finish"; mkdir -p "$tmp"
runs=()
for out in "$@"; do
  case "$out" in
    *.gz) plain="$tmp/$(basename "${out%.gz}")"; gunzip -c "$out" > "$plain"; runs+=("$plain");;
    *) [ -s "$out" ] || { echo "empty or missing: $out"; exit 1; }; runs+=("$out");;
  esac
done
for r in "${runs[@]}"; do
  python3 -c "import json,sys; d=json.load(open(sys.argv[1])); r=d.get('result', d); print(sys.argv[1].split('/')[-1], '| cards', len(r.get('cards',[])), '| pending', len(r.get('pending_entries',[])), '| held', len(r.get('held',[])), '| agents', d.get('agentCount'), '| tokens', d.get('totalTokens'))" "$r"
done
args=(); for r in "${runs[@]}"; do args+=(--run "$r"); done
python3 "$K/scripts/write-topic-result.py" "${args[@]}" --root "$ROOT" --status done
python3 "$K/scripts/validate-craft-cards.py" --provenance "$K/references/craft-cards-provenance.md" --pending "$K/references/pending-evidence.md" "$K/references/craft-cards"
rm -rf "$tmp"
echo "finished $topic: review the note and the cards, then commit research/software-craft/$topic.md, the new cards, craft-cards-provenance.md and pending-evidence.md"

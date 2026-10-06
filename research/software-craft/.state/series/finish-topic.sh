#!/usr/bin/env bash
# Finish one series topic whose research run completed: archive its task output, write the
# note, the cards, the provenance lines and the pending entries, and run the validator.
# Usage: finish-topic.sh <topic-slug> <task-id>   (run from the repository root)
set -euo pipefail
topic="$1"; task="$2"
T=/tmp/claude-0/-home-user-rooted/61735d01-895f-5d61-bc3c-3f903162bd3a/tasks
K=plugins/code-quality/skills/software-craft
out="$T/$task.output"
[ -s "$out" ] || { echo "no output for $task"; exit 1; }
python3 -c "import json,sys; d=json.load(open(sys.argv[1])); r=d['result']; print('topic', r['topic']['slug'], '| cards', len(r.get('cards',[])), '| pending', len(r.get('pending',[])), '| held', len(r.get('held',[])), '| agents', d.get('agentCount'), '| tokens', d.get('totalTokens'))" "$out"
gzip -c "$out" > "research/software-craft/.state/${topic}--series--output.json.gz"
python3 "$K/scripts/write-topic-result.py" --run "$out" --root /home/user/rooted --status done
python3 "$K/scripts/validate-craft-cards.py" --provenance "$K/references/craft-cards-provenance.md" --pending "$K/references/pending-evidence.md" "$K/references/craft-cards"

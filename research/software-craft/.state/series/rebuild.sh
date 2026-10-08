#!/usr/bin/env bash
# rebuild.sh <slug> <finish|rest> [split] : rebuild a topic's bundle(s) from every journal of the topic into
# $S/cont/<slug>/<ROUND_DIR>/<kind>/ (ROUND_DIR defaults to r2); a fresh directory per round, nothing deleted.
set -euo pipefail
slug=$1; kind=$2; split=${3:-1}
S=${SCRATCH:-/tmp/claude-0/-home-user-rooted/e90d4d4d-b4c5-58b7-8385-bbb5069933a1/scratchpad}
ST=/home/user/rooted/research/software-craft/.state
K=/home/user/rooted/plugins/code-quality/skills/software-craft
W=/root/.claude/projects/-home-user-rooted/e90d4d4d-b4c5-58b7-8385-bbb5069933a1/subagents/workflows
R=${ROUND_DIR:-r2}
d=$S/cont/$slug; out=$d/$R/$kind; mkdir -p "$out" "$d/outputs"
J=(--journal $d/journal.jsonl); C=()
for p in 1of2 2of2; do
  j=$ST/journals/$slug--$p.journal.jsonl.gz; o=$ST/outputs/$slug--$p.output.json.gz
  [ -f $j ] && { gunzip -c $j > $d/outputs/$p.journal.jsonl; J+=(--journal $d/outputs/$p.journal.jsonl); }
  [ -f $o ] && { gunzip -c $o > $d/outputs/$p.output.json; C+=(--skip-carded $d/outputs/$p.output.json); }
done
# every later run of the topic (live journals), and the outputs of the finished ones
for wf in $(python3 -c "import json; b=json.load(open('$ST/series/batch3.json')); print(' '.join(r['wf']+':'+r['task'] for r in b['topics']['$slug']['runs'] if not r['part'] in ('1of2','2of2')))"); do
  id=${wf%%:*}; task=${wf##*:}
  [ -f $W/$id/journal.jsonl ] && J+=(--journal $W/$id/journal.jsonl)
  o=/tmp/claude-0/-home-user-rooted/e90d4d4d-b4c5-58b7-8385-bbb5069933a1/tasks/$task.output
  if [ -s $o ]; then C+=(--skip-carded $o)
  elif [ -f $W/$id/journal.jsonl ]; then
    # a stopped run: the cards its journal finished (closing edits, accepted fixes) become a carded output
    cj=$d/outputs/$id.carded.json
    python3 $K/scripts/research-continue.py --journal $d/journal.jsonl --carded-journal $W/$id/journal.jsonl --from-bundle $S/bundles/$slug.js --round 1 --write-carded $cj --root /home/user/rooted >/dev/null
    [ -s $cj ] && C+=(--skip-carded $cj)
  fi
done
if [ $kind = finish ]; then
  python3 $K/scripts/research-continue.py "${J[@]}" --from-bundle $S/bundles/$slug.js --round 1 --resume-cut-short "${C[@]}" --split $split --out-dir "$out" --root /home/user/rooted
else
  python3 $K/scripts/research-continue.py "${J[@]}" --from-bundle $S/bundles/$slug.js --round 1 --skip-fixed "${C[@]}" --split $split --out-dir "$out" --root /home/user/rooted
fi

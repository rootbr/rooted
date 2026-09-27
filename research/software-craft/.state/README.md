# Paused state of the software-craft pilot

Transient: this directory holds the material a paused session needs to resume the pilot without re-running finished agents. It is removed at the close of the work (step 6). Nothing here ships with the plugin.

## What is here

- `index.json` — every pilot run: topic, run label, task id, workflow directory, rotation start, and which agents each journal holds.
- `<topic>--<run>--journal.jsonl.gz` — the workflow journals (one `result` line per finished agent; `research-continue.py` reads them after `gunzip`).
- `<topic>--<run>--output.json.gz` — the Workflow tool outputs of the finished runs (`result.topic`, `result.spine`, `result.next_id`; the cut-short round-2 runs have none).
- `docs-pending.patch` — four documentation changes (SKILL.md script bullet, gotchas G-18, maintenance.md, the design note's research-workflow step 5 and topic count) that await the Quality Gate audit before their commit; apply with `git apply research/software-craft/.state/docs-pending.patch` if the working tree lost them.
- `series/` — the validated argument objects of the 45 series topics (`topics-*.json`, with paper seeds relayed by the orchestrator's searches), the bundle maker `make-bundles.py` (validates against the design note's taxonomy table, embeds the channel note, writes one bundle per topic), the seed merger and the prompt the topic-argument agents followed.
- `make-inventory.py` — the audit inventory helper (`--target-type <type> --tier <tier> --out <inventory.md> <target>`).

## Where the pilot stands

Rotation starts: naming 0, errors 1, doubles 2. Per topic: sources, spine, 12 drafts, 12 first verdicts, 12 fixes and 12 second verdicts are done (round 1: 1 card accepted, 35 rules sent back with exact edits); round 2's fixes (`fix2:`) are done for all 35 rules; round 2's verdicts (`verify3:`) ran for 1 rule (test-doubles) before the pause. The environment facts that shaped this: the sub-agents' WebSearch budget (`CLAUDE_CODE_MAX_WEB_SEARCHES_PER_SESSION`, 200 per session) was spent before the pilot's source layer ran, so papers reach a card only through GitHub-hosted copies or the orchestrator's relayed snippets; the workflow runtime caps each workflow at two concurrent agents on this host.

## To resume

1. Unpack: `mkdir -p /tmp/craft-state && for f in research/software-craft/.state/*.gz; do gunzip -c "$f" > /tmp/craft-state/$(basename "${f%.gz}"); done`
2. Finish round 2 per topic (only the missing skeptic verdicts run; a rule the verdict does not accept goes to pending):
   `python3 plugins/code-quality/skills/software-craft/scripts/research-continue.py --journal /tmp/craft-state/<topic>--r2-1--journal.jsonl --journal ...r2-2... --journal ...r2-3... --from-output /tmp/craft-state/<topic>--r1-1of3--output.json --round 2 --resume-cut-short --rotation-start <rot> --split 3 --out-dir <dir> --root /home/user/rooted`
   then `Workflow({scriptPath: <bundle>})` for each bundle (no args).
3. Write each topic: `python3 plugins/code-quality/skills/software-craft/scripts/write-topic-result.py --run <orig output> --run <r1 outputs ×3> --run <finish outputs> --root /home/user/rooted --status verified`, then the validator and the card audit (kb-card), then the pilot commit.
4. Apply the pending doc patch if needed, audit the four docs (`make-inventory.py` + the audit workflow), commit.
5. Series: `python3 research/software-craft/.state/series/make-bundles.py research/software-craft/.state/series/topics-*.json` writes 45 bundles (rotation by topic index, existing titles from the cards in the tree, the channel note embedded); launch in batches of about ten workflows; after each topic's first round, `--round 2` over its journals; then the writer.

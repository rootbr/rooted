# Transient state of the software-craft build

This directory holds what a continuation of the work needs and nothing that ships: it is removed at the close (step 6). Start with `HANDOVER.md`: the commission, the plan and its state, the environment facts, and the runbook for continuing in another session or another checkout.

## Layout

- `HANDOVER.md` — read first.
- `series/STATUS.md`, `series/status.json` — per-topic state of the series runs, written by `series/series-status.py --snapshot`.
- `series/batchN.json` — the launched batches: per topic the workflow run id and the task ids of every attempt.
- `series/topics-*.json` — the validated argument objects of the 45 series topics (paper seeds relayed by the orchestrator's searches included); `series/make-bundles.py` writes one research-workflow bundle per topic from them into a directory outside the repository.
- `series/finish-topic.sh` — writes a finished topic into the tree (note, cards, provenance lines, pending entries) and validates.
- `series/REVIEWER.md` — the domain reviewer prompt; `series/PROMPT.md`, `series/exemplar-*.json`, `series/merge-seeds.py` — how the topic objects were made.
- `journals/<slug>.journal.jsonl.gz` — snapshot of each in-flight topic's workflow journal (one `result` line per finished agent); `scripts/research-continue.py --from-bundle` continues a topic from it.
- `outputs/<slug>.output.json.gz` — the task outputs of finished runs, the input of `finish-topic.sh`.
- `docs-pending.patch` — documentation edits held until their Quality Gate audit at the close (`git apply`).
- `make-inventory.py` — the audit inventory helper (`--target-type <type> --tier <tier> --out <inventory.md> <target>`).
- `pilot-expected-gen.py` — the generator of the pilot rows of `evals/expected.json`, the pattern for extending the fixture.
- `index.json`, `<topic>--<run>--journal.jsonl.gz`, `<topic>--<run>--output.json.gz` — the pilot's runs (naming, error handling, test doubles), written and committed; kept for re-verification only.

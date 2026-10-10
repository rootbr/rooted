# Maintaining reviewing-java

What changes together when a card, a script, a prompt or a tier changes, and what to re-run. Paths are relative to the skill directory. `README.md` §Layout maps who reads or runs each file.

- Before committing a card, an agent prompt or SKILL.md: `maintenance/scripts/validate-review-cards.py --pending maintenance/pending-evidence.md references/review-cards`, then the audit (repository Quality Gate).
- A rule is one card in `references/review-cards/`; adding or removing one means its card, its `maintenance/review-cards-provenance.md` line, and a `maintenance/review-cards-taxonomy.md` value when a facet is new.
- The validator rejects a `## Source` heading: a card's sources live on its line in `maintenance/review-cards-provenance.md`, found by grepping the map for the id, and `scripts/render-reports.py` reads a finding's source pointer from it (`BLOCKS` and the provenance helpers in `scripts/cardlib.py`). `cardlib.provenance_map_path` is the one place that knows the map's address, and the renderer and the validator go through it.
- A rule with no openable source lives in `maintenance/pending-evidence.md` until one is found; it has no card and no id.
- `maintenance/java-invariants-review-checklist.md` is the guide to discovering, documenting and verifying a project's invariants, which `README.md` §Project integration points a project to for its `config.md`.
- When the aggregation definitions, the schemas, or the prompts change, change `scripts/review-workflow.js` and `plugins/code-quality/agents/review-finder.md` / `review-verifier.md` in the same commit; when a card's triggers or the candidate list change, re-run the tests (§Scripts) and the fixture grading (`evals/grade.py`).
- Pin the tier models in `evals/evals.json`; re-run the fixture on every model change.

## Scripts

The maintainer's script and the tests, each with what it does, reads, writes and the privileges it takes; the run scripts are declared in SKILL.md §Phase 4. Every script of the skill is standard library only, with no network, and a change to any of them re-runs the tests below and the fixture grading.

- `maintenance/scripts/validate-review-cards.py` — checks every card against the corpus schema of `maintenance/review-cards-taxonomy.md` and, with the maps, one provenance line per card and no shipped id among the pending entries; reads the cards, the provenance map (`--provenance`, else the one `cardlib.provenance_map_path` names) and `--pending`; writes nothing.
- `maintenance/tests/` — the unit tests of every script of the skill, the run scripts included: `python3 -m unittest discover -s maintenance/tests -p 'test_*.py'` from the skill directory. They build their fixtures under temporary directories and run git in a temporary repository.

## Deferring pairs (`DEFER_TO`)

A finding of the deferring rule drops when any owner listed for it flagged the same span. Keep this table and `scripts/review-workflow.js` in step.

| Deferring rule | Owner(s) |
|--|--|
| CC-01 | CC-02, CC-09, CC-10, CC-12 |
| CC-07 | CC-45 |
| CC-10 | CC-48 |
| CC-31 | REL-49 |
| CC-32 | CC-03 |
| CC-34 | CC-21 |
| CC-46 | CC-21 |
| CC-49 | CC-01, CC-13 |
| MNT-06 | MNT-05 |
| MNT-16 | CC-16 |
| MNT-27 | REL-07 |
| PF-19 | MNT-31 |
| PF-22 | MNT-24 |
| REL-20 | REL-52 |
| REL-59 | REL-58 |
| SEC-15 | SEC-16 |
| SEC-19 | SEC-18 |
| SEC-36 | SEC-30 |
| SEC-49 | SEC-30 |

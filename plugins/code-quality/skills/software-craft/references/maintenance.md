# Maintaining software-craft

What changes together when a card, a script, a prompt, a signal or a tier changes, and what to re-run. Paths are relative to the skill directory; `plugins/` paths from the repository root.

- A rule is one card in `references/craft-cards/`; adding or removing one means its card, its `references/craft-cards-provenance.md` line, its topic's research note under `research/software-craft/` (the "Cards derived" table), and a `references/craft-cards-taxonomy.md` value when a facet is new. Run `scripts/validate-craft-cards.py --provenance references/craft-cards-provenance.md --pending references/pending-evidence.md references/craft-cards` before committing; run the audit on every card, agent or SKILL.md change (repository Quality Gate).
- A rule with no openable evidence, or a contested rule with no sourced separating condition, lives in `references/pending-evidence.md` until one is found; it has no card and no id.
- A topic is re-researched, or a new one added, through `scripts/research-topic-workflow.js` with the topic's row from the design note's taxonomy as its arguments; `scripts/write-topic-result.py` writes the run's note, cards, provenance lines and pending entries, renumbering ids contiguously from the cards already in the tree. A new topic is a new row in the design note's taxonomy table and a new entry in its deviations section.
- When the aggregation definitions, the schemas, the severity scale or the prompts change, change `scripts/craft-review-workflow.js` and `plugins/code-quality/agents/craft-finder.md` / `craft-verifier.md` in the same commit as SKILL.md §Aggregation and §Workflow; when the developer's procedure changes, `plugins/code-quality/agents/software-developer.md` and SKILL.md §Build change together.
- When a card's triggers, a structural signal, a threshold or the candidate list change, change `scripts/static-craft.py` (`SIGNALS`, `THRESHOLDS`, `CANDIDATE_RULE_IDS`), `scripts/cardlib.py` (`SIGNALS`), the design note's "Structural signals" table and `scripts/tests/test_static_craft.py` together, then re-run `scripts/tests/` and the fixture grading (`evals/grade.py`) in both modes of `evals/fixture/make-fixture.sh`.
- A new facet value (a `step`, an `applies_to` scope) is a `scripts/cardlib.py` constant, a `references/craft-cards-taxonomy.md` row and a `scripts/research-topic-workflow.js` enum in the same commit.
- Pin the tier models in `evals/evals.json`; re-run the fixture on every model change.
- A card the fixture seeds is a row in `evals/expected.json` and a seed plus a control in `evals/fixture/head/`; renaming the card's id renames the row.

## Deferring pairs (`DEFER_TO`)

A finding of the deferring rule drops when any owner listed for it flagged the same span. Keep this table and `scripts/craft-review-workflow.js` in step. The table is filled from the pairs the corpus reviewers find still overlapping after the series.

| Deferring rule | Owner(s) |
|--|--|
| (none yet) | |

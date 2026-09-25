# Maintaining reviewing-java

What changes together when a card, a script, a prompt or a tier changes, and what to re-run. Paths are relative to the skill directory.

- A rule is one card in `references/review-cards/`; adding or removing one means its card, its `references/review-cards-provenance.md` line, and a `references/review-cards-taxonomy.md` value when a facet is new. Run `scripts/validate-review-cards.py --provenance references/review-cards-provenance.md --pending references/pending-evidence.md references/review-cards` before committing; run the audit on every card, agent or SKILL.md change (repository Quality Gate).
- A rule with no openable source lives in `references/pending-evidence.md` until one is found; it has no card and no id.
- When the aggregation definitions, the schemas, or the prompts change, change `scripts/review-workflow.js` and `plugins/code-quality/agents/review-finder.md` / `review-verifier.md` in the same commit; when a card's triggers or the candidate list change, re-run `scripts/tests/` and the fixture grading (`evals/grade.py`).
- Pin the tier models in `evals/evals.json`; re-run the fixture on every model change.


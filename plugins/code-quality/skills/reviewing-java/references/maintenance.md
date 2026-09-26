# Maintaining reviewing-java

What changes together when a card, a script, a prompt or a tier changes, and what to re-run. Paths are relative to the skill directory.

- A rule is one card in `references/review-cards/`; adding or removing one means its card, its `references/review-cards-provenance.md` line, and a `references/review-cards-taxonomy.md` value when a facet is new. Run `scripts/validate-review-cards.py --provenance references/review-cards-provenance.md --pending references/pending-evidence.md references/review-cards` before committing; run the audit on every card, agent or SKILL.md change (repository Quality Gate).
- A rule with no openable source lives in `references/pending-evidence.md` until one is found; it has no card and no id.
- When the aggregation definitions, the schemas, or the prompts change, change `scripts/review-workflow.js` and `plugins/code-quality/agents/review-finder.md` / `review-verifier.md` in the same commit; when a card's triggers or the candidate list change, re-run `scripts/tests/` and the fixture grading (`evals/grade.py`).
- Pin the tier models in `evals/evals.json`; re-run the fixture on every model change.

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

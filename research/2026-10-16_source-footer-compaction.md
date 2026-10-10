# Source block removal — a card carries no citation, its provenance line is the sole record of its sources

Decided by the operator on 2026-10-16 for the three card corpora of `code-quality` and for the audit corpus of `evidence-based-authoring`. Paths are relative to the repository root.

## Finding

Measured on 2026-10-16, before any change:

| Corpus | `## Source` bytes | Corpus bytes | Share | Median per card | p90 per card |
|--|--|--|--|--|--|
| universal craft cards — `plugins/code-quality/skills/software-craft/references/craft-cards` | 2.25 MB | 5.85 MB | 38 % | 4 148 | 6 592 |
| Python craft cards — `…/software-craft/references/craft-cards-python` | 0.45 MB | 1.12 MB | 40 % | 2 313 | — |
| Java review cards — `plugins/code-quality/skills/reviewing-java/references/review-cards` | 0.18 MB | 1.00 MB | 18 % | 708 | — |

Every byte of the block reaches runtime: the finder brief in `plugins/code-quality/skills/software-craft/scripts/craft-review-workflow.js` reads "Read the card at ${c.path}", and the developer agent opens the cards whole, step by step. No runtime consumer opens a source: the finder applies the Validator, the verifier's evidence is what it opens in the repository — the comment, the git log line, the project-context sentence, the surrounding code — and the developer builds to Thesis, Limits and Validator.

The base specification `plugins/evidence-based-authoring/skills/auditing-ai-context/references/kb-card-specification.md` has no Source block; each corpus documented its footer as a deviation from C-A5, for the human reader of a finding and for the verifier. The drafter briefs of `scripts/research-topic-workflow.js` and `scripts/python-topic-workflow.js` required a quote per locator in the footer and anchored the entailment self-check to it, and a fifth of the quoted fragments existed only in the cards: 2 278 of 11 235 in the universal craft corpus, 64 of 158 in the Python corpus and 382 of 783 in the Java corpus are absent from their provenance lines.

## First variant considered

A locator-only footer: `## Source` kept as one `- ` bullet per source plus one caveat line, every quote and fetch status moved to the provenance line, and the validators rejecting a quoted span of 60 characters or more, a fetch marker or a block over 1 200 bytes. It was dropped because the `rule_id` already keys the provenance map, so each locator repeated a citation the map holds, and cards with 17 sources still carried 2.7 KB of locators.

## Decision

1. Card shape — the body is six H2s, `## Thesis` → `## Rationale` → `## Example` → `## Limits` → `## Validator` → `## Finding output`, and no `## Source`. Owners: `craft-cards-taxonomy.md` and `review-cards-taxonomy.md`, §Body block schema and §Provenance. The corpora conform to C-A5 without a deviation.
2. Provenance line — the sole record of a card's sources: citation, URL, fetch status, every quoted statement, formulation, reception, and notes with `caveat: …` on the evidence's scope; a limit of the rule itself goes in `## Limits`. One wording states it in the headers of the three provenance maps and in `PROVENANCE_HEADER` of `write-topic-result.py`.
3. Briefs — both topic workflows name six blocks and no Source rule; the provenance-line rule carries the citations with their quotes, fetch status and evidence caveat; the drafter's sentence-by-sentence self-check pairs each sentence of Thesis, Rationale and Limits with a quoted fragment of the provenance line; the skeptic opens every citation of the provenance line and greps it for its fragments.
4. Validators — `validate-craft-cards.py` (both modes) and `validate-review-cards.py` reject a `## Source` heading and any H2 outside the six (`BLOCKS` and `block_problems` in each skill's `scripts/cardlib.py`) and run the practitioner-text check over the whole card; `check-python-cards.py` resolves the locator and checks the quoted fragments of each citation of the provenance line.
5. Readers of a source — `render-reports.py` of both skills takes a finding's one-line source pointer from the provenance map beside the card's directory: the first citation of the line, cut before its first quoted statement and at 160 characters (`source_pointer` in `scripts/cardlib.py`); `craft-cards.py --provenance <RULE_ID>` prints a craft card's line, and a Java card's line is found by grepping its map for the id.
6. Audit corpus — R-57 extends to `kb-card`: a KB card carries no provenance block, a corpus that keeps a one-line footer documents it in its taxonomy, and quoted evidence or a fetch marker in such a footer moves to the provenance map. The Limits of C-A5 and C-E2 name a source footer in the card body provenance in runtime and R-57's matter. The R-57 provenance line records this measurement with this note as its openable record.
7. The maintenance docs, READMEs and SKILL.md files of both skills state where a card's sources live and what reads them.
8. Versions — code-quality 7.2.0, evidence-based-authoring 4.10.0.

## Steps after the decision, all done on 2026-10-16

1. A migration script (kept outside the repository) moved every item of each card's `## Source` block onto the card's provenance line — a bullet as its own text less the quoted spans the line already held whole, a prose paragraph verbatim, a caveat into `notes: … caveat: …` — and deleted the block; an invariant checked that every text run of twelve characters or more of the former block is on the updated line or in the card body (0 violations in the three corpora), and a second run changes nothing.
2. Corpus C's prose footers went onto the lines whole, so no observed-result segment had to be reviewed.
3. Outside the first write zone, done by the session: `README.md` §Java review sources and §Software craft sources state that a card carries no citation and where its sources live; the footers of R-50, R-60, S-08, S-09 and S-12 keep a bare locator and their quoted statements sit on their lines in `rule-cards-provenance.md`; `static-audit.py`'s `R57_TARGETS` and the `kb-card` bullet of the audit SKILL.md list R-57; the maintainer notes on the provenance lines that referred to a card's footer were rewritten to the present layout; the two older design notes point here from their first lines.

## Result

Measured after the migration on 2026-10-16, the three card directories and their provenance maps:

```
corpus              cards   bytes before -> after   provenance before -> after
craft-cards           520   5.86 MB -> 3.60 MB      4.47 MB -> 5.58 MB
craft-cards-python    178   1.12 MB -> 0.67 MB      0.41 MB -> 0.72 MB
review-cards (java)   240   1.00 MB -> 0.82 MB      0.32 MB -> 0.51 MB
```

- No card of the three corpora has a `## Source` heading; the validators report 0 errors (the warnings on empty `triggers` predate the change); the test suites pass (software-craft 152, reviewing-java 29).
- The provenance lines received 4 303 chunks in craft (9 838 quoted statements were already on the lines and were not duplicated), 1 440 in python, 240 whole paragraphs in java, and 477 / 43 / 7 caveats into `notes`; the invariant that every text run of the former blocks is on the line or in the card body held with 0 violations; 94 maintainer notes on the lines that referred to a card's footer were rewritten to the present layout.
- Of the 18 caveats whose wording suggested a limit of the rule itself, every limit was already in the card's Limits or Validator; none was moved into a card.

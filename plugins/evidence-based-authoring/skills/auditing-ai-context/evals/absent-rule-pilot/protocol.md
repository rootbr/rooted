# Absent-rule pilot

A pilot on one question: does the audit catch a description that argues with a rule its reader never saw? Each cell below is one reading by one auditor, so every figure is an observation. The pilot is the origin of the hypotheses in `research/2026-11-20_argument-with-an-absent-rule.md`; their tests are still to be made.

## Material

- **set-a**, the text with the sentences in question: `README.md` and `plugins/evidence-based-authoring/skills/testing-claims/references/method.md` at commit `50783f2`.
- **set-b**, the same two files after their rewrite, at commit `5a3857a`.
- **set-c**, a control file the rewrite left alone: `plugins/evidence-based-authoring/skills/handing-over-to-readers/SKILL.md` at `5a3857a`.
- A file of a set is `git show <commit>:<path>`; the runs read copies under `tmp/pilot-d06/`, the paths the inventories name.
- **Cards**: the shipped `d-06` card as it stands at `5a3857a`; `cards/d-96--…`, a draft that widens the card from the alternative of a decision to any thing the subject is said not to be, and adds a second question — does the file itself present the denied thing to its reader; `cards/d-97--…`, the same draft with one more sentence that asks for a verdict on every candidate the inventory lists.
- **Inventories**: `plain.md`; `deleted-lines.md`, with the prose lines the commit `fa0bdaf` deleted, copied from the diff (`deleted-statements.txt`); `candidates.md`, with the sentences `absent_rule_probe.py` nominates (`candidates.json`); `candidates-and-deleted-lines.md`, with both.
- **Auditor**: the audit workflow of this skill, one sub-agent per card and file, the model `sonnet` at effort `medium`, on 2026-11-20. `results.json` holds what every cell flagged.

## The observation the pilot started from

The first audit of `method.md`, made while the file was a draft, ran the cards D-01, D-02, D-05, D-06 and R-61 over it, one reading each. All five returned no finding. The file's opening sentence at that time read as it does in set-a: "The scientific method is neither a sequence of steps nor a demand for a citation."

## Predictions and outcomes

T is that opening sentence: line 10 of `set-a/method.md` and line 14 of `set-a/README.md`. The predictions were written before the runs.

| | Prediction | Outcome |
|--|--|--|
| P1 | D-06 with the plain inventory leaves T unflagged in `method.md`, as the first audit did | failed: flagged |
| P2 | D-96 with the plain inventory flags T in both files | held |
| P3 | D-06 with the deleted lines flags T in both files | held |
| P4 | D-96 with the deleted lines flags T in both files | held |
| P5 | D-96 flags no sentence of the rewritten opening paragraphs of set-b | held |
| P6 | D-97, handed the 20 nominated sentences that the rewrite later changed, flags at least 16; fewer than 12 means the list does not repair recall | failed: 5 of 20 |
| P7 | D-97 with the deleted lines as well flags at least as many as under P6 | held: 5 of 20 |
| P8 | D-97 flags at most 2 of the 6 nominated sentences of the control file | held: 0 of 6 |

## Readings by sentence

Six readings of each file of set-a: three cards, each with and without the deleted lines.

| Sentence | Flagged in |
|--|--|
| T, `README.md` L14 and `method.md` L10 | 12 of 12 |
| "A claim of our own needs no citation." (`README.md` L39) | 2 of 6 |
| "A citation is the address of someone else's test and never the support itself" (`README.md` L14) | 1 of 6 |
| the same sentence in `method.md` L12 | 2 of 6 |
| "A citation is the address of such a test, and where an idea came from carries no weight." (`README.md` L9) | 2 of 6 |
| "the lines not yet touched carry their sources without a record." (`README.md` L39) | 0 of 6 |
| "A claim of our own that has no citation takes the lowest branches" (`method.md` L115) | 0 of 6 |

With the deleted lines beside it the shipped card flagged four sentences in each file where it flagged one without them. In set-b each card flagged two older lines of `README.md` and nothing in `method.md`.

## What the probe measured

`python3 -I absent_rule_probe.py <mode> …`, run from the repository root:

- `candidates 340e7a5 fa0bdaf` — the commit that introduced the text adds 546 lines of design prose; 29 sentences carry a denial or contrast marker, 25 of them one of the strict markers. The rewrite of `5a3857a` later changed 26 of the 29.
- `history 45 340e7a5` — over the 35 earlier commits that add up to 700 lines of design prose, the strict markers nominate a sentence in 24 commits, the whole marker set in 30. A marker therefore nominates; it tells an ordinary commit from the one in question by nothing.
- `echo 340e7a5 fa0bdaf` — picking the deleted rule's own terms by their rarity in the repository gives 11 sentences and leaves out every sentence about a citation: the repository uses that word throughout its reference lists.
- `trace 340e7a5 fa0bdaf --term '\b(cit(?:e|es|ed|ing|ation|ations)|traceable source|traces? to)\b'` — with the deleted rule's terms named by hand, the list holds 36 sentences in 8 files and every sentence of the table above; for `50783f2 5a3857a` it is empty.

## Limits

One reading per cell. The marker set, the draft cards and the hand-named terms were all written after the sentences were known, so every figure on set-a is fitted to its material. The 20 sentences of P6 are the ones the rewrite changed; the owner of the repository named eight of them, and the rest were the rewriter's own choice. One auditor model at one effort.

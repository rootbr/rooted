# The change that started this work — an observation outside the test

One real document, read by the three ways of `protocol.md` after run 1. It is the origin of H-08 of `maintenance/pending-evidence.md` and counts as a test of no line: the document is the one the pilot under `evals/absent-rule-pilot/` was made from.

## Material

The repository's `README.md` before and after the change that replaced "every rule cites a source" by the scientific method:

```
git show 340e7a5:README.md > tmp/absent-rule-method/readme-case/old/README.md
git show 50783f2:README.md > tmp/absent-rule-method/readme-case/new/README.md
```

The later commit `5a3857a` rewrote the sentences of that text that argued with the deleted rule.

## What each way returned

`readme.list.json` holds 18 deleted statements and 29 candidates. The files of this directory are named as in a run directory of the protocol.

| Way | Returned |
|--|--|
| The trace pass, three reviewers | 10 of the 29 candidates end as `REWRITE`, each by all three readings; the 13 sentences of the source list at the end of the document are kept |
| The cards as shipped, one reading each | 3 patches; 1 of those 10 sentences flagged |
| The cards with the deleted lines, one reading each | 4 patches; 2 of those 10 sentences flagged; all four sub-agents opened the inventory with the deleted statements |

The ten sentences, with the line of the document:

| Line | Sentence, shortened | Shipped | With the deleted lines |
|--|--|--|--|
| 7 | "… grounded instructions and disciplined reasoning instead of vibes." | | flagged |
| 7 | "Rooted admits rules by the scientific method instead: …" | | |
| 9 | "**Tested, not asserted.**" | | |
| 9 | "A citation is the address of such a test, and where an idea came from carries no weight." | | |
| 14 | "The method here is neither a sequence of steps nor a demand for a citation: …" | | |
| 14 | "A citation is the address of someone else's test and never the support itself; …" | | |
| 34 | "… an author's name supports nothing" | | |
| 39 | "A claim of our own needs no citation." | | |
| 39 | "… the lines not yet touched carry their sources without a record." | flagged | flagged |
| 90 | "A PR that offers a citation in place of a test is returned by design, not by oversight." | | |

The reviewers ran on Claude Sonnet 5.5 at effort `medium`, started without the session's instruction files; the card sub-agents ran on the same model and effort with those files.

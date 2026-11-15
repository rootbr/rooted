# Run 1 — notes

The run that counts for H-01 to H-07. The seed is the hash of the commit that registered them, `97a86d63484ee1526804c3e988e0df5ce2c88e69`. `draw.txt` holds the sixteen drawn domains; the first twelve became the cases and the reserve of four stayed unused.

## Material

- Twelve writers, one per domain, each opened `case-brief.md` and no other file of the repository (`writers.calls.txt`, 0 forbidden calls). Every case passed `validate` at exit 0.
- Twelve checkers, one per case, each opened `label-check-brief.md` and the two documents of its case (`checkers.calls.txt`, 0 forbidden calls). No checker found that a `new.md` presents its old rule.
- `confirm` kept 119 of 120 planted sentences: in case 07 the writer's `foil` p04 got `trace` from the checker and stays out of the count. The twelve `<case>.labels-check.json` files hold the confirmed ids.
- `validate --cues` named nine planted sentences without a cue, seven `licensed` and two `plain`; every planted `trace` and `foil` carries one.

## The three arms

| Arm | Agents | What is kept |
|--|--|--|
| The trace pass | 36 reviewers, three per case, on Claude Sonnet 5.5 at effort `medium` | `<case>.list.json`, `<case>.reading-<k>.json`, `<case>.dispositions.json`, `<case>.check.txt` (the output of `check_trace.py`), `reviewers.calls.txt` |
| The cards as shipped | 48 sub-agents, four cards per case, on Claude Sonnet 5.5 at effort `medium`, and one indexer on Claude Haiku 5.5 | `static.json`, `inventory.md`, `baseline.json`, `cards.calls.txt` |
| The cards with the deleted lines | the same | `inventory-deleted.md`, `baseline-deleted.json`, `cards-deleted.calls.txt` |

The models are read from the harness transcripts of the four workflow runs: writers and checkers ran on Claude Opus 5.5. All five `calls` files report 0 forbidden calls. Every reviewer opened the instruction file, its list and its document. Every card sub-agent opened its document and its card; the inventory, which the audit workflow names to a sub-agent as a path, was opened by a part of them (section "Who read the inventory").

`results.json` and `score.txt` are the output of `absent_rule_eval.py score`.

## Checks around the run

- The twelve `new.md` files have the same checksums before and after the two audit runs.
- `git diff 97a86d6 -- <paths>` prints nothing for `scripts/trace_list.py`, `scripts/check_trace.py`, the agent `trace-reviewer.md`, the cards D-01, D-02, D-06 and R-61, `scripts/audit-workflow.js`, `scripts/static-audit.py`, `absent_rule_eval.py`, the two briefs and the protocol.
- The audit sub-agents ran as the agent types of the installed copy of the plugin. Its two definitions, `audit-subagent.md` and `audit-indexer.md`, are byte for byte the files of the registering commit; the cards and the scripts were read from the working tree at that commit.

## Who read the inventory

By `cards.calls.txt` and `cards-deleted.calls.txt`:

| Arm | Sub-agents that opened the inventory | By card | Cases where none opened it |
|--|--|--|--|
| The cards as shipped | 12 of 48 | D-02 10, D-01 2 | 01, 09 |
| The cards with the deleted lines | 17 of 48 | D-02 9, D-01 5, D-06 3, R-61 0 | 04, 09 |

The deleted statements therefore reached the sub-agents that opened `inventory-deleted.md`. Counted apart, as an observation the protocol fixed no measure for:

| Where the reader of D-02 | `trace` sentences | Flagged with the deleted lines | Flagged as shipped |
|--|--|--|--|
| opened the inventory with the deleted lines (nine cases) | 27, of them 18 `quiet` | 27, of them 18 `quiet` | 11, of them 6 `quiet` |
| left it unopened (cases 04, 09, 12) | 9, of them 6 `quiet` | 5, of them 3 `quiet` | 5, of them 3 `quiet` |

The readers of the seven records found this from the kept call lists; the records of H-05, H-06 and H-07 state it, and H-07 stays a hypothesis, since 3 of the 12 readers of D-06 opened the deleted statements.

## What the run showed beside the seven lines

- In case 05 two of the three reviewers returned `plain` with an empty `target` for five listed sentences, and `check_trace.py` counts a verdict without a target as `rewrite`. One planted `plain` sentence and four sentences no writer planted ended as `REWRITE` that way; they are the one sound sentence of H-04 and four of the five other listed sentences rewritten.
- Each of the three readings alone ended 34 of 36 `trace` sentences as `REWRITE`, the number the three together gave. The two kept ones, both `quiet`, got `plain` from all three reviewers.
- In case 04 the cards of the arm with the deleted lines flagged none of the three `trace` sentences, and as shipped they flagged one; no sub-agent of that case opened the inventory with the deleted lines. Each card was read once.
- With the deleted lines D-02 flagged 25 of the 36 `trace` sentences, against 6 as shipped; D-06 flagged 5, against 7 as shipped.
- The cards flagged 15 of 36 `licensed` sentences as shipped and 16 with the deleted lines, most of them through D-06, whose rule is that a named alternative stands beside the fact that blocks it. The pass ended none of the 36 as `REWRITE`.
- The pass ended 22 of 23 `foil` sentences as `REWRITE`; the cards flagged 13 as shipped and 15 with the deleted lines. No hypothesis of this run carries a threshold for the `foil` sentences.
- The change of the repository's `README.md` that started this work was read the same three ways outside the run. `../../readme-observation/notes.md` holds what each way returned, and H-08 states the claim it suggests.

## The readers of the records

Each of the seven records was read by a reader that saw nothing of the work, by the definition of the plugin's `claim-skeptic` agent, on Claude Opus 5.5 at effort `xhigh`. The first reading found `fit: direct` on a scope wider than the bounds in all seven, and for H-07 a run that could not have refuted the claim; the records were changed and read again by fresh readers. The second reading held every rule for H-02 to H-06 and for the new line H-08; it asked H-01 to name the version of the script in its bounds and found that the protocol, as H-07's named test, could not refute H-07 on a rerun, so that line names no test and waits for one. `verdict-<id>.json` holds the verdict each record stands on and `verdict-<id>-first.json`, with `-second` for H-01 and H-07, the earlier ones.

## Departures from the protocol

`<case>.check.txt` is kept beside each `<case>.dispositions.json`; the protocol names the JSON alone. Nothing else departed.

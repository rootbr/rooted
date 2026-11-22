# The trace pass against planted sentences — protocol

The test of the seven hypotheses `H-01` to `H-07` of `maintenance/pending-evidence.md`. A change that replaces a rule can leave sentences that argue with the replaced text, which a reader of the new text never sees. Three ways of finding such sentences read the same documents: the trace pass, the audit's cards as shipped, and the same cards shown the lines the change deleted. Paths are relative to the skill directory unless they start at the repository root.

## What is under test

- **The trace pass** as the registering commit holds it, in three steps:
  1. `scripts/trace_list.py` lists the statements a change deleted and, as candidates, the added sentences that carry a cue of denial, contrast or history.
  2. Three reviewers, each with `../../agents/trace-reviewer.md` and in its own context, give every candidate the verdict `rewrite`, `licensed` with a quote, or `plain`.
  3. `scripts/check_trace.py` checks every quote and keeps a candidate only when all three readings keep it.
- **The deleted lines as a field of the audit's inventory**: the same cards, with the deleted statements of `trace_list.py` added to what each sub-agent is given.

The pass takes parts 1, 3 and 4 of the design in the repository's `research/2026-11-20_argument-with-an-absent-rule.md` § The design that follows, with the list built from cues alone. That note states the design as four hypotheses:

| Hypothesis of the note | Tested here as | What differs |
|--|--|--|
| H-a, the list holds the sentences | H-01 | the list is built from cues alone, and the threshold is H-01's |
| H-b, a reviewer who asks for the licence leaves fewer in place | H-03, H-06 | the comparison is with the audit's cards, as shipped and shown the deleted lines |
| H-c, three readings against one | none | the scorer prints the shares of each reading by itself, without a threshold |
| H-d, licensed denials are kept | H-04 | licensed and plain sentences are counted together, under H-04's bound |

Between the registering commit and the last run the three files of the pass and the cards D-01, D-02, D-06 and R-61 stay as they are; `git diff <registering commit> -- <those paths>` printing nothing is part of the result.

## Material

Twelve cases, written after the registering commit by writers that see neither the scripts nor the reviewer's instructions.

1. **Draw.** `absent_rule_eval.py draw` orders the domains of `evals/absent-rule/domains.txt` by the hash of the registering commit. The first twelve of sixteen drawn are the cases; the next four are the reserve, in that order.
2. **Writing.** For each drawn domain a writer receives `evals/absent-rule/case-brief.md` and the domain, and writes `old.md`, `new.md` and `labels.json` into `evals/absent-rule/cases/<rank>-<slug>/`. A case holds ten planted sentences, by the table under this list. The writer runs `absent_rule_eval.py validate` on its case until it exits 0.
3. **Checking the labels.** A second reader receives `evals/absent-rule/label-check-brief.md`, the case directory and the ten sentences without their classes, classifies each on its own and writes `labels-check.json`. `absent_rule_eval.py confirm` keeps the planted sentences to which both gave the same class. A case counts when `validate` exits 0, the checker finds that `new.md` outside the planted sentences says nothing of the old rule, and at least eight of its ten sentences count. A case that fails one of the three moves to `evals/absent-rule/replaced/`, and the next domain of the reserve takes its place, written and checked the same way. With the reserve used up the run counts the cases it has, and `notes.md` says so.
4. `evals/absent-rule/write-cases.js` dispatches the writers and the checkers; its header says how it is invoked. Writers run as the session's `brief-worker` type and checkers as its `brief-judge` type, both on Claude Opus 5.5, the writer at effort `high` and the checker at `xhigh`. Those two agent types belong to the operator's own configuration and lie outside this repository; a rerun elsewhere gives each brief to any agent that can read and write files.

| Class | Planted in a case | What the sentence does |
|--|--|--|
| `trace`, `named` | 1 | argues with the replaced rule and uses a name only that rule had |
| `trace`, `quiet` | 2 | argues with the replaced rule in the note's ordinary words |
| `foil` | 2 | sets its subject against a thing neither version of the note presents |
| `licensed` | 3 | denies or contrasts a thing an earlier sentence of the note presents |
| `plain` | 2 | says what the described thing does not do, against no other design |

## Arms

All three arms read the same `new.md` files, with sub-agents on Claude Sonnet 5.5 at effort `medium`.

- **The trace pass.** Per case: `scripts/trace_list.py --old old.md --new new.md` gives the list; three reviewers return three readings; `scripts/check_trace.py --min-readings 3 --json` gives the dispositions. `evals/absent-rule/run-trace-pass.js` dispatches the reviewers. Each is a sub-agent of the type `brief-worker`, which starts without the session's instruction files, told to open the agent's definition file and follow it, because a session resolves a plugin's agent types only from its installed copy.
- **The cards as shipped.** `scripts/audit-workflow.js` at the registering commit over the twelve `new.md` files as `doc` targets, with the cards D-01, D-02, D-06 and R-61 — the four whose subject is a superseded design, a foil or a negative — one reading each, and the inventory `absent_rule_eval.py inventory` builds from the static pre-pass.
- **The cards with the deleted lines.** The same run with the inventory of `absent_rule_eval.py inventory --deleted`, which adds each case's deleted statements.

The sub-agents of the two card arms receive the session's instruction files, as in any audit run from this session. The operator's files hold style rules on denials, so this difference favours the cards against the pass and is the same in both card arms.

## Measures and thresholds

`absent_rule_eval.py score` counts, over the planted sentences that count:

| Hypothesis | Measure | Holds when |
|--|--|--|
| H-01 | share of planted `trace` and of planted `foil` sentences on the list | at least 0.90 of each |
| H-02 | share of `trace` sentences that end as `REWRITE` under the pass | at least 0.80 |
| H-03 | that share for `quiet` traces, beside the share one of the four cards flags as shipped | the pass stands at least 0.20 above the cards |
| H-04 | share of `licensed` and `plain` sentences that end as `REWRITE` under the pass | at most 0.25 |
| H-05 | share of `quiet` traces one of the four cards flags with the deleted lines, beside the share as shipped | the deleted lines add at least 0.15 |
| H-06 | share of `quiet` traces that end as `REWRITE` under the pass, beside the share the cards flag with the deleted lines | the pass stands at least 0.15 above those cards |
| H-07 | share of `licensed` and `plain` sentences one of the four cards flags with the deleted lines, beside the share as shipped | the deleted lines add at most 0.10 |

A card flags a planted sentence when the text of one of its patches contains the sentence, lies inside it or shares a run of forty characters with it. A planted sentence the list misses counts as kept. The thresholds follow the cost of each error: a trace left in place reaches the reader the pass exists for, and a sound sentence rewritten costs its author one rewording. The comparisons are made on the quiet traces, the form the sentences of the case behind this test had. The thresholds rest on two dry cases outside the draw: on them the cards as shipped flagged every trace that used a name of the old rule and neither of the two quiet ones, and the cards shown the deleted lines flagged all three traces of the case that had quiet ones, as the pass did.

The scorer also prints, for information, the shares of each reading by itself, of the `named` traces and of the `foil` sentences in every arm, and the listed sentences no writer planted with the number of them that end as `REWRITE`. For H-03, H-05 and H-06, whose two shares are taken over the same quiet traces, it prints the traces only one arm caught and the two-sided exact p-value of McNemar's test over them; the test takes the traces as independent, and they stand two to a note.

## What each outcome decides

- H-05 and H-07 together support adding the deleted statements to the inventory of an audit.
- H-01, H-02, H-03, H-04 and H-06 together support the trace pass as a step of the skill. With H-06 refuted the pass adds too little to the cards shown the deleted lines to earn its three reviewers.

Whether a supported technique enters `SKILL.md` is the maintainer's decision.

## Runs and their record

One run: one pass of each arm over the twelve cases. A second run, if one is made, takes the next draw from the hash of the commit that registers it. Everything a run produced is kept under `evals/absent-rule/runs/run-1/`. The commands, from the repository root, with `E` for the skill directory, `A` for `$E/evals/absent-rule/absent_rule_eval.py` and `RUN` for the run directory:

```
python3 -I $A draw --seed <hash> --domains $E/evals/absent-rule/domains.txt --count 16 > $RUN/draw.txt
python3 -I $A validate --cues <case directories>
python3 -I $A confirm --run $RUN <case directories>
python3 -I $E/scripts/trace_list.py --old <case>/old.md --new <case>/new.md --out $RUN/<case>.list.json
python3 -I $A readings --result <output file of run-trace-pass.js> --run $RUN
python3 -I $E/scripts/check_trace.py --list $RUN/<case>.list.json --root . --min-readings 3 \
    --json $RUN/<case>.dispositions.json $RUN/<case>.reading-1.json $RUN/<case>.reading-2.json $RUN/<case>.reading-3.json
python3 $E/scripts/static-audit.py --target-type=doc <the new.md files> > $RUN/static.json
python3 -I $A inventory --static $RUN/static.json --out $RUN/inventory.md <case directories>
python3 -I $A inventory --static $RUN/static.json --out $RUN/inventory-deleted.md --deleted $RUN <case directories>
python3 -I $A baseline --result <output file of the audit over inventory.md> --out $RUN/baseline.json
python3 -I $A baseline --result <output file of the audit over inventory-deleted.md> --out $RUN/baseline-deleted.json
python3 -I $A calls --transcripts <transcript directory of a workflow run> --root . --label <prefix> --forbid <text> --out $RUN/<role>.calls.txt
python3 -I $A score --cases $E/evals/absent-rule/cases --run $RUN --out $RUN/results.json
```

Each audit target is named `<case>/new.md`, the name the scorer matches a patch to its case by. The three `calls` files list what every writer, checker and reviewer opened and ran: a writer opens its brief alone, a checker its brief and the two documents, a reviewer the instruction file, the list and the document, and the command exits 1 on a call outside that. Two more `calls` files list what the card sub-agents of each audit run opened, with `labels` and `old.md` as the forbidden texts. `notes.md` holds whatever departed from this protocol.

## Bounds

Generated notes of 60 to 90 lines in English, one replaced rule per note, ten planted sentences per note, sentences planted by a model and written to the same definitions of the four classes the reviewer judges by; twenty-four quiet traces at most, so one sentence moves a share by about four points; one reviewer model at one effort; each card read once. A result is a statement about these conditions.

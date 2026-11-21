# The record

## Contents

- Lines and files
- Fields by kind
- Fields a standing adds
- Tests
- Findings of the record check
- The reader's verdict

A record says what a rule rests on, in fields a script can check. It closes the rule's line: labelled fields separated by ` · `, the first of them `kind`. `scripts/check_record.py` checks records, and `scripts/check_verdict.py` checks the reader's answers about one record.

```
- **R-12** · <free text of the line> · kind: norm · issuer: IEEE · version: 1003.1-2024 · locator: §2.8.2 Exit Status for Commands
```

## Lines and files

- A rule line opens with `- **<id>**`; the id is unique among the rule lines of the files of one directory.
- Text between the id and the field `kind` is free: the script reads only the fields from `kind` to the end of the line.
- From `kind` on, every segment between ` · ` separators is `key: value` with a key of the tables below and a value that is present and holds no ` · `.
- A rule in force keeps its line in a provenance map, a file whose name matches `*provenance*.md`. A hypothesis, a contested claim and a refuted claim keep theirs in a list of hypotheses, a file whose name matches `pending-evidence*.md`, in the same directory as the map their rule will enter.

## Fields by kind

| Kind | Required fields | Optional fields |
|--|--|--|
| `decision` | `owner`, `goal` | `hypothesis` |
| `definition` | `term` | |
| `norm` | `issuer`, `version`, `locator` | |
| `claim` | `standing`, `measure`, `against`, `refuter`, one of `scope` and `event`, and the fields its standing adds | `threshold`, `runs`, `test`, `transfer`, `validity` |

A rule line takes the kind of what its rule rests on. A line that names a test of the rule's claim is a `claim`, also when it names a document beside the test. A line whose ground is a document that prescribes or describes the practice — a standard, a specification, official documentation, a style guide, a rule of a static analyser — is a `norm`. A line whose ground is the project's own choice is a `decision`, and a line that fixes a term is a `definition`. A run that left nothing to open or to rerun is no test here: its line takes the kind of the ground that remains, or its claim is recorded as a hypothesis.

- a line that cites a paper's measurement and a style guide: `claim`.
- a line that cites a style guide and a local run of which nothing was kept: `norm`.

A claim about one event — what caused one failure, what one change did, what one observed result means — is a claim that carries `event`; `references/method.md` § A claim about one event states its path, and the rows below and the tables of the next sections say what its fields hold.

| Field | Value |
|--|--|
| `owner` | who took the decision, by name or role |
| `goal` | what the decision is for |
| `hypothesis` | the id of the hypothesis record that states the untested claim behind the decision |
| `term` | the term the definition fixes |
| `issuer` | the body that publishes the document |
| `version` | the version, edition or date of the document as it was opened |
| `locator` | where the prescription stands in the document: a section, a clause, a rule id |
| `standing` | `hypothesis`, `supported`, `law`, `leading`, `contested` or `refuted` |
| `measure` | what is measured, in units a result can be read in; for a claim about one event, the trace that tells it from its rivals |
| `validity` | what checked that the measure follows what the claim is about, in one of the four forms below |
| `against` | what the technique is compared with; `none` for a claim that something exists or happens at all; for a claim about one event, its rival explanations by name, at least one |
| `scope` | the conditions the claim is made for: who, what, which version |
| `event` | for a claim about one event, in place of `scope`: the event and its date or identifier |
| `refuter` | the outcome that would refute the claim |
| `threshold` | the size of difference fixed before the test |
| `runs` | the number of repetitions, per arm for a comparison |
| `test` | one test or several joined by `; ` (section Tests) |
| `result` | what the tests showed, every run counted; a comparison of shares names the test and its p-value or interval |
| `bounds` | the conditions the tests ran under |
| `fit` | `direct` when the scope lies within the bounds, `transfer` when the rule is applied beyond them |
| `transfer` | under `fit: transfer`, what differs between the scope and the bounds |

`validity` takes one of four forms:

- `direct: <why the measure is the thing claimed>` — the claim is about the very quantity the measure reports;
- `probe: <what was changed in a known direction, and how the measure moved>` — a run of its own;
- `labels: <who labelled what, how many, and their agreement>` — labels made by a person, or confirmed blind by a second reader;
- `unchecked` — nothing checked the measure.

§ Fields a standing adds says where the field is required. Elsewhere it is optional: a hypothesis may plan it, and a record resting on someone else's test says what the source reports of its measure, or leaves the field out.

## Fields a standing adds

| Standing | Added required fields |
|--|--|
| `hypothesis` | with a test of our own named in `test`: `threshold` and `runs`, except on a claim about one event; otherwise none |
| `supported` | `test`, `result`, `bounds`, `fit`; with a test of our own also `threshold`, `runs` and a `validity` other than `unchecked` |
| `law` | the fields of `supported`, with two tests or more |
| `leading` | `event`, `test`, `result`, `bounds` |
| `contested` | `test` with two tests or more, `result` |
| `refuted` | `test`, `result`, `bounds` |

## Tests

A test is written in one of four forms.

- `own <path>`: a test of our own. The path, relative to the repository root, names the file that holds or runs it, and that file exists. For a claim about one event it names the file that keeps the trace: a log, a dump, a recording.
- `external <locator> first-hand`: someone else's test, opened, with its comparison, measure, sample and result found in the source.
- `external <locator> abstract`: someone else's test in a source that passed peer review, read by its abstract alone — a journal article, a paper in reviewed proceedings, an encyclopedia entry under editorial review. A preprint read by its abstract is a `relay`.
- `external <locator> relay`: a source that was read about and has yet to be opened. It is a lead for a later search.

A `supported` or `law` standing rests on one test at least that is `own`, `first-hand` or `abstract`; a `leading` standing on one that is `own` or `first-hand`.

```
- **H-03** · kind: claim · standing: hypothesis · measure: share of runs in which the agent reads the file before its first edit · against: the same prompt without the paragraph · scope: coding agents on one named model editing a repository file · refuter: the share with the paragraph is under ten points above the share without it · threshold: ten points · runs: ten per arm · test: own checks/read-before-edit/cases.json
- **H-04** · the queue overflow caused the outage · kind: claim · standing: hypothesis · measure: the lock wait time in the database log during the outage · against: a lock in the database · event: the outage of the order service on 2026-10-14, incident 412 · refuter: the lock wait time rises above its usual level before the queue fills
```

## Findings of the record check

Every finding is one line, `<path>:<line>: <CODE>: <message>`. The exit status is 0 with no finding, 1 with a finding, 2 on unreadable input, wrong usage or a failed git command.

| Code | Reported for |
|--|--|
| `KIND` | a record whose `kind` is absent or outside the four kinds |
| `FIELD` | a required field absent; a key outside the tables; an empty value; a key written twice; a field its kind does not take; a claim with neither or both of `scope` and `event`; `against: none` beside `event` |
| `STANDING` | a `standing` outside the six; the words `proved` or `proven` in `standing` or `result`; beside `event`, a standing other than `hypothesis`, `leading`, `contested` or `refuted` |
| `TEST` | a test outside the four forms; fewer tests than the standing takes by the table above |
| `SUPPORT` | a `supported`, `law` or `leading` standing without the test the section Tests asks of it |
| `VALIDITY` | a `validity` outside the four forms; a `supported` or `law` claim whose `test` holds an `own` test and whose `validity` is absent or `unchecked` |
| `OWN` | an `own` test whose path does not exist under the root |
| `FIT` | a `fit` outside the two values; `fit: transfer` without `transfer` |
| `DUP` | a recorded line whose id stands on another rule line of the same directory |
| `NORECORD` | under `--require`, or on an added or changed line, a rule line without a record |
| `PREDICTION` | a claim with an `own` test and a standing other than `hypothesis` whose id, at the base revision and in the same directory, is absent or carries a different `measure`, `against`, `scope`, `event`, `refuter` or `threshold` |
| `ERASED` | an id whose record at the base revision had the standing `refuted` or `contested`, or carried a `result` whatever its standing, and whose line is gone from its directory |

`NORECORD` on changed lines, `PREDICTION` and `ERASED` compare two states of the files, so they run in the two comparing modes. `--changed` sets the working tree against a base revision, `HEAD` unless `--base` names another; `--staged` sets the index against `HEAD`. With no file named, both modes check the files that match the two name patterns in either state, so a deleted map still answers for its records. A map that git reports as renamed is compared with its text under the earlier name, and a map whose text changed too much for git to pair it is paired through the directory its neighbours moved from, so a directory that moves keeps the history of its records. `PREDICTION` is what puts a prediction into history before its result: the hypothesis is committed first, and the commit that adds the result finds it at the base revision unchanged.

## The reader's verdict

The independent reader returns one JSON object for one record, with an answer for each of the seven rules of `references/method.md`: 1 facts apart from decisions, 2 refutability, 3 severity of the test, 4 reproducibility, 5 bounds of transfer, 6 no fitting, 7 revision. A verdict is `holds`, `fails` or `not-applicable`; the table says where each rule applies. This section fixes the shape of a verdict, and what each rule asks stands in `references/method.md`.

| Rule | `decision`, `definition` | `norm` | `claim` as `hypothesis` | `claim` in any other standing |
|--|--|--|--|--|
| 1 | applies | applies | applies | applies |
| 2 | not applicable | not applicable | applies | applies |
| 3, 5, 6 | not applicable | not applicable | applies when a test is planned | applies |
| 4 | not applicable | applies | applies when a test is planned | applies |
| 7 | not applicable | not applicable | applies | applies |

A claim at `leading` takes the last column.

`scripts/check_verdict.py` prints one line per finding, `<CODE>: <message>`, and exits by the convention of the record check: 0 means that every applicable rule holds.

| Code | Reported for |
|--|--|
| `SHAPE` | an object without `id`, `kind` or `answers`; a claim without `standing`; a `kind` or `standing` outside the vocabulary; a rule of 1–7 absent or given twice; a verdict outside the three values |
| `QUOTE` | a `holds` without a quote |
| `MISSING` | a `fails` without `missing` |
| `APPLY` | a `not-applicable` where the rule applies, a `holds` or `fails` where it is not applicable; on a hypothesis rules 3, 4, 5 and 6 take any of the three verdicts, since the object does not say whether a test is planned |
| `FAILS` | an applicable rule whose verdict is `fails` |

```json
{
  "id": "H-03",
  "kind": "claim",
  "standing": "hypothesis",
  "answers": [
    {"rule": 1, "verdict": "holds", "quote": "<the words of the record or the source the verdict rests on>", "missing": ""},
    {"rule": 2, "verdict": "fails", "quote": "", "missing": "<what the record would have to say>"},
    {"rule": 3, "verdict": "not-applicable", "quote": "", "missing": ""}
  ]
}
```

# Maintaining handing-over-to-readers

Nothing under `maintenance/` or `evals/` is read or executed in a run of the skill. Paths are relative to the skill directory; `../../hooks/hooks.json` is the plugin's hook file.

## What changes together

- A rule: its numbered line in `references/rules.md`, its line in `maintenance/rules-provenance.md`, and the rules table of the research note `research/2026-10-21_reading-contract-evidence.md` (§Rules and data) at the repository root. A rule number never moves, because `scripts/check_question.py`, `scripts/check_report.py` and the eval expectations name rules by number; a rule that leaves keeps its number as a gap. A held-back rule or clause waits in `maintenance/pending-evidence.md` and enters `references/rules.md` with its bracket once an opened source or an eval assertion backs it.
- A check: the script and its test module in `maintenance/tests/`. A script carries no check for a rule or clause held in `maintenance/pending-evidence.md`.
- A matched label or word: the `WORDS` list of the script and the test that uses it; a user's lexicon file adds a language's alternatives without a change here.
- The card form: `scripts/check_question.py` (`problems`, `GUIDANCE`), `maintenance/tests/test_check_question.py`, `../../hooks/hooks.json`, and the eval `question-to-operator-with-default`.
- The report template: `references/report-template.md`, the first-page patterns `FIRST_PAGE` and `STATUS` of `scripts/check_report.py`, and the eval `operator-report-with-failing-build`.
- A source: a reference file carries the rule and its numbers alone; the sources with their locators, the pointer to the quoted fragment, the evidence class, the fit and the eval that tested the rule stand on the rule's line in `maintenance/rules-provenance.md`, and rule g of the repository's `check-skill-layout.py` rejects a citation bracket, an eval tag or a fetch marker in a run-set file. The repository `README.md` §Handing-over-to-readers sources lists the first-hand academic and standard sources.

## Tests

From the repository root:

```
python3 -m unittest discover -s plugins/evidence-based-authoring/skills/handing-over-to-readers/maintenance/tests -p 'test_*.py'
```

The test fixtures are English reports and cards; the `Lexicon` cases add a label or a word through a lexicon file; the `--hook` tests run the script as the hook runs it.

## Evals

`evals/evals.json` holds the three evals in skill-creator's eval format: the prompt, the fixture files under `evals/fixtures/`, the expected output and the expectations. A run writes `<iteration>/eval-*/{with_skill,without_skill}/run-*/outputs/`, and `python3 evals/grade.py <iteration>` writes each run's `grading.json` from the expectations of `evals.json`, matched by the eval directory's name. The language of the recorded run `evals/runs/iteration-1/` is stated in its `benchmark.md`. `evals/fixtures/repo/build.log` line 4 names `RouterTest` line 24, one line above the assertion, because the recorded report quotes that log line as its fragment; a corrected log is a new iteration. Re-grading `evals/runs/iteration-1` reproduces the pass rates of its `benchmark.md`.

## Layout

- `maintenance/rules-provenance.md` — one line per shipped rule and per "What the research adds" bullet: its sources with locators, the formulation, the evidence class and fit, the caveat.
- `maintenance/pending-evidence.md` — the rules and clauses held back, each with what was searched and what would admit it.
- `maintenance/tests/` — the unit tests of both scripts, the hook mode included.

Who reads or runs every other file of the skill, and when: `README.md` §Layout.

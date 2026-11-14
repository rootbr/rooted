# Maintaining handing-over-to-readers

Nothing under `maintenance/` or `evals/` is read or executed in a run of the skill. Paths are relative to the skill directory; `../../hooks/hooks.json` is the plugin's hook file.

## What changes together

- A rule: its numbered line in `references/rules.md`, its line in `maintenance/rules-provenance.md`, and the rules table of the research note `research/2026-10-21_reading-contract-evidence.md` (§Rules and data) at the repository root; a clause of `references/explaining.md` or `references/media.md` has its line in `maintenance/rules-provenance.md` and its row in `research/2026-11-07_report-forms-evidence.md` (§ Rules and data). A rule number never moves, because `scripts/check_question.py`, `scripts/check_report.py` and the eval expectations name rules by number; a rule that leaves keeps its number as a gap. A held-back rule or clause waits in `maintenance/pending-evidence.md` and enters its reference file with its provenance line once an opened source or an eval assertion backs it.
- A check: the script and its test module in `maintenance/tests/`. A script carries no check for a rule or clause held in `maintenance/pending-evidence.md`.
- A matched heading or word: the `WORDS` list of the script and the test that uses it; a user's lexicon file adds a language's alternatives without a change here. A key that leaves `WORDS` makes every lexicon still carrying it unreadable (exit 2), so its removal is announced to the users of the lexicon.
- The card form: `scripts/check_question.py` (`problems`, `GUIDANCE`), `maintenance/tests/test_check_question.py`, `../../hooks/hooks.json`, the card bullet of `SKILL.md` § 5, rule 18 of `references/rules.md`, and the eval `question-to-operator-with-default`.
- The report template: `references/report-template.md`, `check_story` and `LOOK_HEADING` of `scripts/check_report.py` with the `StoryForm` tests, `assets/page-body-example.html`, which draws the same report as a page, and the eval `operator-report-with-failing-build`.
- A delivery form: its row and section in `references/media.md`, the form bullet of `SKILL.md` § 5, the skill's description and its line in `maintenance/rules-provenance.md`.
- The ear rule of the story: `references/explaining.md` § The story, the worked report of `references/report-template.md`, `STORY_SENTENCE_WORDS` and `STORY_OPENING_SENTENCES` of `scripts/check_report.py` and the `StoryForm` tests.
- The page tooling: `references/media.md` § The page with voice, `references/page.md`, `scripts/voice_cues.py`, `scripts/build_page.py`, `assets/page-template.html` and `assets/page-body-example.html`, with `maintenance/tests/test_voice_cues.py`, `maintenance/tests/test_build_page.py`, `maintenance/tests/test_page_behaviour.py` and `maintenance/tests/fixtures/`. The behaviour tests run the built page in a headless Chrome (`$CHROME`, the macOS application, or `google-chrome`, `chromium` or `chromium-browser` on `PATH`) with the audio element stubbed, and are skipped where no such browser is found; a change to the pause, the comments or the answer of the template is checked there. `scripts/build_page.py` imports `LOOK_HEADING` from `scripts/check_report.py`, so the heading of a report's closing list changes in both.
- The cold read: `SKILL.md` § 6, `references/explaining.md` § The cold read, the plugin's `../../agents/cold-reader.md`, `scripts/check_cold_read.py` with `maintenance/tests/test_check_cold_read.py`, and the measurement `evals/cold-read/` graded by `evals/grade_cold_read.py` (`maintenance/tests/test_grade_cold_read.py`). A change to the agent's instructions or to the questions is a new iteration under `evals/cold-read/runs/`, which keeps the instructions and the questions it ran with beside its answers; `evals/cold-read/plant.py` writes the planted reports and the blind copies.
- The reader record and the intake: `references/intake.md`, `SKILL.md` § 2, the `reader` commands of `scripts/records.py` with `maintenance/tests/test_records.py`, and the Intake lines of `maintenance/rules-provenance.md`.
- The ledger and the gate: `SKILL.md` §§ 4 and 7, rules 3 and 25 of `references/rules.md`, the `ledger` commands of `scripts/records.py`, the gate in the hook mode of `scripts/check_question.py` with its tests, both entries of `../../hooks/hooks.json`, and the Gate lines of `maintenance/rules-provenance.md`. The floor and the count of candidates are house defaults held in `maintenance/pending-evidence.md`.
- The usage journal: `scripts/feedback.py` with its closed `SCHEMA`, the `journal()` call of every other script, `maintenance/tests/test_feedback.py`, `SKILL.md` § 8, `README.md` § Feedback and the issue form `.github/ISSUE_TEMPLATE/handing-over-feedback.yml` at the repository root, whose file name the summary's address carries. A script records an event or a field only after `SCHEMA` holds it: a line outside the schema is dropped.
- A source: a reference file carries the rule and its numbers alone; the sources with their locators, the pointer to the quoted fragment, the evidence class, the fit and the eval that tested the rule stand on the rule's line in `maintenance/rules-provenance.md`, and rule g of the repository's `check-skill-layout.py` rejects a citation bracket, an eval tag or a fetch marker in a run-set file. The repository `README.md` §Handing-over-to-readers sources lists the first-hand academic and standard sources.

## Tests

From the repository root:

```
python3 -m unittest discover -s plugins/evidence-based-authoring/skills/handing-over-to-readers/maintenance/tests -p 'test_*.py'
```

The test fixtures are English reports and cards; the `Lexicon` cases add a heading or a word through a lexicon file and resolve the default lexicon under a temporary `XDG_CONFIG_HOME`, never the user's own; the `--hook` tests run the script as the hook runs it; every test module points `HANDOVER_FEEDBACK_DIR` at a temporary directory, never the user's own journal.

## Evals

`evals/evals.json` holds the six evals in skill-creator's eval format: the prompt, the fixture files under `evals/fixtures/`, the expected output and the expectations. A run writes `<iteration>/eval-*/{with_skill,without_skill}/run-*/outputs/`, and `python3 evals/grade.py <iteration>` writes each run's `grading.json` from the expectations of `evals.json`, matched by the eval directory's name. A run's `benchmark.md` states its language, its baseline and every correction made to the grader after its first grading. Re-grading `evals/runs/iteration-2` reproduces the pass rates of its `benchmark.md`; a changed fixture or prompt is a new iteration. A report eval is graded by `story_facts` of `evals/grade.py` plus the facts of its own fixture; an expectation tag `E<n>` in `maintenance/rules-provenance.md` counts the expectations of `evals.json` in order.

## Layout

- `maintenance/rules-provenance.md` — one line per shipped rule, per "What the research adds" bullet and per clause of `references/explaining.md` and `references/media.md`: its sources with locators, the formulation, the evidence class and fit, the caveat.
- `maintenance/pending-evidence.md` — the rules and clauses held back or shipped on practice alone, each with what was searched and what would admit it.
- `maintenance/tests/` — the unit tests of the scripts, the hook mode included; `maintenance/tests/fixtures/` holds the files the page tests read.

Who reads or runs every other file of the skill, and when: `README.md` §Layout.

# handing-over-to-readers

Skill for Claude Code that shapes what an agent hands to a human — a report, a question, a client's question list, a PR description — into a handover the reader checks against evidence; paths in this file are relative to this directory. A report opens with a first page of five lines (the risk, the reader's action, what is not done, the condition under which the conclusion is wrong, a status from exit codes); every claim about code carries a `path:line` anchor with the fragment of that line; candidate questions pass filters (already answerable, changes nothing, reversible, internal) before they are asked, and those that survive are written as decision cards; the agent takes reversible decisions by default and records them in a registry. The research behind the rules is the note `research/2026-10-21_reading-contract-evidence.md` at the repository root; the sources of each rule stand on its line in `maintenance/rules-provenance.md`.

## Addressees

Two profiles set what the reader can open. The `operator` opens files and runs commands, so his claims carry anchors; a `client` opens nothing of ours, so his list carries no paths, dates, deadlines or effort estimates. `SKILL.md` §1 defines them, and `references/rules.md` tabulates what each profile changes.

## Checks

```
python3 -I scripts/check_report.py --profile operator --root <repo> <report.md>
python3 -I scripts/check_report.py --profile client <questions.md>
python3 -I scripts/check_question.py --questions <card.json>
```

`check_report.py` exits 0 when the text has no error, 1 on an error (or a warning under `--strict`), 2 on unreadable input. `check_question.py` exits 0 when the card passes, 1 on a problem, 2 on unreadable input. Both match English labels and words; a lexicon file adds another language's — `--lexicon FILE`, or `$XDG_CONFIG_HOME/handing-over-to-readers/lexicon.json` when it exists, a JSON object with a section per script that maps a key of the script's `WORDS` to extra regex alternatives.

## Hook

The plugin's `../../hooks/hooks.json` registers a PreToolUse hook on `AskUserQuestion` that runs `scripts/check_question.py --hook`. A card outside the form exits 2 with its problems and the card form on stderr, so Claude Code blocks the question and shows the guidance to the model; a passing card and unreadable input exit 0.

## Eval

Three evals ran once with and once without the skill — a client question list, an operator report on a failing build, a question to the operator with a default decision — and `evals/grade.py` grades them by the two check scripts and pattern assertions: with the skill 8/8, 7/7 and 6/6, without it 6/8, 2/7 and 2/6. The recorded run lives in `evals/runs/iteration-1/`, and `python3 evals/grade.py evals/runs/iteration-1` reproduces its grades.

## Layout

This skill's instance of the repository `README.md` §Skill layout:

| Path | Who reads or runs it | When |
|--|--|--|
| `SKILL.md` | the session | on invocation, whole |
| `references/rules.md` | the session | collecting candidates, running the filters, writing an item |
| `references/evidence.md` | the session | deciding whether a claim's support counts as evidence |
| `references/report-template.md` | the session | writing a report to the operator |
| `scripts/check_report.py` | the session | before a report or a client list is delivered |
| `scripts/check_question.py` | the session; the plugin hook with `--hook` | before and on every `AskUserQuestion` |
| `maintenance/README.md` | a maintainer | before changing a rule, a check, the card form or the template |
| `maintenance/rules-provenance.md` | a maintainer | adding a rule or re-verifying its source |
| `maintenance/pending-evidence.md` | a maintainer | admitting a held-back rule or clause |
| `maintenance/tests/` | a maintainer | after any script change |
| `evals/evals.json`, `evals/fixtures/` | a maintainer | re-running the evals |
| `evals/grade.py` | a maintainer | grading a run |
| `evals/runs/iteration-1/` | a maintainer, a reviewer | checking a rule that rests on the eval |

# handing-over-to-readers

Skill for Claude Code that shapes what an agent hands to a human — a report, an explanation, a question, a client's question list, a PR description — so the reader understands what happened, checks the claims against evidence and decides; paths in this file are relative to this directory. An explanation of a mechanism for a team is a page with voice whose first part gives the mechanism whole, its rule as pseudocode of a few steps with what each line needs standing at that line, and whose later parts hold only what can be understood apart from it; a table after the first part gives each reader's question with the place that answers it, a claim about code opens its code where it stands, and a map at the side of the page lists every part with its figures (`references/explainer.md`). A report to the operator is a story written for the ear: an opening paragraph that gives the whole matter, parts under short headings with one picture each, the reader's decision last with its options in a block, then the list "Where to look" with `path:line` anchors, the fragment of each line and the checks with their exit codes. It goes out as text in the chat, and also as a page with voice when a figure shows its mechanism or it ends in a decision among options; the reader's word overrides that default. On the page a button at the heading of each part speaks that part, that button and the Space key pause the voice, and a selected piece of the text shows two buttons, one that copies it and one for the reader's comment, which the copied answer carries. Candidate questions pass filters (already answerable, changes nothing, reversible, internal) before they are asked, and those that survive are written as decision cards; the agent takes reversible decisions by default and records them in a registry. The research behind the rules is in the notes `research/2026-10-21_reading-contract-evidence.md`, `research/2026-11-07_report-forms-evidence.md`, `research/2026-11-14_explanation-page-evidence.md` and `research/2026-11-22_explanation-page-editing-evidence.md` at the repository root; the sources of each rule stand on its line in `maintenance/rules-provenance.md`.

## Addressees

Two profiles set what the reader can open. The `operator` opens files and runs commands, so his claims carry anchors; a `client` opens nothing of ours, so his list carries no paths, dates, deadlines or effort estimates. `SKILL.md` §1 defines them, and `references/rules.md` tabulates what each profile changes.

## Checks

```
python3 -I scripts/check_report.py --profile operator --root <repo> <report.md>
python3 -I scripts/check_report.py --profile client <questions.md>
python3 -I scripts/check_question.py --questions <card.json>
python3 -I scripts/check_cold_read.py --report <report.md> --questions <questions.json> --answers <cold.json>
python3 scripts/check_page.py <page.html> --shots <dir>
```

`check_report.py` exits 0 when the text has no error, 1 on an error (or a warning under `--strict`), 2 on unreadable input. `check_question.py` exits 0 when the card passes, 1 on a problem, 2 on unreadable input. Both match English headings and words; a lexicon file adds another language's — `--lexicon FILE`, or `$XDG_CONFIG_HOME/handing-over-to-readers/lexicon.json` when it exists, a JSON object with a section per script that maps a key of the script's `WORDS` to extra regex alternatives (`WHERE_TO_LOOK` for the heading of a report's closing list). `check_cold_read.py` checks the answers a cold reader gave to the reader's questions from the report alone: it exits 0 when every question has an answer with a quoted sentence that stands in the report, 1 when a question is left without one, 2 on unusable input; the terms the reader lists as unexplained are printed and change no exit code. `check_page.py` opens a copy of a built page in a Chrome or Chromium without a window (`--chrome` or `$CHROME` names it): it exits 0 when the page loads without a script error and no text runs outside the frame of its figure, 1 on a finding, 2 on an unreadable page or an unwritable directory and 3 when no usable browser is found; with `--shots` it writes a picture of every part in the light and in the dark theme.

## Hook

The plugin's `../../hooks/hooks.json` registers a PreToolUse hook on `AskUserQuestion` that runs `scripts/check_question.py --hook`. A card outside the form exits 2 with its problems and the card form on stderr, so Claude Code blocks the question and shows the guidance to the model; a passing card and unreadable input exit 0. The hook calls `python3`; on Windows it also needs Git for Windows (§ Another language, another system). After the form check the same hook searches the project's ledger for earlier answers that may cover the card and returns the card to the agent once with what it found; a second hook, PostToolUse on `AskUserQuestion`, runs `scripts/records.py ledger capture --hook` and writes each answer into the ledger. Neither blocks a question because of its own failure. Two limits come from Claude Code and not from the skill: on a login without managed settings, a `managed-mcp.json` file or a Team or Enterprise account, an installed mod that handles `tool.check` can approve a call that a PreToolUse hook blocked ([Configure permissions](https://code.claude.com/docs/en/permissions), "Precedence among rules, hooks, and mods"), so such a mod can let through a card the hook returned; and a question asked in prose never reaches the hook.

## Records

`scripts/records.py` keeps two JSON Lines files. The reader record is one private file a person, `$XDG_DATA_HOME/handing-over-to-readers/reader.jsonl`: for a topic, what the reader holds and lacks, what he does with a result, the depth he wants, the basis and the date; the script refuses a file that a repository would track. The ledger is the project's, `.claude/handing-over-to-readers/ledger.jsonl`: every answer the reader gave on a card, every closure and every default decision, with its date, basis, what it applies to, what overturns it and its status. `find` scores two sentences by the character trigrams they share, divided by the geometric mean of their two counts, so that a short sentence does not match a long one on a few shared trigrams. In the ledger every scored pair holds a question, the last sentence of a card: the question of the query against each sentence of the record, and each sentence of the query against the question of the record, because the sentences of the card form repeat from card to card and the question is a card's own. Two cards whose closing questions are too short to match by are compared whole. In the reader record every sentence of the query meets every sentence of the record's topic and items. `find` prints the records at or above a floor of 0.37, and the agent decides what a found record means. The score is not weighted by the rarity of a word, since a project's ledger holds few records. `references/intake.md` and `SKILL.md` §§ 2, 4 and 7 say when each command runs.

## Feedback

Claude Code reports nothing of a plugin's use to its author, and the skill sends nothing either. Three things let a user tell how it works for him:

- **A usage journal on his machine, off until he turns it on.** `python3 -I scripts/feedback.py on` starts it and `off` stops it; `status` and `reset` show and delete it. While it is on, every script of the skill appends one line to `$XDG_STATE_HOME/handing-over-to-readers/journal.jsonl` (`$HANDOVER_FEEDBACK_DIR` names another directory): the day, the plugin version, the event and its counts and rule codes. The schema is closed, so no script can write a text, a path or a name into it.
- **A summary he reads before it goes anywhere.** `python3 -I scripts/feedback.py summary` prints counts without dates: reports checked and their most frequent rule codes, cards passed and returned, reader lookups and intakes, ledger lookups, cold reads, pages, page checks and voice.
- **A form in the repository.** The summary ends with the address of the issue form `handing-over-feedback.yml`; he pastes the summary there and says in his own words what worked and what got in the way.

The switch is a file that a command writes, and not an option asked at installation: a plugin's `userConfig` value reaches hook processes, while the scripts also run from the session's shell.

## Another language, another system

The rules are the same in every language; three files carry the language. `lexicon.json` adds a language's words to the English ones the checks match, per key: the heading of the closing list, the words for an exit code and a self-report, the words that say why a question is asked. `page-strings.json`, or `--strings`, replaces the labels of the page; a key the page has stopped showing is read with a warning and dropped. The voice is whatever the synthesiser named on the command line speaks.

A German report, question card, voice and page were built this way on macOS with a German lexicon and German page strings; two commands voiced the story, `espeak-ng -v de -w {out} {text}` and `say -v Anna --data-format=LEI16@22050 -o {out} {text}`. The warning thresholds (three sentences of opening, twenty words a sentence) were read by one reader in Russian and run by agents in English; in German they are untested.

Nothing here ran on Windows. What the caller needs there, and what the skill prepares:

- **Required: Git for Windows, and `python3` on `PATH`.** The commands and the hook call `python3`. A hook that cannot start is a non-blocking error under Git Bash: the question goes out unchecked. Where Git Bash is absent, Claude Code blocks the call, so no question reaches the reader until Git for Windows is installed ([Claude Code hooks reference](https://code.claude.com/docs/en/hooks), "Failed hooks on Windows without Git Bash").
- The four scripts set their standard streams to UTF-8, because Python gives a pipe the system code page there; the tests run them with such a code page set.
- A path with backslashes in `--tts-command` is quoted or written with forward slashes: the line is split like a shell line, and an unquoted backslash is dropped.

## Eval

Six evals ran once with and once without the skill — a client question list, a question to the operator with a default decision, and four operator reports (a failing build, a retry that breaks another team's test, a rename with a stale override, an upgrade that silences an alert) — and `evals/grade.py` grades them by the two check scripts and pattern assertions: with the skill 52 of 52 expectations, without it 20 of 52. The run lives in `evals/runs/iteration-2/`; its `benchmark.md` states what the baseline was and which checks of the grader were corrected after the first grading.

The cold read has its own measurement: four of those reports, each intact and with one of three omissions planted, read blind by a fresh agent. With the shipped instructions it marked the missing decision in 4 of 4 and the missing cause in 4 of 4, marked nothing on the intact reports and noticed none of the 4 removed introducing sentences (`evals/cold-read/runs/iteration-3/grading.json`; `python3 evals/grade_cold_read.py evals/cold-read/plants.json evals/cold-read/runs/iteration-3` reproduces it). The run before it, with the same questions and the instructions as they stood before the context audit's wording fixes, came out the same in all sixteen cells (`runs/iteration-2`). Two other reader models with the shipped instructions (`runs/iteration-4`, `runs/iteration-5`) marked the decision and the cause in 4 of 4 as well, noticed 1 of the 4 removed introducing sentences, and each marked one intact report on the question about what is unverified; `evals/cold-read/runs/README.md` lists the iterations.

On real reports the read is a weaker signal. Sixty closing messages from one operator's stored sessions, thirty he asked back about and thirty he approved, were each read once against the six default questions: the read left a question open in 58 of them, and of the thirty things he asked back about it named 8 and touched 11 more (`research/2026-11-07_report-forms-evidence.md` § The cold read on real reports). Those reports predate the story form, and their texts stay outside the repository.

## Layout

This skill's instance of the repository `README.md` §Skill layout:

| Path | Who reads or runs it | When |
|--|--|--|
| `SKILL.md` | the session | on invocation, whole |
| `references/explaining.md` | the session | collecting the reader's questions and his terms, writing the story, its pictures and the list "Where to look" |
| `references/explainer.md` | the session | writing an explanation of a mechanism for several readers |
| `references/intake.md` | the session | deciding whether the reader is known, holding the intake dialogue, keeping the reader record |
| `references/media.md` | the session | choosing the form of delivery; the rules of the page with voice |
| `references/report-template.md` | the session | writing a report to the operator |
| `references/rules.md` | the session | collecting candidates, running the filters, writing an item |
| `references/evidence.md` | the session | deciding whether a claim's support counts as evidence |
| `references/page.md` | the session | writing the body of a page with voice |
| `scripts/check_report.py` | the session | before a report or a client list is delivered |
| `scripts/check_question.py` | the session; the plugin hook with `--hook` | before and on every `AskUserQuestion` |
| `scripts/check_cold_read.py` | the session | before a report with a decision, or a page, is delivered, and on the first part of an explanation: checks the cold reader's answers, and the steps of its retelling, against the text |
| `../../agents/cold-reader.md` | the session, as a dispatched agent | the cold read: answers the reader's questions from the text alone and, when asked, retells a mechanism by its steps |
| `scripts/records.py` | the session; the plugin hooks | looking the reader up before a long deliverable and recording an intake; searching and writing the project's ledger of answers; `ledger capture --hook` after every `AskUserQuestion` |
| `scripts/feedback.py` | the session, at the reader's word; every other script through its `journal()` call | turning the usage journal on or off, printing its summary; one journal line a run while it is on |
| `scripts/voice_cues.py` | the session | voicing a story for the page with voice: writes the audio and the time of every sentence |
| `scripts/build_page.py` | the session | building the page with voice: numbers the sentences of the body the agent wrote, writes the story for the voice and the page's text, joins the page template, the body and the cues, resolves the references the body names, and refuses a body that breaks the form, holds a barred word of the list of terms or a reference that does not resolve, or, for an explanation, breaks the order of its blocks |
| `scripts/check_page.py` | the session | after a page is built: opens it in a browser without a window, reports script errors and text outside a figure's frame, writes a picture of every part |
| `assets/page-template.html` | `scripts/build_page.py` | on every page build |
| `assets/page-body-example.html` | the session | writing the body of a page, as a worked example |
| `maintenance/README.md` | a maintainer | before changing a rule, a check, the card form, the template or the page tooling |
| `maintenance/rules-provenance.md` | a maintainer | adding a rule or re-verifying its source |
| `maintenance/pending-evidence.md` | a maintainer | to see which claims behind a rule or clause wait for a test and which tests were found, or admitting a held-back rule or clause |
| `maintenance/citations.json` | a maintainer | to check that the quoted words of the two files stand in their sources |
| `maintenance/tests/`, `maintenance/tests/fixtures/` | a maintainer | after any script or template change |
| `evals/evals.json`, `evals/fixtures/` | a maintainer | re-running the evals |
| `evals/grade.py` | a maintainer | grading a run |
| `evals/runs/iteration-2/` | a maintainer, a reviewer | checking a rule that rests on the eval |
| `evals/cold-read/` (`plants.json`, `plant.py`, `questions.json`, the four cases, `runs/`), `evals/grade_cold_read.py` | a maintainer | measuring the cold read on reports with planted omissions |
| `evals/retelling/` (`README.md`, `plants.json`, the two questions files, the four cases, `runs/`), `evals/grade_retelling.py` | a maintainer | measuring whether a retelling of a first part marks a step the text leaves out |
| `evals/explainer-reading/protocol.md` | a maintainer and the repository's owner | the two readings of the rebuilt explanation page and what each counts |

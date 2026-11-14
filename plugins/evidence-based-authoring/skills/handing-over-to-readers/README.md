# handing-over-to-readers

Skill for Claude Code that shapes what an agent hands to a human — a report, an explanation, a question, a client's question list, a PR description — so the reader understands what happened, checks the claims against evidence and decides; paths in this file are relative to this directory. A report to the operator is a story written for the ear: an opening paragraph that gives the whole matter, parts under short headings with one picture each, the reader's decision last with its options in a block, then the list "Where to look" with `path:line` anchors, the fragment of each line and the checks with their exit codes. It goes out as text in the chat, and also as a page with voice when a figure shows its mechanism or it ends in a decision among options; the reader's word overrides that default. Candidate questions pass filters (already answerable, changes nothing, reversible, internal) before they are asked, and those that survive are written as decision cards; the agent takes reversible decisions by default and records them in a registry. The research behind the rules is in the notes `research/2026-10-21_reading-contract-evidence.md` and `research/2026-11-07_report-forms-evidence.md` at the repository root; the sources of each rule stand on its line in `maintenance/rules-provenance.md`.

## Addressees

Two profiles set what the reader can open. The `operator` opens files and runs commands, so his claims carry anchors; a `client` opens nothing of ours, so his list carries no paths, dates, deadlines or effort estimates. `SKILL.md` §1 defines them, and `references/rules.md` tabulates what each profile changes.

## Checks

```
python3 -I scripts/check_report.py --profile operator --root <repo> <report.md>
python3 -I scripts/check_report.py --profile client <questions.md>
python3 -I scripts/check_question.py --questions <card.json>
python3 -I scripts/check_cold_read.py --report <report.md> --questions <questions.json> --answers <cold.json>
```

`check_report.py` exits 0 when the text has no error, 1 on an error (or a warning under `--strict`), 2 on unreadable input. `check_question.py` exits 0 when the card passes, 1 on a problem, 2 on unreadable input. Both match English headings and words; a lexicon file adds another language's — `--lexicon FILE`, or `$XDG_CONFIG_HOME/handing-over-to-readers/lexicon.json` when it exists, a JSON object with a section per script that maps a key of the script's `WORDS` to extra regex alternatives (`WHERE_TO_LOOK` for the heading of a report's closing list). `check_cold_read.py` checks the answers a cold reader gave to the reader's questions from the report alone: it exits 0 when every question has an answer with a quoted sentence that stands in the report, 1 when a question is left without one, 2 on unusable input; the terms the reader lists as unexplained are printed and change no exit code.

## Hook

The plugin's `../../hooks/hooks.json` registers a PreToolUse hook on `AskUserQuestion` that runs `scripts/check_question.py --hook`. A card outside the form exits 2 with its problems and the card form on stderr, so Claude Code blocks the question and shows the guidance to the model; a passing card and unreadable input exit 0. The hook calls `python3`; on Windows it also needs Git for Windows (§ Another language, another system). After the form check the same hook searches the project's ledger for earlier answers that may cover the card and returns the card to the agent once with what it found; a second hook, PostToolUse on `AskUserQuestion`, runs `scripts/records.py ledger capture --hook` and writes each answer into the ledger. Neither blocks a question because of its own failure. Two limits come from Claude Code and not from the skill: on a login without managed settings, a `managed-mcp.json` file or a Team or Enterprise account, an installed mod that handles `tool.check` can approve a call that a PreToolUse hook blocked ([Configure permissions](https://code.claude.com/docs/en/permissions), "Precedence among rules, hooks, and mods"), so such a mod can let through a card the hook returned; and a question asked in prose never reaches the hook.

## Records

`scripts/records.py` keeps two JSON Lines files. The reader record is one private file a person, `$XDG_DATA_HOME/handing-over-to-readers/reader.jsonl`: for a topic, what the reader holds and lacks, what he does with a result, the depth he wants, the basis and the date; the script refuses a file that a repository would track. The ledger is the project's, `.claude/handing-over-to-readers/ledger.jsonl`: every answer the reader gave on a card, every closure and every default decision, with its date, basis, what it applies to, what overturns it and its status. `find` scores a record sentence against sentence: for the best pair of a sentence of the query and a sentence of the record, the share of the shorter one's character trigrams found in the other; it prints the records at or above a floor of 0.40, and the agent decides what a found record means. The score is not weighted by the rarity of a word, since a project's ledger holds few records, and it is not taken over whole texts, since a card carries the card form's own sentences. `references/intake.md` and `SKILL.md` §§ 2, 4 and 7 say when each command runs.

## Another language, another system

The rules are the same in every language; three files carry the language. `lexicon.json` adds a language's words to the English ones the checks match, per key: the heading of the closing list, the words for an exit code and a self-report, the words that say why a question is asked. `page-strings.json`, or `--strings`, replaces the labels of the page. The voice is whatever the synthesiser named on the command line speaks.

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
| `references/explaining.md` | the session | collecting the reader's questions, writing the story, its pictures and the list "Where to look" |
| `references/intake.md` | the session | deciding whether the reader is known, holding the intake dialogue, keeping the reader record |
| `references/media.md` | the session | choosing the form of delivery; the rules of the page with voice |
| `references/report-template.md` | the session | writing a report to the operator |
| `references/rules.md` | the session | collecting candidates, running the filters, writing an item |
| `references/evidence.md` | the session | deciding whether a claim's support counts as evidence |
| `references/page.md` | the session | writing the body of a page with voice |
| `scripts/check_report.py` | the session | before a report or a client list is delivered |
| `scripts/check_question.py` | the session; the plugin hook with `--hook` | before and on every `AskUserQuestion` |
| `scripts/check_cold_read.py` | the session | before a report with a decision, or a page, is delivered: checks the cold reader's answers against the report |
| `../../agents/cold-reader.md` | the session, as a dispatched agent | the cold read: answers the reader's questions from the report alone |
| `scripts/records.py` | the session; the plugin hooks | looking the reader up before a long deliverable and recording an intake; searching and writing the project's ledger of answers; `ledger capture --hook` after every `AskUserQuestion` |
| `scripts/voice_cues.py` | the session | voicing a story for the page with voice: writes the audio and the time of every sentence |
| `scripts/build_page.py` | the session | building the page with voice: joins the page template, the body the agent wrote and the cues, and refuses a page that breaks the form |
| `assets/page-template.html` | `scripts/build_page.py` | on every page build |
| `assets/page-body-example.html` | the session | writing the body of a page, as a worked example |
| `maintenance/README.md` | a maintainer | before changing a rule, a check, the card form, the template or the page tooling |
| `maintenance/rules-provenance.md` | a maintainer | adding a rule or re-verifying its source |
| `maintenance/pending-evidence.md` | a maintainer | admitting a held-back rule or clause |
| `maintenance/tests/`, `maintenance/tests/fixtures/` | a maintainer | after any script or template change |
| `evals/evals.json`, `evals/fixtures/` | a maintainer | re-running the evals |
| `evals/grade.py` | a maintainer | grading a run |
| `evals/runs/iteration-2/` | a maintainer, a reviewer | checking a rule that rests on the eval |
| `evals/cold-read/` (`plants.json`, `plant.py`, `questions.json`, the four cases, `runs/`), `evals/grade_cold_read.py` | a maintainer | measuring the cold read on reports with planted omissions |

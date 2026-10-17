---
name: handing-over-to-readers
description: >-
  Shape everything that reaches a human reader — a report or hand-back, a question to the
  operator, a question list for a client, a PR description, a document — so the reader checks
  claims against evidence and takes decisions: a first page
  as a handover (risk, the reader's action, not done, wrong if), a status from exit codes, every
  claim about code with a `path:line` anchor and its fragment, questions only after the
  operator's filters and in the card form (fact, what the answer changes, one question last, a
  consequence in every option), reversible decisions taken by default into a registry; it runs the
  skill's two check scripts on the text, and the plugin's PreToolUse hook rejects an
  AskUserQuestion outside the card form. Use it
  whenever a report, summary, status update or list of questions is about to be written for the
  operator or a client ("write up the results", "summarize what you did"), and before any
  AskUserQuestion. NOT for sentence-level style, code review (software-craft) or the author's
  own PR gate (preparing-for-review).
---

# Reading contract

A reader of generated text cannot find a plausible error by reading: fluency hides it, and the
check needs a reference (the code, a test, the state of the environment). What a human reader
can do cheaply is check a claim against evidence that sits beside it and take a decision whose
consequences are written in each option. This skill therefore turns every deliverable to a human
into a handover: claims with evidence, decisions with consequences, and an account of what was
not read or not done. The rules, generalised from the operator's list to any addressee, are
`references/rules.md`.

**Agents judge, scripts check.** The filters that need judgement (is the answer already in the
files? does the answer change the work? is it reversible?) are the agent's; the form is checked
by `scripts/check_report.py` and `scripts/check_question.py`. The plugin's `hooks/hooks.json`
holds a PreToolUse hook on `AskUserQuestion` that runs `scripts/check_question.py --hook` and
rejects a question outside the card form. Run the scripts with the interpreter
(commands in § 5); they need no setup. Both scripts read the
files named on their command line (`check_question.py --hook` reads the hook payload from stdin),
print their findings to stdout and return an exit code; they write nothing, open no network
connection and use the Python standard library alone.

## 1. Resolve the addressee

- `operator`: the operator of this session. He opens files, runs commands and reads the
  transcript, so a claim about code carries a `path:line` anchor and the fragment of that line;
  identifiers of runs, workflows and agents stay out of the prose; a commit hash is allowed as
  what an approval is bound to.
- `client`: a customer, a neighbouring team, a product owner. He opens nothing of ours, so the
  text carries no file paths, section references, dates, deadlines, effort estimates or
  references to the contract; what he must know is explained in one sentence before it is used,
  in his words.

The profile changes only what the reader can open and the delivery format; the rules of
`references/rules.md` are the same for both. When the addressee is not named, a report or a
question inside a session goes to the operator, a list of questions to a client.

## 2. Collect candidates

A candidate is a place where the work runs into the addressee's decision or data: an open
question from a report, a discrepancy between documents, a missing input (rule 1). Write each
candidate first as the pair "the fact we know" and "what the answer changes", only then as a
question (rule 2). The agent's own decisions are not candidates: they are taken and recorded
(step 3, rule 6).

## 3. Run the filters

Run rules 3–9 of `references/rules.md` over the list, in order. Each is a separate test: an item
that passes "the answer is unknown" may fall on "the answer changes nothing" (rule 10). Three of
them take an action of their own:

- **The answer is already known** (3): open the file, count, run the command before asking. A
  question closed this way is recorded under § 6 as "closed, basis".
- **The answer changes nothing** (4): name, for each possible answer, what we do differently.
  Nothing differs → the item is dropped, however interesting.
- **It is reversible** (6): we have a basis, the error is cheap to undo → decide, tell the
  addressee as a fact, record it under § 6 (rule 25). Only the
  irreversible, the costly and what the addressee alone knows reaches him as a question, and the
  question says which of the three it is: the hook checks for that.

Internal matters (our own inconsistencies, our licences, fallbacks, estimates for our team) go to
a separate internal block: the operator's report carries it as its last section, the client's
file never carries it (rule 9).

## 4. Write by the template

- **A report to the operator**: `references/report-template.md`. First page in five lines (risk,
  what the reader does, not done, wrong if, status), the riskiest claim first, each claim with
  its anchor and fragment (§ 1) or with evidence that `references/evidence.md` accepts, decisions taken
  by default, questions in the card form, the internal block last, as § 3 places it. A claim takes at most three
  lines: the claim with one anchor, its evidence, its counter-argument; further anchors go to the
  internal block, because the reader checks one place per claim and the first page has to fit
  one screen (a house limit without a measurement). A question item is one paragraph with its options as a table beneath it, one option
  per row. The status line carries the checker's signal (§ What a report carries).
- **A question to the operator** (AskUserQuestion or a decision card): the question text opens
  with the fact and its decisive number, states what the answer changes and why the decision was
  not taken by default, and ends with its one question. Every option's description carries the
  consequence and the cost of being wrong; a recommendation stands as its own line with its
  basis. For an irreversible decision the answer comes as typed input, and the agent repeats the
  chosen consequence before acting (rule 18). Questions are batched at the boundary of a task
  (`references/rules.md` § What the research adds).
- **A list for a client**: rules 11–24. One claim per sentence, the decisive number first, the
  single question at the end of each item; options keyed by the client's condition ("if the
  result is needed by morning"); order by dependency; the delivered file is generated from our
  source, which keeps the internal block. The sentence that says why the item is asked ("only
  you know this", "irreversible") belongs to the operator's card, where the hook checks for it; a
  client item carries the fact, the options and its question, with our filters kept in the
  operator's card, and a default decision reaches the client as a fact (rule 14).

## 5. Check the form, then deliver

```bash
python3 -I <skill-dir>/scripts/check_report.py --profile operator --root <repo> <report.md>
python3 -I <skill-dir>/scripts/check_report.py --profile client <questions.md>
python3 -I <skill-dir>/scripts/check_question.py --questions <card.json>
```

`check_report.py` lists errors (the form) and warnings (three numbers in one sentence, a
self-report without evidence, two items on one topic) with the line; fix the errors, weigh the
warnings, deliver. An anchor whose fragment the script does not find on its line is a claim about
code that is not where the report says: fix the anchor or the claim, never the check. The scripts
match English labels and words; a lexicon file (`--lexicon`, or
`$XDG_CONFIG_HOME/handing-over-to-readers/lexicon.json`) adds those of another language, so a
report or a card written in it passes the same checks. An agent definition that returns reports
runs the operator check on its own report before returning it.

## 6. Record

Every closure and every default decision is a registry line: decision, basis, what overturns it
(rule 25). The registry lives beside the source of the list (`decisions.md` in the project, or
the store of the decision cards where one exists); the delivered file never carries it.

## What a report carries

- A checker's signal: an exit code, a count, an enumerated status (§ 5).
- The motive, the decisions and what is unverified: the bullet on what the prose carries in
  `references/rules.md` § What the research adds owns that rule.
- Load-bearing text in full, whatever the length target: an error report, a failing test, a
  security warning, the confirmation of a destructive action.

## Maintenance

`maintenance/README.md` names what changes together.

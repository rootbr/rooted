# Contributing to Rooted

Rooted is a Claude Code plugin marketplace rooted in evidence. Contributions are welcome — with one hard rule.

## The rule

Every rule, checklist item, or review criterion — whether newly added **or edited** — says what it rests on, and a claim rests on a test that could have refuted it. The method is [`references/method.md`](plugins/evidence-based-authoring/skills/scientific-method/references/method.md) of the `/scientific-method` skill; in short, a statement is one of four kinds:

- **A claim** — "this technique works better" — names its measure, what it is compared with, the conditions it is made for, and the outcome that would refute it. It carries a test: a study you opened, with its comparison, measure, sample and result in view — for a peer-reviewed study its abstract suffices, and the record says so — or a test of your own in the repository. A claim about one event — what caused one failure — names instead its rival explanations and the trace that tells them apart.
- **A norm** — a standard, a specification, official documentation, a tool's rule — is cited by issuer, version and place. It shows that a practice is accepted; whether the practice works better is a separate claim.
- **A decision** — a goal, a priority, a matter of taste — is recorded under its owner, with what it is for.
- **A definition** is recorded with its term.

A claim with no test yet is a hypothesis: it goes to its skill's list of hypotheses with its refuting outcome. A claim for which no refuting outcome can be named is an opinion and stays out.

Cite a source in the form anyone can open: an arXiv ID or DOI, an RFC number or a link to the specification, a linked commit. A source that cannot be fetched cannot be re-verified — by a reviewer, by a later reader, or by the reader that checks the record.

## A rule of your own

A rule of your own enters on a test of your own:

1. Commit the hypothesis: the measure, the comparison, the scope, the refuting outcome, the threshold and the number of runs.
2. Run the same work with the technique and without it, and keep every run.
3. Commit the result with the conditions it was obtained under and what checked the measure; a comparison of shares names its test and its p-value or interval.

`check_record.py --staged` reads the order from history and rejects a result whose hypothesis was not committed before it.

## When the rule comes from a book or a blog

A practitioner text is where a formulation comes from; the rule rests on the test of its claim. Three steps:

1. Word the claim so that it can fail.
2. Find the study that tested it, open it, and rest the rule on that test — or run the test yourself. Most durable craft rules have such a study; the practitioner text usually restates it.
3. Name the practitioner text on the rule's provenance line as the formulation the rule follows. Attribution lives on that line alone (`C-E2`), and the rule rests on the test of step 2.

Worked example: the "one thesis per card" rule was formulated by the Zettelkasten literature, whose own pages call it "a guiding compass" with "no clear litmus test". The test is Dense X Retrieval (Chen et al., EMNLP 2024, [arXiv:2312.06648](https://arxiv.org/abs/2312.06648)), which measures proposition-level indexing beating passage-level retrieval. The rule rests on that measurement, within the retrieval setting it was run in; the Zettelkasten pages are named as its formulation.

## Before you open a PR

Find the smallest change that solves the problem. Then run the three checks of `AGENTS.md` § Quality Gate. Enable the repository's hook once per clone — `git config core.hooksPath .githooks` — and two of them, the layout check and the record check, run on the content of every commit.

## What we accept

- New skills, agents, or checklists — each rule inside with its record
- Improvements to existing skills — same requirement on every line they add or change
- Corrections to references, examples, or evidence that is out of date; a test that goes against an existing rule
- Infrastructure and tooling that keeps the records checkable

## What we reject

- A claim presented as a finding with no test behind it, whoever or whatever proposed it
- Rules with "best practice" or "everyone knows" as the only ground
- A claim whose only ground is a paper that states the rule without testing it, or a source nobody opened

## Code of conduct

Be direct, be cited, be kind. A disagreement about a claim resolves by a test; a disagreement about a decision resolves by argument and the owner's word.

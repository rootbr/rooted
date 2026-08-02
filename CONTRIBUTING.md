# Contributing to Rooted

Rooted is a Claude Code plugin marketplace rooted in evidence. Contributions are welcome — with one hard rule.

## The rule

Every rule, checklist item, or review criterion — whether newly added **or edited** — MUST cite exactly one of:

- **An arXiv ID or DOI** for academic research
- **An RFC number or a link to an official specification** for technical standards
- **A linked hands-on test** — a gist, PR, or commit demonstrating the behavior in practice

Each of the three is named in the form anyone can open. A source that cannot be fetched cannot be re-verified — by a reviewer, by a later reader, or by the audit that runs over these files.

## When the rule comes from a book or a blog

A trade book is not one of the three classes, and neither is a practitioner blog post. That does not mean the idea is wrong — it means the citation is pointing at the wording rather than at the evidence. Three steps:

1. Find the research that backs the claim itself, and rest the rule on that. Most durable craft rules have one; the practitioner text usually restates it.
2. Name the practitioner text in `rule-cards-provenance.md` as the formulation the rule follows — never inside the card, where `C-E2` forbids attribution, and never as the rule's evidence.
3. Where an openable source carries the same formulation, drop the unopenable one rather than keeping both.

Worked example: the "one thesis per card" rule was formulated by the Zettelkasten literature, whose own pages call it "a guiding compass" with "no clear litmus test". The evidence is Dense X Retrieval (Chen et al., EMNLP 2024, [arXiv:2312.06648](https://arxiv.org/abs/2312.06648)), which measures proposition-level indexing beating passage-level retrieval. The rule rests on the paper; the Zettelkasten pages are named as its formulation; the book restating them was dropped.

If no research backs the claim, the third class is still open: demonstrate it with a linked test and cite that.

## Before you open a PR

Find the smallest change that solves the problem.

## What we accept

- New skills, agents, or checklists — each rule inside cited per the rule above
- Improvements to existing skills — same citation requirement
- Corrections to references, examples, or evidence that is out of date
- Infrastructure and tooling that keeps the citation chain enforceable

## What we reject

- LLM-generated rules, even if they look reasonable
- Rules with "best practice" or "everyone knows" as the only justification
- Anything that cannot be traced back to a paper, an RFC, or a real test

## Code of conduct

Be direct, be cited, be kind. Disagreements resolve by exchanging evidence, not opinions.

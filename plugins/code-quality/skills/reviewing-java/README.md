# reviewing-java

Java code review skill for Claude Code; paths in this file are relative to this directory. A deterministic pre-pass matches a corpus of atomic rule cards against your diff, one workflow runs a finder per triggered card and a skeptic per finding, and two reports land under `review/`: the verified findings and the rejection audit trail.

## What it does

Six phases — **Scope** → **Context** → **Pre-pass** → **Workflow** → **Follow-ups** → **Report** — with one confirmation, the scope summary.

| Stage | What runs | Where it lives |
|--|--|--|
| Pre-pass | `static-review.py` reads `git diff -U0`, the card frontmatter and your `config.md`, and writes `review/plan.json`: which cards the diff triggers, which files each one reads, the logic-pass slices, mechanical candidates, your project invariants as cards | `scripts/static-review.py` |
| Bundle | `bundle-run.py` embeds the plan, the design intent and the project context into `review/run.js`, the workflow script the orchestrator runs by path, so a plan of any size never passes through a typed tool call | `scripts/bundle-run.py` |
| Find | one finder per (card by slice) at the card's tier, one logic pass per slice, one finder per project invariant per slice | `scripts/review-workflow.js`, `plugins/code-quality/agents/review-finder.md` |
| Aggregate | deterministic: duplicates dropped, spans grouped, compatible fixes folded, conflicts resolved by domain priority | `scripts/review-workflow.js` |
| Verify | one skeptic per finding tries to refute it with something it opened and calibrates severity; a rejected Critical or Major gets a second skeptic and an arbiter | `scripts/review-workflow.js`, `plugins/code-quality/agents/review-verifier.md` |
| Report | `render-reports.py` writes the review report and the rejection report | `scripts/render-reports.py` |

## The card corpus

`references/review-cards/` holds one file per rule — `cc-08--check-then-act-on-a-concurrent-map-is-one-compute-call.md` and its siblings — across six domains:

| Prefix | Domain | Runs when |
|--|--|--|
| `CC-` | concurrency: races, visibility, atomicity, locks, executors, virtual threads | the diff's added lines match the card's triggers |
| `SEC-` | security: injection, XSS, CSRF, SSRF, auth, crypto, secrets, deserialization | same |
| `PF-` | performance: allocation, collections, JIT shape, cache layout, I/O, hot paths | same |
| `REL-` | reliability: leaks, data integrity, transactions, resilience, REST, compatibility, shutdown | same |
| `MNT-` | maintainability: function shape, naming, complexity, SOLID, API design, testability, logging, DI | same |
| `META-` | the quality of your own `config.md` invariants | `config.md` changed in the diff, or `--meta` |

Each card is one checkable claim with a Thesis, a Rationale, a Java `bad:`/`good:` pair, its Limits (when the pattern is correct), a Validator ending in one binary question, and what the finder emits; it carries no citation. Its sources — a JDK 21 Javadoc entry, a JLS section, a JEP, a Spring or Hibernate reference section, an OWASP cheat sheet, a CWE, a SEI CERT rule, an RFC, a paper, or a jcstress sample — live on its line in `maintenance/review-cards-provenance.md`, with the fetch status, every quoted statement, the origin section in the checklist the card came from and any formulation it follows; a finding's one-line source pointer in the review report comes from that line. A rule with no openable source waits in `maintenance/pending-evidence.md` and ships nowhere. The corpus schema is `maintenance/review-cards-taxonomy.md`; `maintenance/scripts/validate-review-cards.py` checks every card against it.

## Quickstart

```
cd <your-java-repo>
/reviewing-java
```

Works out of the box if your repo is a git working tree with Java sources and a standard base branch (`main`, `master`, or `develop`). The workflow needs the Workflow tool (Claude Code with dynamic workflows enabled); without it the skill falls back to one sub-agent per domain and says so in the report.

## Output

Two documents, under `review/` or at the path your config's `review_output` names:

1. **Review report** (`java-review-<branch>.md`) — only findings that survived verification. Executive summary, critical and major findings with the rule id, a one-line source pointer and suggested fix code, a table of minor findings and suggestions, and a section for findings an arbiter could not settle.
2. **Rejection report** (`java-review-<branch>-rejections.md`) — everything a skeptic rejected or downgraded, with the evidence it opened. It lets the author see what the skeptics filtered and push back.

`review/plan.json`, `review/plan.log`, `review/run.js`, `review/findings.json` and `review/verdicts.json` stay as the run's record; a review can resume from `findings.json` in a new session.

## Project integration

Add a config file to your repo:

```
<your-repo>/
└── .claude/
    └── reviewing-java/
        ├── config.md          # frontmatter + invariants
        └── cards/             # optional: full rule cards of your own, in the corpus schema
```

### config.md

YAML frontmatter configures the skill; the Markdown body becomes `project_context`, which every finder and skeptic receives.

```markdown
---
project_name: MyProject
base_branch: main
branch_pattern: '^feature/PROJ-\d+'
ticket_id_pattern: 'PROJ-\d+'
ticket_design_doc: 'docs/{TICKET_ID}.md'
review_output: 'docs/{TICKET_ID}-review.md'
documentation: 'docs/architecture'
modules: [{"name": "core", "packages": ["com.acme.core"]}, {"name": "web", "packages": ["com.acme.web"]}]
---

# MyProject review context

## Tolerances
- The `Stats#sample` counter is an approximate statistics counter; lost increments are accepted.

## Invariants
1. **Sentinel at index 0**: Index 0 is reserved and never holds data; every iteration uses `> 0`. Violation: reads garbage.
16. **Size tracking**: onAdd and onRemove are called symmetrically. Violation: the size counter drifts.
```

- **Tolerances** reject findings: a skeptic that finds "lost increments are accepted" on the flagged counter rejects the race finding with that sentence as evidence. Write them in the vocabulary of the cards' Limits — "approximate counter", "confined to one thread", "debug-only path", "duplicate load accepted".
- **Invariants** become project cards `PROJ-N`: the bold title, the rule, and the sentence after `Violation:` as the forbidden state; a number in the item (`~50 M invocations/day`) becomes the scale the finder multiplies by. Number them, make them checkable against code, and state the consequence.
- **`modules`** names the module boundaries the pre-pass slices by; without it, slicing follows package prefixes.
- **`cards/`** holds full cards in the corpus schema (`maintenance/review-cards-taxonomy.md`); they run like shipped cards.

See [Java Invariants Review Checklist](maintenance/java-invariants-review-checklist.md) for discovering, documenting and verifying invariants, `references/gotchas.md` when a review misfires, and `maintenance/README.md` before changing a card, a script, a prompt or a tier.

## Layout

This skill's instance of the repository `README.md` §Skill layout:

| Path | Who reads or runs it | When |
|--|--|--|
| `SKILL.md` | the orchestrating session | on `/reviewing-java`, whole |
| `references/review-cards/` | the pre-pass (frontmatter), each finder (its one card) | every review |
| `references/gotchas.md` | the orchestrating session | when a review misfires |
| `references/report-format.md` | the orchestrating session | writing or checking the two reports |
| `scripts/static-review.py` | the orchestrating session | the pre-pass of every review |
| `scripts/bundle-run.py` | the orchestrating session | before the workflow call |
| `scripts/review-workflow.js` | the Workflow tool, as `review/run.js` | every review |
| `scripts/render-reports.py` | the orchestrating session | after the verify stage |
| `scripts/cardlib.py` | imported by the scripts above and by the validator | with them |
| `maintenance/README.md` | a maintainer | before changing a card, a script, a prompt or a tier |
| `maintenance/review-cards-provenance.md` | a maintainer; `scripts/render-reports.py` through `cardlib.provenance_map_path` | authoring a card; a finding's source pointer in the report |
| `maintenance/review-cards-taxonomy.md` | a maintainer, the validator | authoring a card or a facet value |
| `maintenance/pending-evidence.md` | a maintainer | authoring |
| `maintenance/java-invariants-review-checklist.md` | a maintainer, a project writing its invariants | writing `config.md` invariants |
| `maintenance/scripts/validate-review-cards.py` | a maintainer | before committing a card |
| `maintenance/tests/` | a maintainer | after any script change |
| `evals/` | a maintainer | a model or tier change, the fixture grading |

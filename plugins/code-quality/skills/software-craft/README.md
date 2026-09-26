# software-craft

Build-and-review skill for Claude Code; paths in this file are relative to this directory. A developer agent writes code by a corpus of atomic craft cards — the general, language-agnostic craft of programming, one checkable rule each, an openable source each — and a card-dispatched review checks its own diff against the same cards: a deterministic pre-pass matches the cards' dispatch conditions against the diff, one workflow runs a finder per triggered card and a skeptic per finding, one fix round returns the confirmed findings to the developer, and two reports land under `craft/`. The review also runs alone on any diff in any mainstream language.

## What it does

Seven phases — **Scope** → **Context** → **Build** → **Pre-pass** → **Workflow** → **Fix round** → **Follow-ups and report** — with one confirmation, the scope summary. A review-only run skips Build and the Fix round.

| Stage | What runs | Where it lives |
|--|--|--|
| Build | one developer agent, inside the write zone the task names: detects the stack, plans, lists the cards for each step of its work and reads the ones whose titles apply, implements, tests, self-reviews with the pre-pass, reports | `plugins/code-quality/agents/software-developer.md`, `scripts/craft-cards.py` |
| Pre-pass | `static-craft.py` reads the diff (a commit range, or the working tree with its untracked files), measures eleven structural signals per hunk, matches the card frontmatter and your `config.md`, and writes `craft/plan.json`: which cards the diff triggers, which files each one reads, the logic-pass slices, mechanical candidates, your project invariants as cards | `scripts/static-craft.py` |
| Bundle | `bundle-run.py` embeds the plan, the design intent and the project context into `craft/run.js`, the workflow script the orchestrator runs by path, so a plan of any size never passes through a typed tool call | `scripts/bundle-run.py` |
| Find | one finder per (card by slice) at the card's tier, one logic pass per slice, one finder per project invariant per slice | `scripts/craft-review-workflow.js`, `plugins/code-quality/agents/craft-finder.md` |
| Aggregate | deterministic: duplicates dropped, spans grouped, compatible fixes folded, conflicts resolved by domain priority | `scripts/craft-review-workflow.js` |
| Verify | one skeptic per finding tries to refute it with something it opened and calibrates severity; a rejected Major gets a second skeptic and an arbiter | `scripts/craft-review-workflow.js`, `plugins/code-quality/agents/craft-verifier.md` |
| Fix round | confirmed findings go back to the developer once; the pre-pass and the verify stage run again on the fix diff | `SKILL.md` §Phase 6 |
| Report | `render-reports.py` writes the review report and the rejection report | `scripts/render-reports.py` |

## Two consumers of one card

Every card serves two readers. The developer retrieves cards before a step of its work — designing, implementing, handling errors, testing, refactoring, documenting — through `scripts/craft-cards.py --step <step>`, scans the titles and opens the cards whose titles apply; the `step` and `applies_to` facets are its index. The review finder receives one card whole, with the diff hunks the card's `triggers` selected (regular expressions against added lines in any language, or `signal:<name>` for a structural signal the pre-pass measures: a long routine, a deep nest, a long parameter list, a boolean argument, an empty handler, a magic number, commented-out code, a marker comment, a duplicated block), reads at the card's `scope`, and applies its Validator's one binary question. The Example on a card shows the rule in one of five languages — Java, Python, TypeScript, Go, Rust — and the rule holds in all of them.

## The card corpus

`references/craft-cards/` holds one file per rule — `<prefix>-NN--<slug>.md` — across ten domains:

| Prefix | Domain | Topics |
|--|--|--|
| `CODE-` | code inside a function | naming, comments, layout, routine shape, variables and numerics, control flow, table-driven construction, generics |
| `DSN-` | module design | complexity and depth, information hiding, coupling, duplication, inheritance and composition, patterns, mutable state, functional style, domain modeling |
| `API-` | interfaces | API design and use, contracts and assertions, evolution and deprecation |
| `ERR-` | errors and resilience | error and exception handling, defensive programming, fault tolerance, resource management, logging |
| `TST-` | tests | unit testing and test quality, test-first, test doubles, larger tests, property-based testing |
| `CHG-` | changing code | refactoring, smells, seams and characterization tests, large-scale change, small steps, technical debt |
| `PRF-` | diagnostics and performance | debugging, profiling and tuning, algorithm and data-structure choice |
| `TOOL-` | tools and hygiene | build, warnings, static analysis, CI, dependencies, configuration, internationalization and encoding |
| `DOC-` | reading and documenting | reading code, code review as author and reviewer, documentation beyond comments |
| `INP-` | input and security hygiene | parsing and grammar-based input, security hygiene in ordinary code |

Each card is one checkable claim with a Thesis, a Rationale, a `bad:`/`good:` pair in one language, its Limits (when the pattern is correct — for a contested rule, the sourced condition that separates the cases), a Validator ending in one binary question, what the finder emits, and a compact locator of an openable source: a paper by arXiv id or DOI, a standard or official documentation page by section, a static-analysis rule page, or a fixture test. The full citation with its fetch status, the topic's research note, the formulation the rule follows and the reception it met live in `references/craft-cards-provenance.md`; a rule with no openable evidence, or a contested rule with no separating condition, waits in `references/pending-evidence.md` and ships nowhere. The corpus schema is `references/craft-cards-taxonomy.md`; `scripts/validate-craft-cards.py` checks every card against it. Each topic was researched through `scripts/research-topic-workflow.js`, whose notes sit under `research/software-craft/` at the repository root; the design is `research/2026-09-26_software-craft-cards.md`.

## Quickstart

```
cd <your-repo>
/software-craft implement rate limiting for the public API in src/api/limits.py, with tests
/software-craft                       # review the current branch against its base
/software-craft --worktree            # review uncommitted changes
```

Works out of the box in any git working tree with a standard base branch (`main`, `master`, or `develop`). The workflow needs the Workflow tool (Claude Code with dynamic workflows enabled); without it the skill falls back to one sub-agent per domain and says so in the report. The developer agent, the finder and the skeptic resolve as `code-quality:software-developer`, `code-quality:craft-finder` and `code-quality:craft-verifier` where the plugin is installed; a repository checkout runs the same prompts on the default agents.

## Output

Two documents, under `craft/` or at the path your config's `review_output` names:

1. **Review report** (`craft-review-<task>.md`) — only findings that survived verification. Executive summary, the developer's report of what was built, major findings with the rule id, a one-line source pointer and suggested fix code in the file's language, a table of minor findings and suggestions, and a section for findings an arbiter could not settle.
2. **Rejection report** (`craft-review-<task>-rejections.md`) — everything a skeptic rejected or downgraded, with the evidence it opened. It lets the author see what the skeptics filtered and push back.

`craft/plan.json`, `craft/plan.log`, `craft/run.js`, `craft/findings.json`, `craft/verdicts.json` and `craft/build-report.md` stay as the run's record; a review can resume from `findings.json` in a new session. Nothing is committed: the skill and the developer agent make no version-control write, and the operator commits what the report names.

## Project integration

Add a config file to your repo:

```
<your-repo>/
└── .claude/
    └── software-craft/
        ├── config.md          # frontmatter + invariants
        └── cards/             # optional: full rule cards of your own, in the corpus schema
```

### config.md

YAML frontmatter configures the skill; the Markdown body becomes `project_context`, which the developer, every finder and every skeptic receive.

```markdown
---
project_name: MyProject
base_branch: main
branch_pattern: '^feature/PROJ-\d+'
ticket_id_pattern: 'PROJ-\d+'
ticket_design_doc: 'docs/{TICKET_ID}.md'
review_output: 'docs/{TICKET_ID}-craft-review.md'
documentation: 'docs/architecture'
modules: [{"name": "core", "paths": ["src/core"]}, {"name": "web", "paths": ["src/web"]}]
---

# MyProject craft context

## Tolerances
- Numeric literals in `src/core/units.py` are physical constants and stay inline.

## Invariants
1. **Handlers return a result**: Every request handler returns a `Result`; no handler raises across the boundary. Violation: an exception escaping a handler.
2. **Repositories take their store in the constructor**: A repository receives its store through its constructor. Violation: a repository that opens its own connection.
```

- **Tolerances** reject findings: a skeptic that finds "physical constants stay inline" on the flagged literal rejects the magic-number finding with that sentence as evidence. Write them in the vocabulary of the cards' Limits.
- **Invariants** become project cards `PROJ-N`: the bold title, the rule, and the sentence after `Violation:` as the forbidden state; a number in the item becomes the scale the finder multiplies by. Number them, make them checkable against code, and state the consequence.
- **`modules`** names the module boundaries the pre-pass slices by; without it, slicing follows directory prefixes, with test files sliced apart.
- **`cards/`** holds full cards in the corpus schema (`references/craft-cards-taxonomy.md`); they run like shipped cards.

See `references/gotchas.md` when a run misfires and `references/maintenance.md` before changing a card, a script, a signal or a tier.

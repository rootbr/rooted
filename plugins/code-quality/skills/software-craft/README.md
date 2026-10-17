# software-craft

Build-and-review skill for Claude Code; paths in this file are relative to this directory. A developer agent designs a change into a brief and, once the brief is confirmed, implements it by a corpus of atomic craft cards — the general, language-agnostic craft of programming, one checkable rule each, an openable source each — and a card-dispatched review checks the developer's diff against the same cards: a deterministic pre-pass matches the cards' dispatch conditions against the diff, one workflow runs a finder per triggered card and a skeptic per finding, one fix round returns the confirmed findings to the developer, and two reports land under `craft/`. The review also runs alone on any diff in any mainstream language.

## What it does

Nine phases — **Scope** → **Context** → **Design** → **Build** → **Pre-pass** → **Workflow** → **Follow-ups** → **Fix round** → **Report** — with one confirmation: on a build run the scope summary with the design brief at the end of Design, on a review-only run the scope summary at the end of Scope. A review-only run skips Design, Build and the Fix round.

A build run names its build model — `fable` for a task that adds or changes a boundary, a data flow across modules, a failure contract, concurrency or a project invariant, `opus` otherwise, or the one the task names. The design dispatch runs on it at `xhigh`; the build at `high` on `fable` and `xhigh` on `opus`, and at `opus` `high` when every step of the brief is mechanical; a dispatch on `fable` that errors repeats once on `opus`. The review runs on `opus` at every tier, so a change built on Fable is judged by another model.

| Stage | What runs | Where it lives |
|--|--|--|
| Design | one developer agent on its design dispatch: reads the write zone and its neighbours, lists the `design` cards, designs each significant decision twice and writes the design brief `craft/design.md` — task, stack, design with its decisions, failure paths, tests, steps, out of scope — checked by `brief-gate.py` and shown with the scope summary for the one confirmation | `plugins/code-quality/agents/software-developer.md`, `SKILL.md` §Phase 3, `scripts/craft-cards.py`, `scripts/brief-gate.py` |
| Build | the same agent type on its build dispatch, inside the write zone the task names: reads the brief and follows its steps, lists the cards for each step and reads the ones whose titles apply, implements, tests, self-reviews with the pre-pass, reports with its deviations from the brief | `plugins/code-quality/agents/software-developer.md`, `scripts/craft-cards.py` |
| Pre-pass | `static-craft.py` reads the diff (a commit range, or the working tree with its untracked files), measures eleven structural signals per hunk, matches the card frontmatter and your `config.md`, and writes `craft/plan.json`: which cards the diff triggers, which files each one reads, the logic-pass slices, mechanical candidates, your project invariants as cards, and whether the `META-` cards audit your `config.md` | `scripts/static-craft.py` |
| Bundle | `bundle-run.py` embeds the plan, the design intent and the project context into `craft/run.js`, the workflow script the orchestrator runs by path, so a plan of any size never passes through a typed tool call; a large plan is bundled in parts, one workflow each, and `merge-parts.py` joins their outputs | `scripts/bundle-run.py`, `scripts/merge-parts.py` |
| Find | one finder per (card by slice) at the card's tier, one logic pass per slice, one finder per project invariant per slice | `scripts/craft-review-workflow.js`, `plugins/code-quality/agents/craft-finder.md` |
| Aggregate | deterministic: duplicates dropped, spans grouped, compatible fixes folded, conflicts resolved by domain priority | `scripts/craft-review-workflow.js` |
| Verify | one skeptic per finding tries to refute it with something it opened and calibrates severity; a rejected Critical or Major gets a second skeptic and an arbiter | `scripts/craft-review-workflow.js`, `plugins/code-quality/agents/craft-verifier.md` |
| Fix round | confirmed findings go back to the developer once, with the same brief; the pre-pass and the verify stage run again on the fix diff | `SKILL.md` §Phase 8 |
| Report | `render-reports.py` writes the review report and the rejection report | `scripts/render-reports.py` |

## Two consumers of one card

Every card serves two readers. The developer retrieves cards before a step of its work — designing on the design dispatch, then implementing, handling errors, testing, refactoring and documenting on the build — through `scripts/craft-cards.py --step <step>`, scans the titles and opens the cards whose titles apply; the `step` and `applies_to` facets are its index. The review finder receives one card whole, with the diff hunks the card's `triggers` selected (regular expressions against added lines in any language, or `signal:<name>` for a structural signal the pre-pass measures: a long routine, a deep nest, a long parameter list, a boolean argument, an empty handler, a magic number, commented-out code, a marker comment, a duplicated block), reads at the card's `scope`, and applies its Validator's one binary question. The Example on a card shows the rule in one of five languages — Java, Python, TypeScript, Go, Rust — and the rule holds in all of them.

## The card corpus

`references/craft-cards/` holds one file per rule — `<prefix>-NN--<slug>.md` — 529 cards across twelve domains, with 173 further rules waiting in `maintenance/pending-evidence.md` for an openable source. Two language corpora sit beside it, each with its own two maps; both consumers take a language corpus as a further `--cards-dir`, and the pre-pass dispatches its cards only onto that language's files:

- `references/craft-cards-python/` — 178 cards `PY-NN` across twelve topics, the rules that hold because of Python itself, with `maintenance/craft-cards-python-provenance.md` and `maintenance/pending-evidence-python.md` (5 rules waiting), researched through `maintenance/scripts/python-topic-workflow.js` into the notes under `research/software-craft-python/` and recorded in `research/2026-10-15_software-craft-python-cards.md`.
- `references/craft-cards-java/` — 231 cards `JAVA-01`..`JAVA-231`, the rules that hold because of Java and its ecosystem, across nine domains: concurrency and security, which no universal prefix owns, and performance, errors, code, design, interface, tooling and tests. A card bound to a framework or library — Spring, Spring Security, JPA and Hibernate, Jackson, Resilience4j and others — triggers on that framework's API, so only code that uses the framework dispatches it. Its maps are `maintenance/craft-cards-java-provenance.md`, whose line names the origin section of the Java review checklist a card was carded from, and `maintenance/pending-evidence-java.md` (36 rules waiting); its design is recorded in `research/2026-10-16_software-craft-java-corpus.md`.

The universal prefixes:

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
| `ARCH-` | architecture | component cohesion and change coupling, stable dependencies between components, boundary enforcement and package structure, boundaries and adapters, composition root and wiring, services as components, architecture decisions and their record |
| `META-` | the audit of `config.md` | the quality of your own `config.md` invariants; runs onto that file alone, when the diff changed it or under `--meta` |

Each card is one checkable claim with a Thesis, a Rationale, a `bad:`/`good:` pair in one language, its Limits (when the pattern is correct — for a contested rule, the sourced condition that separates the cases), a Validator ending in one binary question, and what the finder emits; it carries no citation. Its sources — a paper by arXiv id or DOI, a standard or official documentation page by section, a static-analysis rule page, or a fixture test — live on its line in `maintenance/craft-cards-provenance.md` (a language card's in its corpus's map), with the fetch status, every quoted statement, the topic's research note, the formulation the rule follows and the reception it met; `python3 scripts/craft-cards.py --provenance <RULE_ID>` prints that line (with `--cards-dir references/craft-cards-python` for a `PY-` id, `--cards-dir references/craft-cards-java` for a `JAVA-` id), and a finding's one-line source pointer in the review report comes from it. A rule with no openable evidence, or a contested rule with no separating condition, waits in `maintenance/pending-evidence.md` (a language rule in its corpus's) and ships nowhere. The corpus schema is `maintenance/craft-cards-taxonomy.md`; `maintenance/scripts/validate-craft-cards.py` checks every card against it. Each topic was researched through `maintenance/scripts/research-topic-workflow.js`, whose notes sit under `research/software-craft/` at the repository root; the design is `research/2026-09-26_software-craft-cards.md`.

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

1. **Review report** (`craft-review-<task>.md`) — only findings that survived verification. Executive summary with a recommendation — Block for a critical finding, Fix before merge for a major one, Merge with fixes for a minor one, Merge otherwise — the developer's report of what was built, critical and major findings with the rule id, a one-line source pointer and suggested fix code in the file's language, a table of minor findings and suggestions, and a section for findings an arbiter could not settle.
2. **Rejection report** (`craft-review-<task>-rejections.md`) — everything a skeptic rejected or downgraded, with the evidence it opened. It lets the author see what the skeptics filtered and push back.

`craft/design.md`, `craft/plan.json`, `craft/plan.log`, `craft/run.js`, `craft/findings.json`, `craft/verdicts.json` and `craft/build-report.md` stay as the run's record; a review can resume from `findings.json` in a new session. Nothing is committed: the skill and the developer agent make no version-control write, and the operator commits what the report names.

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
- **`cards/`** holds full cards in the corpus schema (`maintenance/craft-cards-taxonomy.md`); they run like shipped cards.
- **The `META-` cards** audit `config.md` itself — every rule on code a numbered invariant that names its forbidden state and the handle that enforces it, a scale number where load decides the rule, terms defined once, numbers kept across revisions, no two invariants in conflict — when the diff changes the file, or on an unchanged file under `--meta`.

See `maintenance/java-invariants-review-checklist.md` for discovering, documenting and verifying the invariants of a Java codebase, `references/gotchas.md` when a run misfires and `maintenance/README.md` before changing a card, a script, a signal or a tier.

## Layout

This skill's instance of the repository `README.md` §Skill layout:

| Path | Who reads or runs it | When |
|--|--|--|
| `SKILL.md` | the orchestrating session | on `/software-craft`, whole |
| `references/craft-cards/`, `references/craft-cards-python/`, `references/craft-cards-java/` | the pre-pass (frontmatter), the developer agent (the cards whose titles apply), each finder (its one card) | every build and review |
| `references/gotchas.md` | the orchestrating session | when a run misfires |
| `references/report-format.md` | the orchestrating session | writing or checking the two reports |
| `scripts/static-craft.py` | the orchestrating session, the developer agent | the pre-pass of a review, the developer's self-review |
| `scripts/craft-cards.py` | the developer agent; a reader with `--provenance` | before each design and build step |
| `scripts/brief-gate.py` | the developer agent, then the orchestrating session | after the brief is written, before the confirmation; after a fix round amends the brief |
| `scripts/bundle-run.py` | the orchestrating session | before each workflow call |
| `scripts/craft-review-workflow.js` | the Workflow tool, as `craft/run.js` | every review |
| `scripts/merge-parts.py` | the orchestrating session | a review run in parts |
| `scripts/render-reports.py` | the orchestrating session | after the verify stage |
| `scripts/cardlib.py` | imported by the scripts above and by the authoring scripts | with them |
| `maintenance/README.md` | a maintainer | before changing a card, a script, a prompt, a signal or a tier |
| `maintenance/craft-cards-provenance.md`, `maintenance/craft-cards-python-provenance.md`, `maintenance/craft-cards-java-provenance.md` | a maintainer; `scripts/render-reports.py` and `scripts/craft-cards.py --provenance` through `cardlib.provenance_map_path` | authoring a card; a finding's source pointer in the report |
| `maintenance/craft-cards-taxonomy.md` | a maintainer, the validator, the research agents | authoring a card or a facet value |
| `maintenance/brief-provenance.md` | a maintainer | changing a rule of the design brief — the decisions, the operations of a module entry, the gate |
| `maintenance/pending-evidence.md`, `maintenance/pending-evidence-python.md`, `maintenance/pending-evidence-java.md` | a maintainer, `maintenance/scripts/write-topic-result.py` | authoring |
| `maintenance/java-invariants-review-checklist.md` | a project's author, a maintainer | discovering and writing the invariants of a Java project's `config.md` |
| `maintenance/scripts/` | a maintainer | researching a topic, harvesting the Python catalogs, validating the cards (`maintenance/README.md` §Scripts) |
| `maintenance/tests/` | a maintainer | after any script change |
| `evals/`: the fixtures `evals/fixture/` and `evals/fixture-java/`, graded against `evals/expected.json` and `evals/expected-java.json` | a maintainer | a model or tier change, the fixture grading, the smoke task |

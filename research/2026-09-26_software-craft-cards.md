# Design note — `software-craft` on atomic rule cards

The `/software-craft` skill builds code and reviews it against one corpus of atomic craft cards — the general, language-agnostic craft of programming, one checkable rule per card, an openable source per card. A developer agent writes code by the cards, listing the cards for each step of its work and reading the ones whose titles apply; a deterministic pre-pass then matches the cards' dispatch conditions against the agent's own diff, a Workflow script runs one finder per (card × slice) plus a logic pass per slice, aggregates deterministically and runs one skeptic per finding; one fix round returns the confirmed findings to the developer; a render script writes two Markdown reports. A rule with no openable source is held in `pending-evidence.md` and ships nowhere.

This note is the design record: the layout, the two consumers, the card schema and its controlled vocabulary, the topic taxonomy, the structural signals, the contested-rule treatment, the ownership and priority tables, the `plan.json` contract, the workflow contracts, the research workflow, the source policy, the fixture and grading design, the progress and cost of the build, and the deviations from the brief that commissioned it. Each fact names its runtime owner; where this note and a runtime file differ, the runtime file decides. Paths are relative to `plugins/code-quality/skills/software-craft/` unless they start with `plugins/` or `research/`.

## Layout

```
plugins/code-quality/
|-- agents/
|   |-- software-developer.md      # code-quality:software-developer
|   |-- craft-finder.md            # code-quality:craft-finder
|   `-- craft-verifier.md          # code-quality:craft-verifier
`-- skills/software-craft/
    |-- SKILL.md                   # orchestration; under 500 lines; disallowed-tools: Edit, NotebookEdit
    |-- README.md
    |-- references/
    |   |-- craft-cards/           # <prefix>-NN--<slug>.md, one rule each
    |   |-- craft-cards-taxonomy.md    # corpus schema, controlled vocabulary, deltas from the base card spec
    |   |-- craft-cards-provenance.md  # rule_id, evidence citation, formulation source, reception, notes
    |   |-- pending-evidence.md    # rules held back: no openable evidence, or no separating condition
    |   |-- maintenance.md         # what changes together when a card, script, prompt or tier changes
    |   |-- gotchas.md             # G-NN, symptom-indexed
    |   `-- report-format.md       # the exact layout of the reports render-reports.py writes
    |-- scripts/
    |   |-- static-craft.py        # pre-pass: diff + cards -> craft/plan.json, craft/plan.log; stdlib only
    |   |-- cardlib.py             # shared frontmatter and trigger parsing
    |   |-- craft-cards.py         # lists cards by facet for the developer agent: rule_id, title, path
    |   |-- validate-craft-cards.py    # mechanical corpus validator
    |   |-- bundle-run.py          # plan + intent + context -> craft/run.js
    |   |-- craft-review-workflow.js   # Find -> Aggregate -> Verify -> Refute
    |   |-- research-topic-workflow.js # one topic -> research note, card drafts, provenance lines, pending entries
    |   |-- render-reports.py
    |   `-- tests/
    `-- evals/
        |-- evals.json
        |-- expected.json
        |-- grade.py
        `-- fixture/               # base/ and head/ trees in several languages; make-fixture.sh
research/
|-- 2026-09-26_software-craft-cards.md   # this note
`-- software-craft/<topic-slug>.md       # one research note per topic, retained
```

The plugin-level `agents/` directory holds the three agent types because a Claude Code plugin resolves agent types only from that directory, under `<plugin>:<name>`. The progress table under §Progress says which of these files exist; a path listed here and marked open there is a deliverable of a later step.

## Two consumers of one card

1. The developer while writing. Before a step — designing a module, implementing, adding tests, handling errors, refactoring, documenting — the developer agent lists the cards for that step by facet through `scripts/craft-cards.py`, reads the titles, opens the cards whose titles apply, and writes to them. This is the base card specification's retrieval model: a facet filter followed by an index scan of titles.
2. The finder during self-review. After the step, the pre-pass matches each card's dispatch conditions — regular expressions against the added lines, or a structural signal the pre-pass computes — and the review workflow dispatches one finder per (card × slice) and one skeptic per finding. The finder reads the card whole, in isolation, with the hunks.

The schema serves both: `step` and `applies_to` are the first consumer's retrieval facets; `triggers`, `scope` and `check_kind` are the second consumer's dispatch facets; both consumers apply the Validator. Every shipped card has a Validator with one binary question. A principle with no checkable form on a diff becomes the Rationale of a checkable card, or is recorded in its topic's research note under "held back" and yields no card.

## Card schema

A craft card is a specialization of the base KB card specification (`plugins/evidence-based-authoring/skills/auditing-ai-context/references/kb-card-specification.md`), the third corpus after the audit's rule cards and the Java review cards. `references/craft-cards-taxonomy.md` owns the schema, the allowed values and the deltas from the base specification; this section carries the design reasons.

Frontmatter, exactly these keys in this order:

| Field | Values | Role |
|--|--|--|
| `title` | the rule as one complete, checkable declarative claim | the index line and the H1 |
| `rule_id` | `<PREFIX>-NN`, one prefix per topic group (§Topic taxonomy) | stable id; a finding is `<rule_id>.<ordinal>` |
| `domain` | the topic group's domain name, one value | ownership and conflict priority |
| `step` | one or more of `design`, `implement`, `handle-errors`, `test`, `refactor`, `document`, `review` | the developer's retrieval facet |
| `applies_to` | `universal`, or one or more named scopes: a paradigm, a boundary kind, a language trait, a file kind | self-restriction |
| `triggers` | Python `re` patterns matched against added lines in any language, or `signal:<name>` for a structural signal; `[]` means every diff | the dispatch facet |
| `scope` | `hunk`, `file`, `base-compare`, `callers` | what the finder reads beyond the hunk |
| `check_kind` | `mechanical`, `semantic` | the finder's tier and burden |
| `severity_default` | `major`, `minor`, `suggestion` | starting severity; the verifier calibrates |

Body blocks in this order: `## Thesis` → `## Rationale` → `## Example` → `## Limits` → `## Validator` → `## Finding output` → `## Source`.

Design reasons behind the deltas from the base specification and from the Java review corpus:

- Two retrieval facets return. The developer consumer retrieves by facet and title, so `step` (the moment in the work) and `applies_to` (the scope where the rule holds) are consumer fields again; the Java corpus dropped them because its only consumer was a dispatched finder.
- `triggers` admit a structural signal. A craft defect often has no lexical signature — a long routine, a deep nest, a parameter list of seven, a boolean argument — so the pre-pass computes a fixed list of language-neutral signals per hunk (§Structural signals) and a card names one with `signal:<name>`. A card takes `[]` and runs on every diff when neither a pattern nor a signal can express its condition; that class is kept to a handful because each always-on card is one finder per slice on every review.
- The `## Example` is a `bad:` / `good:` pair of at most ten lines in one of the five first-class languages — Java, Python, TypeScript, Go, Rust — with the fence tagged with that language and generic names. The rule is language-agnostic; the example is not, and across the corpus the languages rotate so that no language carries more than a third of the examples and none fewer than a tenth.
- `critical` is not a craft severity. A data-loss or security defect belongs to a security or reliability corpus; craft severities stop at `major`.
- `## Source` stays in the card as a compact locator; the full citation, the fetch status, the formulation source and the reception live in `references/craft-cards-provenance.md`. Prose blocks stay attribution-free: no author, book or blog is named in a card.
- Self-containment is strict: a card names no sibling card id, no "the skill", no "see above". Its reader is a sub-agent holding the card, the hunks and the inventory, or a developer agent holding the card and its task.

### Numbering

Ids are assigned per domain in shipping order — the order in which topics complete — counting shipped cards only, two zero-padded digits, contiguous per domain; `references/craft-cards-provenance.md` records the topic of each card. A retired card leaves a gap that the validator warns about rather than renumbering its siblings, since findings, fixture seeds and provenance lines carry the id.

## Topic taxonomy

Ten topic groups, each one domain and one id prefix. The topics inside a group are the lower bound of coverage; the locators name where the canon formulates the topic (CC — *Code Complete*, 2nd ed., by chapter; SW — SWEBOK Guide V4.0 chapter 4, by section, chapter 3 where noted; SEG — *Software Engineering at Google*, by chapter; PP — *The Pragmatic Programmer*, 20th anniversary edition, by topic; PoP — *The Practice of Programming*, by chapter; APOSD — *A Philosophy of Software Design*; WELC — *Working Effectively with Legacy Code*; TF — *Tidy First?*). The canon names formulations only; evidence is a separate layer (§Source policy). A topic marked contested is one on which the authors of *Clean Code* and of *A Philosophy of Software Design* disagree in public; §Contested rules says what its cards do.

| Group, domain, prefix | Topic slug (`research/software-craft/<slug>.md`) | Formulation locators |
|--|--|--|
| A, `code`, `CODE` | `naming-identifiers` | CC11, PP "Naming Things", PoP1 |
| | `comments-and-self-documenting-code` (contested) | CC32, APOSD ch. "Comments" |
| | `layout-and-coding-style` | CC31, SEG8 |
| | `routine-size-and-parameters` (contested) | CC7 |
| | `variables-scope-and-numerics` | CC10–13 |
| | `control-flow` | CC14–17, CC19 |
| | `table-driven-and-state-machines` | CC18, SW4.7 |
| | `generics-and-parameterization` | SW4.3 |
| B, `design`, `DSN` | `complexity-and-deep-modules` | SW1.1, APOSD |
| | `information-hiding-and-encapsulation` | CC5, CC6 |
| | `coupling-and-dependency-direction` | PP "Orthogonality", "Decoupling" |
| | `duplication-and-single-source-of-truth` | PP "DRY" |
| | `inheritance-versus-composition` | PP "Inheritance Tax", CC6 |
| | `design-patterns-in-construction` | SWEBOK ch. 3 §4.4 |
| | `mutable-state-and-immutability` | PP "Shared State Is Incorrect State" |
| | `functional-style-and-pipelines` | PP "Transforming Programming" |
| | `domain-modeling-and-domain-language` | PP "Domain Languages", SWEBOK ch. 3 §5.10 |
| C, `interface`, `API` | `api-design-and-use` | SW4.1 |
| | `contracts-assertions-and-invariants` | PP "Design by Contract", SW4.4, CC8 |
| | `api-evolution-and-deprecation` | SEG15, SEG21 |
| D, `errors`, `ERR` | `error-and-exception-handling` | SW4.5, CC8, PP "Dead Programs Tell No Lies" |
| | `defensive-programming` | CC8, SW4.4 |
| | `fault-tolerance-retries-timeouts-fallbacks` | SW4.5 |
| | `resource-management-and-ownership` | PP "How to Balance Resources" |
| | `logging-and-diagnostic-output` | no canon chapter; researched from the evidence layer |
| E, `tests`, `TST` | `unit-testing-and-test-quality` | CC22, SEG12 |
| | `test-first-and-test-driven-development` (contested) | SW4.16, PP "Test to Code" |
| | `test-doubles` | SEG13 |
| | `larger-tests-integration-and-end-to-end` | SEG14 |
| | `property-based-testing` | PP "Property-Based Testing" |
| F, `change`, `CHG` | `refactoring` | CC24, PP "Refactoring" |
| | `code-smells-and-antipatterns` | CC24 |
| | `seams-and-characterization-tests` | WELC |
| | `large-scale-changes-and-migrations` | SEG22, SW3.8 |
| | `small-steps-and-minimal-diffs` | TF |
| | `technical-debt` | PP "Software Entropy" |
| G, `performance`, `PRF` | `debugging` | CC23, PoP5, PP "Debugging" |
| | `profiling-and-code-tuning` | CC25–26, PoP7, SW4.14 |
| | `algorithm-and-data-structure-choice` | PoP2, PP "Algorithm Speed" |
| H, `tooling`, `TOOL` | `build-warnings-static-analysis-ci` | SEG18, SEG20, SEG23, PP "Pragmatic Starter Kit" |
| | `dependency-management` | SW2.4, SEG21 |
| | `runtime-configuration` | SW4.8, PP "Configuration" |
| | `internationalization-and-text-encoding` | SW4.8 |
| I, `docs`, `DOC` | `reading-and-understanding-code` | no canon chapter; researched from the evidence layer |
| | `code-review-as-author-and-reviewer` | CC21, SEG9 |
| | `documentation-beyond-comments` | SEG10 |
| J, `input`, `INP` | `parsing-and-grammar-based-input` | SW4.9, PoP9 |
| | `security-hygiene-in-ordinary-code` | PP "Stay Safe Out There", SWEBOK ch. 3 §3.7 |

Forty-six topics. §Deviations records every topic the research adds beyond this table, with its source.

Concept ownership between neighbouring topics, decided at carding time so that one concept has one card:

| Concept | Owner topic | The neighbour yields |
|--|--|--|
| Validation of a value that crosses a trust boundary | `security-hygiene-in-ordinary-code` | `defensive-programming` keeps preconditions and fail-fast inside the trust boundary |
| A comment that restates the code, or a missing why-comment | `comments-and-self-documenting-code` | `documentation-beyond-comments` keeps documents outside the source |
| Routine length and parameter count | `routine-size-and-parameters` | `complexity-and-deep-modules` keeps module depth and interface width |
| Duplicated code blocks | `duplication-and-single-source-of-truth` | `code-smells-and-antipatterns` keeps the smells with no owner of their own |
| A retried, timed-out or fallen-back remote call | `fault-tolerance-retries-timeouts-fallbacks` | `error-and-exception-handling` keeps the local handling of a failure |
| A test that mocks what it should not | `test-doubles` | `unit-testing-and-test-quality` keeps assertion and structure |
| The size and shape of one change | `small-steps-and-minimal-diffs` | `code-review-as-author-and-reviewer` keeps the description and the reviewer's reading |
| A magic number or a global variable | `variables-scope-and-numerics` | `mutable-state-and-immutability` keeps shared mutable state between components |

Reserved specialties are outside the corpus and outside the developer agent's mandate: low-latency and high-frequency-trading tuning, concurrency correctness, security-critical design, machine-learning or algorithm research. The agent names the specialty in its report and stops. Distributed systems, middleware, cross-platform construction, process and team management, estimation, and product or UX decisions are outside the corpus too.

## Controlled vocabulary

`references/craft-cards-taxonomy.md` owns the allowed values and their definitions. The design reasons:

- `step` has seven values because the developer agent's work has seven moments at which it loads cards: `design`, `implement`, `handle-errors`, `test`, `refactor`, `document`, `review`. A card lists every moment at which its rule is applied while writing, not only the one where the defect is found; `review` is reserved for rules about the shape and description of the change itself.
- `applies_to` is `universal` for a rule that holds in every mainstream language and paradigm; otherwise it names a paradigm (`object-oriented`, `functional`), a boundary kind (`public-api`, `service-boundary`, `library`), a language trait (`exceptions`, `result-types`, `garbage-collected`, `manual-memory`, `static-types`, `dynamic-types`) or a file kind (`tests`, `build-config`, `prose`). A rule that holds only in one language is not carded here; it belongs to a language-specific corpus.
- `scope`, `check_kind` and the tiers keep the Java review corpus's meanings, so the two review workflows read a card the same way.
- Severity has three values:
  - `major` — a correctness or maintainability defect the card's evidence ties to failures or to measured cost;
  - `minor` — a clarity or design cost;
  - `suggestion` — style, naming, documentation.

## Structural signals

The pre-pass computes a fixed list of language-neutral signals per hunk from the diff and the file at HEAD (or in the working tree), so that a card can dispatch on shape rather than on vocabulary. A card names one with the trigger `signal:<name>`; the pre-pass threshold is a coarse net, and the card's Validator applies the rule's own bound. `scripts/static-craft.py` (`SIGNALS`) is the runtime owner; each signal has a unit test per fixture language.

| Signal | Level | Measured as | Fires when |
|--|--|--|--|
| `long_routine` | hunk | the line count of the routine enclosing an added line, by brace matching in Java, TypeScript, Go and Rust and by indentation in Python | any enclosing routine is longer than 40 lines |
| `deep_nesting` | hunk | the block depth of an added line inside its routine, by braces or indentation | depth of 4 or more |
| `many_parameters` | hunk | the parameter count on an added routine-signature line | 5 or more |
| `boolean_argument` | hunk | a boolean literal (`true`, `false`, `True`, `False`) as a call argument on an added line | one or more |
| `empty_handler` | hunk | a `catch`, `except`, `rescue` or `if err != nil` block whose body is empty, `pass`, a bare `return` or a discarded error | one or more |
| `magic_number` | hunk | a numeric literal other than 0, 1, 2, -1 and 100 on an added line that is not a constant declaration, an enum member, an annotation or a test | one or more |
| `commented_out_code` | hunk | two or more consecutive comment lines carrying statement syntax | one run or more |
| `todo_marker` | hunk | `TODO`, `FIXME`, `HACK` or `XXX` in an added comment | one or more |
| `duplicate_block` | file | a run of six or more non-blank added lines, whitespace-normalized, that occurs twice among the diff's added lines | one or more |
| `test_file` | file | a path or name matching a test convention: `test_*.py`, `*_test.py`, `*_test.go`, `*Test.java`, `*Tests.java`, `*.test.ts`, `*.spec.ts`, a `test/`, `tests/`, `__tests__/` or `spec/` directory | classification; also decides slicing and `applies_to: [tests]` |
| `added_file` | file | the diff status `added` | classification |

Every signal carries its measured value in `plan.json` (`inventory.files[].hunks[].signals`), so a finder reads the number rather than re-deriving it.

## Contested rules

Where the canon disagrees — routine length, comments, test-first among them — a card states the rule in the scope where the evidence holds and carries in `## Limits` the condition that separates the cases, each side resting on its own openable evidence. Where no separating condition can be sourced, the rule has no card: it goes to `references/pending-evidence.md` under "no separating condition", with both positions and their formulation sources, so the next search starts where this one stopped. A card never presents a refuted position as a recommendation, and never flattens a disagreement into a rule by picking the louder side.

## Concept ownership and priority

Two mechanisms keep one defect from surfacing twice. At carding time a concept has one owner (§Topic taxonomy). At aggregation time, when two cards still flag one span, a rule-level defer map and a domain-priority order decide; `SKILL.md` §Aggregation is the runtime owner of both and `scripts/craft-review-workflow.js` encodes them.

`DEFER_TO` — a deferring `rule_id` and its owner(s); a finding drops when its owner also flagged the same span. The map is filled from the pairs the corpus reviewers find still overlapping after the series; until then it is empty.

`DOMAIN_PRIORITY` for a genuine conflict (same span, incompatible fixes):

| Priority | Domain |
|--|--|
| 0 | `input` |
| 1 | `errors`, `interface`, `project`, `logic` |
| 2 | `design`, `tests`, `change` |
| 3 | `performance` |
| 4 | `code`, `docs`, `tooling` |

The order follows what a wrong fix costs: a validation defect at a trust boundary outranks a failure-handling defect, which outranks a structural one, which outranks a performance cost, which outranks a readability cost. A tie at the top keeps both findings and flags them for the author. Two fixes are compatible when one fix's code, whitespace-normalized, equals or contains the other; the higher-priority finding is kept and the other's `rule_id` is appended to `also`.

## Pre-pass contract — `craft/plan.json`

`scripts/static-craft.py` reads `git diff -U0` over text files, every card's frontmatter and `.claude/software-craft/config.md`; it writes `craft/plan.json` and `craft/plan.log` in the repository under review and nothing else. Standard library only, no network. `diff_ref` is a range, a commit, or absent — the working tree against `HEAD`, staged and unstaged, since the developer agent's diff is uncommitted.

```
{
  "inventory": {
    "mode": "committed" | "worktree",
    "diff_ref": "<base_sha>...<head_sha>" | "<base_sha>...worktree",
    "base_sha": "...", "head_sha": "..." | "worktree",
    "path_filter": "", "size_class": "SMALL" | "MEDIUM" | "LARGE",   // 1-19, 20-49, 50+ changed files
    "file_count": N, "languages": { "python": 3, "go": 1 },
    "files": [ { "path": "src/pkg/mod.py", "language": "python",
                 "kind": "source" | "test" | "config" | "docs" | "build",
                 "status": "added" | "modified" | "renamed", "group": "src/pkg",
                 "hunks": [ { "start": 42, "base_start": 40,
                              "lines": [ { "no": 42, "text": "..." } ],
                              "signals": { "long_routine": 57, "boolean_argument": 1 } } ],
                 "signals": { "test_file": false, "added_file": false, "duplicate_block": 0 },
                 "added_lines": N, "removed_lines": N } ],
    "skipped": [ { "path": "vendor/x.js", "reason": "vendored" | "generated" | "minified" | "lock" | "binary" | "unknown-language" } ],
    "config_path": ".claude/software-craft/config.md" | null, "config_changed": bool, "config": { ... } | null
  },
  "cards": [ { "rule_id": "CODE-03", "path": "/abs/.../code-03--....md", "title": "...", "domain": "code",
               "step": ["implement"], "applies_to": ["universal"], "triggers": ["..."],
               "scope": "hunk", "check_kind": "mechanical", "severity_default": "minor" } ],
                                                          // the dispatched cards only
  "jobs": [ { "id": "CODE-03:all", "rule_id": "CODE-03",
              "slice": { "name": "all",
                         "files": [ { "path": "...", "hunks": [ 0, 2 ], "added_lines": N,
                                      "matched": { "patterns": [ "..." ], "signals": [ "long_routine" ] } } ],
                         "added_lines": N } } ],
  "slices": [ { "name": "src/pkg", "languages": ["python"], "files": [ "..." ], "added_lines": N } ],
  "candidates": [ { "id": "empty-handler", "rule_id": "ERR-NN" | null, "file": "...", "line": 17,
                    "text": "...", "status": "needs_verification" } ],
  "project_cards": { "cards": [ { "rule_id": "PROJ-1", "title": "...", "thesis": "...", "validator": "...",
                                  "rationale": "..." } ],
                     "card_paths": [ ".claude/software-craft/cards/x.md" ] }
}
```

The deny-list, documented in the script, skips a file for one of six reasons:

- vendored: a tree under `vendor/`, `node_modules/`, `third_party/`, `.venv/`, `target/`, `build/` or `dist/`;
- generated: a `generated` or `DO NOT EDIT` marker in the first five lines, or a name such as `*_pb2.py`, `*.pb.go`, `*_generated.*`;
- minified: `*.min.js`, `*.min.css`, or an average line longer than 400 characters;
- lock: `package-lock.json`, `yarn.lock`, `pnpm-lock.yaml`, `Cargo.lock`, `poetry.lock`, `Pipfile.lock`, `go.sum`, `composer.lock`, `Gemfile.lock`;
- binary: git reports no text diff;
- unknown-language: an extension the language table does not name.

Language detection is by extension; the finder's `fix` is written in the file's language.

Job construction: for each card, the slice is the set of files whose added lines match any pattern or whose hunks carry the named signal, carrying only the matching hunks by index into the inventory record, so no hunk text repeats and the plan travels as a bundle. A card's slice stays one job while its added lines total at most 400; above that it splits by the config's `modules` (`[{name, paths: [..]}]`) or by directory prefix. The total is capped at 96 jobs, and `craft/plan.log` records every merge and drop the cap forces:

1. the jobs of the card with the most jobs are merged back into one, repeated while any card holds more than one job;
2. then the smallest `suggestion` job is dropped;
3. then the smallest `minor` job;
4. a `major` job is never dropped: the log records by how much the cap is exceeded and every job is kept.

Logic-pass slices are three to eight file groups by module or directory prefix, tests sliced apart from sources; fewer than three files means one slice per file.

Candidates are mechanical hits the pre-pass names outright, tagged `needs_verification`: the `empty_handler`, `boolean_argument`, `commented_out_code` and `todo_marker` signals per line, plus a `return null` / `return None` / `return nil` from a routine whose signature declares a collection type, and a `print` / `console.log` / `System.out` / `fmt.Println` / `println!` outside a test or a `main`. Project cards follow the Java review's shape: the numbered invariants in the body of `config.md` become `PROJ-N` cards (the invariant shape is `N. **Title**: rule. Violation: consequence.`), and files under `.claude/software-craft/cards/*.md` are indexed as written.

## Review workflow contracts

`scripts/craft-review-workflow.js`, run as a bundle: `scripts/bundle-run.py` embeds `root`, `stage`, `plan`, `design_intent`, `project_context`, `findings`, `tiers` and `agentTypes` as `const EMBEDDED_ARGS` after the script's `meta` block and writes `craft/run.js`, which the orchestrator calls through `Workflow({ scriptPath })` with no `args`. The phases:

1. Find — one finder per job at the card's tier, one logic pass per slice, one finder per (project card × slice).
2. Aggregate — deterministic JS.
3. Verify — one skeptic per finding.
4. Refute — a rejected Major gets a second skeptic and, when the defense holds, an arbiter.

Tiers, overridable through `tiers`; no stage runs on Fable, and a model naming Fable is rejected loud:

| Tier | Model | Effort | Runs |
|--|--|--|--|
| `mechanical` | `claude-opus-5-5` | `high` | finders of mechanical cards |
| `semantic` | `claude-opus-5-5` | `xhigh` | finders of semantic cards, the logic pass, project cards; skeptics of Minor and Suggestion findings |
| `verdict` | `claude-opus-5-5` | `max` | skeptics of Major findings; every second skeptic and arbiter |

Schemas: `FINDINGS` — `{ findings: [ { rule_id, severity ∈ {major, minor, suggestion}, file, symbol, code, problem, fix, rationale } ] }`, `code` verbatim from the diff and `fix` in the file's language; `VERDICT` — `{ verdict ∈ {confirmed, rejected, downgraded, upgraded, modified}, evidence, final_severity, note, corrected_finding? }`; `REFUTATION` — `{ refuted, evidence, note }`; `RULING` — `{ ruling ∈ {upheld, refuted, uncertain}, evidence, final_severity, note }`. Stages: `find` returns the aggregated findings for `craft/findings.json`; `verify` takes them back and skips Find; `all` runs both. `main_agent_followups` carries the integrity check, because the workflow runtime grants Write and Edit to sub-agents regardless of their `tools:` allowlist (claude-code#63762).

The finder prompt names the card path, the slice files and hunks with their signals, the card's scope, the candidates for that card, the design intent, the project context and the empty-case rule, and wraps hunks, intent, context and candidates in `<target_excerpt>` tags as untrusted data. The skeptic prompt is adversarial and refutes only with something it opened.

## Fix round

Confirmed findings go back to the developer agent once, with the write zone unchanged; the pre-pass and the workflow run again on the fix diff at `stage: verify` over the re-found set. One round; what remains is reported. The developer agent launches no sub-agents and performs no version-control write; the skill performs none either.

## Research workflow

`scripts/research-topic-workflow.js` is the authoring pipeline for one topic, kept in the repository so a topic can be re-researched or a new one added the same way. Arguments: the topic (slug, title, group, domain, prefix, locators, the candidate evidence titles), the next free id in the domain, the titles of the cards already shipped, and the channel policy. Phases:

1. Sources — three agents in parallel, one per layer of the research protocol, each returning locators, quotes and a fetch status through a schema: formulation (what the canon says, read through openable forms where one exists), reception (critiques, defenses, the threads where the canon is argued, practitioner surveys as a freshness check, the tool rule catalogs as the record of what is checked mechanically), evidence (the research, standard, documentation or hands-on test that backs each candidate rule).
2. Spine — one agent merges the three layers into candidate rules in source order, each with its formulation locator, its reception (contested or not, by whom), its evidence anchor or the search that found none, its checkability on a diff, and its proposed facets.
3. Draft — one agent per candidate rule writes the card, its provenance line and, where evidence is missing, its pending entry.
4. Verify — one skeptic per draft checks entailment of the Thesis by the evidence, self-containment, the Example's compilability in its language, the trigger's sanity and the separating condition of a contested rule, and returns a verdict with the edit it requires.
5. Fix — the drafter applies the verdict once; a draft rejected twice goes to pending.

Every agent names `model: 'claude-opus-5-5'`; effort `xhigh` for the source, spine and draft agents and `max` for the skeptic. The workflow writes no files: it returns the research note body, the cards, the provenance lines and the pending entries, and the orchestrator writes them, runs the validator and the audit, and commits. The research note's frontmatter `status: researched | drafted | verified | done` is the run's durable state: on start, the work list is derived from these files and continues from the first topic not `done`.

## Source policy

Every card cites one admissible class of the repository's Evidence-Based Rule, in a form anyone can open: academic research (an arXiv id or a DOI); a technical standard or official documentation — an IEEE or ISO/IEC standard by clause, the SWEBOK Guide V4.0 by section, an RFC by section, a language specification or its official documentation, a SEI CERT rule, a CWE entry, an OWASP cheat sheet or ASVS item, or a static-analysis rule page (SonarSource RSPEC, PMD, Checkstyle, ESLint, Pylint, Ruff, `go vet`, `clippy`, Error Prone, SpotBugs, Semgrep) as documentation of a check tools run in practice; or verified hands-on experience in an openable form — a test under `evals/fixture/`, a benchmark in a public repository, a linked gist or commit. A trade book, a practitioner blog, a talk or a forum thread is never evidence; it is the formulation a rule follows and the reception it met, named in the provenance map and the topic's research note, never inside a card.

Fetch status, recorded per citation on the provenance line:

- `fetched` — opened from the authoring environment and quoted. The channel is GitHub-hosted content (`raw.githubusercontent.com`): the tool rule documentation of ESLint, Error Prone, PMD, Checkstyle, Pylint, Ruff, `go vet`, clippy, SpotBugs, Semgrep and the SonarSource language plugins; official documentation whose source is on GitHub (CPython, the Go specification and Effective Go, the Rust book, reference and API guidelines, the TypeScript handbook, the OpenJDK sources, the PEPs, Google's style guides and engineering practices, the OWASP cheat sheets and ASVS, the httpwg RFC sources, the tz database, semver); the CC-licensed *97 Things* repository; the public discussion of the authors of APOSD and *Clean Code*; plus `pkg.go.dev` for Go package documentation.
- `relayed` — the paper itself could not be opened, and the search index's summary of it states the claim with its number; the card's Thesis carries no more than the relayed statement, and the provenance line quotes it.
- `unfetched` — cited from memory with no relayed statement; such a citation backs no card. When a rule's only anchor is unfetched, the rule goes to `references/pending-evidence.md`.

A card's evidence is fetched or relayed; the drafter and the skeptic confirm that the anchored section states the claim as the card words it — no inversion, no stripped precondition, no conditional flattened to an absolute — and a rule with no such anchor is not shipped. Where a fetched tool-rule page and a relayed paper back one rule, the card cites both and the fetched page is the first locator.

## Evals and fixture

`evals/fixture/base/` and `evals/fixture/head/` hold a small tree in at least three of the five languages, plain sources with no build. The head tree introduces one seeded defect per seeded card across every domain, at least three seeds per domain, plus controls that must yield no finding: their suspicious-looking code is correct by a stated tolerance — a comment, a documented project tolerance, a scope the card's Limits name. `make-fixture.sh` builds a temporary git repository with two commits so the pre-pass and the finders run on a real `diff_ref`; its second mode leaves the head tree uncommitted so the working-tree path is graded too. `expected.json` lists per seed the expected `(rule_id, file, symbol)` and per control the rule ids that must stay silent; `evals/grade.py` grades mechanically on those triples. `evals.json` records the grading, the pinned models, and the constraints satisfied and unsatisfied; the developer agent's own build path is graded by one smoke task on the fixture whose result is checked by the review workflow and by the tests the agent wrote, named as a single-run, unrepeated measurement.

## Progress

The tree is the state: each topic's research note carries `status`, each card exists or does not, each step's gate leaves a committed artifact. The table names the step gates and their state.

| Step | Gate | State |
|--|--|--|
| 1 Design note and taxonomy | both audit clean as `doc` | open |
| 2 Pilot: `research-topic-workflow.js` on naming, error handling, test doubles; `validate-craft-cards.py` | validator clean, audit clean, every Source fetched or relayed and entailed, research notes complete with cost lines | open |
| 3 Scripts and agents: `static-craft.py` and tests, `craft-cards.py`, `bundle-run.py`, `craft-review-workflow.js`, `render-reports.py`, three agent definitions | tests pass, workflow scripts pass the wrapped syntax check, agents audit clean | open |
| 4 Dry run: fixture for the pilot cards in three languages, both pre-pass modes, workflow, grading, smoke task | every seed found, every control silent; the smoke task builds, its tests pass, its review report is written | open |
| 5 Series: every remaining topic in batches, one reviewer per domain, corpus audit, fixture to three seeds per domain | validator, audit and grading clean, `pending-evidence.md` complete, every note `done`, provenance round-trip holds | open |
| 6 Close: SKILL.md, READMEs, maintenance, gotchas, report format, `overview.sh`, versions, final audit | final audit clean | open |

## Cost

Per topic, the research workflow runs 3 source agents, 1 spine agent, and per candidate rule one drafter, one skeptic and at most one fix. The measured cost per pilot topic and the projection for the series are recorded here once the pilot has run.

## Deviations from the brief

The brief is the operator's handover message that commissioned this build; it is not a file in the repository, so each entry quotes the instruction it deviates from and states the determining reason.

1. Branch. The brief says "Work on branch `feat/software-craft`". I commit and push the work on the branch the session environment designates, `claude/youthful-thompson-m7gj89`, because that environment binds pushes to its designated branch and the operator follows it in the session view.
2. Fetch channel. The brief says "Fetch every source you cite and confirm the anchored section states the claim as the card words it" and, for the pilot gate, "every `## Source` fetched and entailed". The environment's egress policy denies arXiv, doi.org, the publishers, the vendors' documentation sites and the search engines, and admits GitHub-hosted content, `pkg.go.dev` and the search tool. A paper therefore enters a card only as `relayed` — the search index's statement of the claim with its number — and a standard or tool rule as `fetched` from its GitHub source, as §Source policy states; the pilot gate reads "fetched or relayed, and entailed". I have not re-verified the relayed citations against the papers themselves; an environment with arXiv access can, and that re-verification is open for the operator.
3. Agent types. The brief names the types `code-quality:craft-finder`, `code-quality:craft-verifier` and `code-quality:software-developer`. A probe of the workflow runtime in this checkout shows a plugin's types resolve only where the plugin is installed, so every workflow run here dispatches the default sub-agent with the same prompts, and the smoke task runs the developer definition's body as a general-purpose agent's prompt; `evals.json` says so.
4. Skill preloading. The brief says the developer agent preloads the skill through `skills:` "where the current Claude Code documentation confirms that field exists for plugin agents". The subagent reference (`code.claude.com/docs/en/sub-agents.md`, the `skills` row of its frontmatter table) and the plugin components reference (`code.claude.com/docs/en/plugins/components.md`, its list of supported agent fields) confirm the field for plugin agents and show bare skill names in the example; neither page names a plugin-qualified form, and neither says whether a preloaded skill's `disallowed-tools` binds the agent. The agent therefore preloads `software-craft` by bare name and its body also names the card index script by path, so the agent works where the field does not resolve. I have not verified whether the preloaded skill's `disallowed-tools: Edit` reaches the agent; a session with the plugin installed can, and that check is open for the operator.
5. Topic slug. The brief names the topic "legacy code, seams, characterization tests". The research note is `seams-and-characterization-tests`, because the corpus's audit treats the word in the brief's title as a marker of a superseded design on every run, and the two mechanisms named are the topic's content.
6. Skill name. The brief names the skill `software-craft`. The audit's naming rule asks for a verb and an object in a skill name; the brief's name stays, because the layout, the developer agent's `skills:` field and the marketplace README address the skill by it, and its description carries the verbs and the objects.

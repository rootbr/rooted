# Craft-cards taxonomy & corpus schema

Out-of-runtime maintainer doc. Defines the controlled vocabulary, which `scripts/validate-craft-cards.py` validates facet by facet, and the corpus-local card schema. Neither consumer receives this file: the developer agent receives the card index and the cards it opens, and the review workflow passes a card to its finder. Paths in this document are relative to `plugins/code-quality/skills/software-craft/`.

This corpus is a specialization of `plugins/evidence-based-authoring/skills/auditing-ai-context/references/kb-card-specification.md` for two consumption models of one card. The developer agent retrieves cards by facet and title — the base specification's facet filter and index scan — before a step of its work and reads the ones whose titles apply. The review finder receives one card, dispatched whole, and reads it in isolation with the diff hunks whose added lines matched the card's triggers, the inventory, and what the card's `scope` lets it open. The deltas from the base specification follow from serving both.

## How this corpus specializes the KB card spec

| Spec feature | Here | Why |
|--|--|--|
| `links` + linker | dropped | a card is retrieved by facet and title or dispatched; it is never traversed |
| `tags` (grep index) | dropped | the developer scans titles by facet, and the pre-pass matches `triggers` against the diff; no agent greps the pool |
| Facets (retrieval filter) | kept for the developer as `step` and `applies_to`; added for the finder as the dispatch facet `triggers` and the reading-budget facet `scope` | two consumers, two facet sets on one card |
| `confidence` facet | dropped from the card; recorded in the provenance map | neither consumer weighs evidence strength at runtime |
| Inline citation | a compact locator stays in the card (`## Source`); the full citation, its fetch status, the formulation source and the reception go to the provenance map | the human reading a finding and the verifier calibrating it benefit from the locator; the prose stays attribution-free, so C-E2's core concern holds. A documented deviation from C-A5 (provenance-out-of-card), the same one the audit and review corpora document |
| `## Example` form (C-F3) | a fenced `bad:` / `good:` pair in one of five languages, defined under Body block schema | a three-line everyday-domain pair cannot carry a programming defect; the reader is a programmer and the defect is the card's own. A documented deviation from C-F3 |
| Numbers in claims | kept in the card | C-E3: the number is the load-bearing part |
| Self-containedness (group C) | strict: no sibling-rule ids, no "the skill", no "see above", no author, book or blog | each reader sees only its card plus the hunks and the inventory, or the card plus its task |
| Cross-card concerns (ownership / defer, conflict priority) | in `scripts/craft-review-workflow.js` (`DEFER_TO`, `DOMAIN_PRIORITY`), keyed by `rule_id` / `domain` | orchestration belongs to the workflow, and the atom stays free of it |

## Frontmatter fields

Exactly these keys, all required, in this order; the validator rejects any other key or order.

| Field | Meaning |
|--|--|
| `title` | the rule as one complete, checkable declarative claim (C-A1); identical to the H1 |
| `rule_id` | stable id `<PREFIX>-NN`; the finder stamps it on every finding and the workflow dedups and applies ownership by it. A finding is `<rule_id>.<ordinal>` |
| `domain` | the owning topic group; decides conflict priority. The prefix and the domain agree by the table under Allowed values |
| `step` | inline list of the moments in the developer's work at which the developer loads the card; the developer's retrieval facet |
| `applies_to` | inline list: `[universal]`, or the named scopes where the rule holds; a self-restriction (C-C3) |
| `triggers` | inline list of Python `re` patterns, each matched with `re.search` against one added line of the diff at a time in any language, or `signal:<name>` naming a structural signal the pre-pass computes; a card runs on a file when any pattern matches any added line or any hunk carries the named signal. `[]` means every diff and is reserved for a handful of always-on cards |
| `scope` | what the finder reads beyond the matched hunk |
| `check_kind` | `mechanical` or `semantic`, defined under Allowed values |
| `severity_default` | the severity the finder emits; the verifier calibrates |

Lists are YAML inline lists of quoted strings, `['a', 'b']`; `step` and `applies_to` values may be bare.

## Allowed values

| Facet | Value | Meaning |
|--|--|--|
| `rule_id` prefix, `domain` | `CODE-`, `code` | code inside a function: naming, comments, layout, routine shape, variables and numerics, control flow, table-driven and state-machine construction, generics |
| | `DSN-`, `design` | module design: complexity and depth, information hiding, coupling and dependency direction, duplication, inheritance and composition, patterns, mutable state, functional style, domain modeling |
| | `API-`, `interface` | interfaces: API design and use, contracts and assertions, evolution and deprecation |
| | `ERR-`, `errors` | errors and resilience: error and exception handling, defensive programming, fault tolerance, resource management, logging |
| | `TST-`, `tests` | tests: unit testing and test quality, test-first, test doubles, larger tests, property-based testing |
| | `CHG-`, `change` | changing code: refactoring, smells, seams and characterization tests, large-scale change, small steps, technical debt |
| | `PRF-`, `performance` | diagnostics and performance: debugging, profiling and tuning, algorithm and data-structure choice |
| | `TOOL-`, `tooling` | tools and hygiene: build, warnings, static analysis, CI, dependencies, runtime configuration, internationalization and encoding |
| | `DOC-`, `docs` | reading and documenting: reading code, code review as author and reviewer, documentation beyond comments |
| | `INP-`, `input` | input and security hygiene: parsing and grammar-based input, security hygiene in ordinary code |
| | `PROJ-`, `project` | a project card synthesized from a project's `config.md`; never shipped with the plugin |
| `step` | `design` | shaping a module, its interface, its data and its dependencies before code is written |
| | `implement` | writing the body of a routine, a type or a data structure |
| | `handle-errors` | deciding what code does on failure: exceptions or results, validation, resources, logging |
| | `test` | writing or changing tests |
| | `refactor` | changing structure while keeping behaviour |
| | `document` | writing comments, doc-comments, READMEs and change descriptions |
| | `review` | the self-review before the report: the shape, size and description of the change |
| `applies_to` | `universal` | every mainstream language and paradigm; stands alone |
| | `object-oriented`, `functional` | a paradigm |
| | `public-api`, `service-boundary`, `library` | a boundary kind: an interface other code depends on, a process or network boundary, code shipped for others to call |
| | `exceptions`, `result-types`, `garbage-collected`, `manual-memory`, `static-types`, `dynamic-types` | a language trait: how failures propagate, how memory is reclaimed, when types are checked |
| | `tests`, `build-config`, `prose` | a file kind: a test file, a build or configuration file, a document |
| `scope` | `hunk` | the added lines and their hunk context |
| | `file` | plus the whole file at HEAD or in the working tree |
| | `base-compare` | plus the base version via `git show <base_sha>:<path>` |
| | `callers` | plus usages of the changed symbols across the repository |
| `check_kind` | `mechanical` | the pattern or signal is the finding once one light context question is confirmed; routed to the `mechanical` tier |
| | `semantic` | the finder traces something (a call chain, a contract, a duplicate's divergence) before it can decide; routed to the `semantic` tier |
| `severity_default` | `major` | a correctness or maintainability defect the card's evidence ties to failures or to measured cost |
| | `minor` | a clarity or design cost |
| | `suggestion` | style, naming, documentation |
| `confidence` (provenance map only) | `high`, `moderate`, `low` | evidence strength recorded on the provenance line |
| fetch status (provenance map only) | `fetched`, `relayed`, `unfetched` | how the citation was verified from the authoring environment; a card's evidence is fetched or relayed |

`critical` is not a craft severity: a data-loss or security defect is another corpus's finding. Rule ids carry two zero-padded digits and are contiguous per domain in shipping order.

## Trigger discipline

- Broad beats narrow: a false trigger costs one finder that returns an empty array; a missed trigger costs a missed defect.
- A pattern is Python `re` syntax matched against added lines of every language, so it names the vocabulary of the defect as it appears across languages — the keyword family (`catch|except|rescue`), the call shape, the literal. A pattern that names one language's API matches the defect in that language and misses the same defect in every other. Escape parentheses (`'\b(catch|except|rescue)\b'`, `'[.]then\('`) and write a literal dot as a character class, so the pattern reads as a pattern rather than as a backslash path to a scanner. A pattern must compile; the validator compiles every one and rejects backslash-dot.
- A structural signal is named as `signal:<name>`, one of the names the design note lists under "Structural signals" and `scripts/static-craft.py` computes; the validator rejects a name outside that list. A signal is the trigger for a defect of shape — length, depth, arity, an empty block, a literal in an argument — that no vocabulary identifies.
- Prefer two to six triggers. A card takes `[]` only when the corpus can afford to run it on every diff; the corpus keeps that class to a handful.
- Triggers are case-sensitive except where a pattern says otherwise with `(?i)`.

## Body block schema (one schema across the corpus, C-F1)

In this order: `## Thesis` → `## Rationale` → `## Example` → `## Limits` → `## Validator` → `## Finding output` → `## Source`. Nothing before `## Thesis` but the H1; no other H2.

- `## Thesis` — the rule, one checkable claim, in the programmer's vocabulary: what the code must show, stated positively, with no language named.
- `## Rationale` — the mechanism and its numbers, attribution-free: why the defect costs what it costs, which property the rule restores. The Thesis or the Rationale carries every threshold, condition, identifier and qualifier the rule depends on.
- `## Example` — one fenced block tagged `java`, `python`, `typescript`, `go` or `rust`, holding a `bad:` line group and a `good:` line group, at most ten lines in total, with generic names. `{ ... }` or `...` marks an elided body and is the one non-code token allowed, so the `good:` half compiles in a plausible enclosing scope of that language once each elision gets a body; the fence carries no diff markers. Across the corpus the five languages rotate: no language carries more than a third of the examples and none fewer than a tenth; the validator reports the distribution.
- `## Limits` — when the pattern is correct: a documented project tolerance, a scope the rule does not reach, a language trait that changes the answer; for a contested rule, the condition that separates the cases, each side resting on its own evidence. The card's own bound, naming no sibling card. A tolerance stated in `project_context` rejects the finding; the Limits say which tolerance.
- `## Validator` — the operative check: what to grep in the hunk, what to open at the card's `scope`, what to trace, and one binary validator question in bold whose "yes" is the finding. Sentences are imperatives to the finder; the developer applies the same question to its own code before reporting.
- `## Finding output` — the consumer block (C-D2, one per card, one name per corpus). Its shape: "When the validator answers yes, the finder emits one finding (`rule_id: <ID>`, severity <severity_default>, `file`, `symbol`, `code` = <what to quote verbatim from the diff>, `fix` = <what the fix shows, in the file's language>, `rationale` = <what the rationale names>)." The `rule_id` in this block equals the frontmatter's. The developer reads the card whole and needs no second block.
- `## Source` — a compact locator of the admissible evidence: an arXiv id or DOI, an IEEE or ISO/IEC standard by clause, the SWEBOK Guide V4.0 by section, an RFC by section, a language specification or official documentation page by section, a SEI CERT rule id, a CWE id, an OWASP cheat sheet or ASVS item, a static-analysis rule id (a SonarSource RSPEC id, a PMD, Checkstyle, ESLint, Pylint, Ruff, `go vet`, clippy, Error Prone, SpotBugs or Semgrep rule name), or a fixture test path — plus any one-line caveat. A book, a blog, a talk or a course is named in the provenance map as the formulation the rule follows, and nowhere in the card. Not in-prose attribution (Thesis and Rationale stay attribution-free), so the spirit of C-E2 holds.

## Filename

`<prefix lower-case>-NN--<slug>.md`, the slug a lower-case ASCII kebab-case of the title's central claim, at most about sixty characters, in the shape `code-03--an-identifier-is-a-word-or-phrase-never-a-single-letter.md`. Renaming a slug means renaming its provenance line; nothing else references it.

## Provenance

`craft-cards-provenance.md` holds, keyed by `rule_id` and never loaded at runtime: the full citation with its fetch status, the topic and research note the card came from, the formulation source where a practitioner text supplied the wording, the reception (contested or not, and by whom), the evidence strength, and any ownership note. The card's `## Source` footer carries only a compact locator of the same citation. Round-trip rule: a card plus its provenance line plus its topic's research note reconstruct everything known about the rule.

A rule has no card and no id when it has no openable evidence, or when it is contested and no sourced condition separates the cases; it lives in `pending-evidence.md` with its original wording, its formulation source, its topic and what was searched.

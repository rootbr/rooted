# Review-cards taxonomy & corpus schema

Out-of-runtime maintainer doc. Defines the controlled vocabulary (for facet validation by `scripts/validate-review-cards.py`) and the corpus-local card schema. The review workflow passes a card to its finder; it never passes this file. Paths in this document are relative to `plugins/code-quality/skills/reviewing-java/`.

This corpus is a specialization of `plugins/evidence-based-authoring/skills/auditing-ai-context/references/kb-card-specification.md` for one consumption model: each card is **dispatched** to its own finder sub-agent (one card → one finder per diff slice), read in total isolation — not retrieved from a pool by facet, grep, or link. The finder holds the card, the diff hunks whose added lines matched the card's triggers, and the review inventory; nothing else. The deltas from the base spec follow from that.

## How this corpus specializes the KB card spec

| Spec feature | Here | Why |
|--|--|--|
| `links` + linker | dropped | cards are dispatched, never traversed: each is read alone |
| `tags` (grep index) | dropped | no agent greps the pool; the pre-pass matches `triggers` against the diff |
| Facets (retrieval filter) | repurposed as the **dispatch facet** `triggers` plus the reading-budget facet `scope` | the pre-pass selects which cards run on a diff and how much the finder reads |
| `confidence` facet | dropped from the card; recorded in the provenance map | the finder acts on the card, not on its evidence strength |
| Inline citation | a compact locator stays in the card (`## Source`); the full citation, origin section and formulation source go to the provenance map | the human reading a finding and the verifier calibrating it benefit from the locator; the prose stays attribution-free, so C-E2's core concern holds. A documented deviation from C-A5 (provenance-out-of-card), the same one the audit corpus documents |
| `## Example` form (C-F3) | a fenced Java `bad:` / `good:` pair of at most ten lines, with generic names (`cache`, `load`, `k`); `{ ... }` marks an elided method body and is the one non-Java token allowed, so a `good:` half compiles once each elision gets a body; no diff markers inside the fence; on a `meta` card the fence is still ```java for the validator but its lines are the config's Markdown invariants, since that card reads `config.md` | a three-line everyday-domain pair cannot carry a Java defect; the reader is a Java reviewer and the card's domain is its own. A documented deviation from C-F3 |
| Numbers in claims | kept in the card | C-E3: the number is the load-bearing part |
| Self-containedness (group C) | strict: no sibling-rule ids, no "the skill", no "the checklist", no "see above" | each finder sees only its card + the hunks + the inventory |
| Cross-card concerns (ownership / defer, conflict priority) | in `scripts/review-workflow.js` (`DEFER_TO`, `DOMAIN_PRIORITY`), keyed by `rule_id` / `domain` | orchestration is the workflow's job, not the atom's |

## Frontmatter fields

Exactly these keys, in this order; the validator rejects any other key or order.

| Field | Required | Meaning |
|--|--|--|
| `title` | yes | the rule as one complete, checkable declarative claim (C-A1); identical to the H1 |
| `rule_id` | yes | stable id; the finder stamps it on every finding and the workflow dedups and applies ownership by it. A finding is `<rule_id>.<ordinal>` |
| `domain` | yes | the owning domain; decides conflict priority |
| `triggers` | yes | list of Python `re` patterns, each matched with `re.search` against one added line of the diff at a time; a card runs on a file when any pattern matches any added line. `[]` means every diff and is reserved for a handful of always-on cards |
| `scope` | yes | what the finder reads beyond the matched hunk |
| `check_kind` | yes | `mechanical`: the pattern is the finding once one light context question is confirmed (hot path? user input? shared field?); `semantic`: the finder traces a chain, such as a happens-before edge, a taint path, a query inside a loop, an API contract |
| `severity_default` | yes | the severity the finder emits; the verifier calibrates |

`group` is not a field: the domain is the group.

## Allowed values

| Facet | Value | Meaning |
|--|--|--|
| `rule_id` prefix | `CC-` | domain `concurrency` |
| | `SEC-` | domain `security` |
| | `PF-` | domain `performance` |
| | `REL-` | domain `reliability` |
| | `MNT-` | domain `maintainability` |
| | `META-` | domain `meta` |
| | `PROJ-` | a project card synthesized from a project's `config.md`; never shipped with the plugin |
| `scope` | `hunk` | the added lines and their hunk context |
| | `file` | plus the whole file at HEAD |
| | `base-compare` | plus the base version via `git show <base_sha>:<path>` |
| | `callers` | plus usages of the changed symbols across the repository |
| `check_kind` | `mechanical` | the pattern is the finding once one light context question is confirmed |
| | `semantic` | the finder traces a chain before it can decide |
| `severity_default` | `critical` | data loss, a security breach (remote code execution, injection, auth bypass), data corruption under normal operation |
| | `major` | a correctness bug, a resource leak that degrades over time, a concurrency defect yielding wrong results, a security defect needing specific conditions |
| | `minor` | a performance cost, a clarity problem, missing error handling for an unlikely scenario |
| | `suggestion` | style, documentation, naming |
| `confidence` (provenance map only) | `high`, `moderate`, `low` | evidence strength recorded on the provenance line |

Rule ids carry two zero-padded digits and are contiguous per domain.

## Trigger discipline

- Broad beats narrow: a false trigger costs one finder that returns an empty array; a missed trigger costs a missed defect.
- Patterns are Python `re` syntax; escape parentheses (`'containsKey\('`) and write a literal dot as a character class (`'Files[.]lines\('`), so the pattern reads as a pattern rather than as a backslash path to a scanner. A pattern must compile; the validator compiles every one and rejects backslash-dot.
- Match the vocabulary of the defect as it appears in an added line — the API name, the keyword, the annotation — and also the vocabulary of the fix when the fix is a common site of the same defect (a `computeIfAbsent(` lambda that touches the same map).
- Prefer three to six patterns. Some defects have no lexical signature at all, the design-level rules among them: such a card takes `[]` only when the corpus can afford to run it on every diff, and otherwise names the constructs the defect lives in.
- Triggers are case-sensitive; Java identifiers are.

## Body block schema (one schema across the corpus, C-F1)

In this order: `## Thesis` → `## Rationale` → `## Example` → `## Limits` → `## Validator` → `## Finding output` → `## Source`. Nothing before `## Thesis` but the H1; no other H2.

- `## Thesis` — the rule, one checkable claim, in the reviewer's vocabulary: what the diff must show, stated positively.
- `## Rationale` — the mechanism and its numbers, attribution-free: why the defect occurs, what it costs, which guarantee the fix restores. Every threshold, condition, identifier and qualifier the rule depends on is here or in the Thesis.
- `## Example` — one fenced `java` block holding a `bad:` line group and a `good:` line group, at most ten lines in total, with generic names (`cache`, `load`, `k`). The `good:` half compiles in a plausible enclosing class once each `{ ... }` elision gets a body; the fence carries no diff markers.
- `## Limits` — when the pattern is correct: thread confinement, a lock around both calls, a documented project tolerance, a debug-only path, a JDK version boundary. The card's own bound, naming no sibling card. A tolerance stated in `project_context` rejects the finding; the Limits say which tolerance.
- `## Validator` — the operative check: what to grep in the hunk, what to open at the card's `scope`, what to trace, and one binary validator question in bold whose "yes" is the finding. Sentences are imperatives to the finder.
- `## Finding output` — the consumer block (C-D2, one per card, one name per corpus). Its shape: "When the validator answers yes, the finder emits one finding (`rule_id: <ID>`, severity <severity_default>, `file`, `symbol`, `code` = <what to quote verbatim from the diff>, `fix` = <what the fix shows>, `rationale` = <what the rationale names>)." The `rule_id` in this block equals the frontmatter's.
- `## Source` — a compact locator of the admissible source: a JDK 21 Javadoc page by class and member, a JLS or JVMS section, a JEP number, a Spring or Hibernate reference section, an OWASP cheat sheet or ASVS item, a CWE id, a SEI CERT Java rule id, a SonarSource RSPEC id, an RFC number and section, an arXiv id or DOI, a jcstress sample path, or a fixture test path — plus any one-line caveat. A book, a blog, a talk or a course is named in the provenance map as the formulation the rule follows, and nowhere in the card. Not in-prose attribution (Thesis and Rationale stay attribution-free), so the spirit of C-E2 holds.

## Filename

`<prefix lower-case>-NN--<slug>.md`, the slug a lower-case ASCII kebab-case of the title's central claim, at most about sixty characters (`cc-14--check-then-act-on-a-concurrent-map-is-one-compute-call.md`). Renaming a slug means renaming its provenance line; nothing else references it.

## Provenance

The full citation, the origin section in the source checklist, the formulation source where a practitioner text supplied the wording, the evidence strength, and any ownership note live in `review-cards-provenance.md` — keyed by `rule_id`, never loaded at runtime. The card's `## Source` footer carries only a compact locator of the same citation. Round-trip rule: a card plus its provenance line reconstruct everything known about the rule.

A rule that has no openable source has no card and no id; it lives in `pending-evidence.md` with its original wording, its unopenable source, its domain and what was searched.

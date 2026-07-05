# Rule-cards taxonomy & corpus schema

Out-of-runtime maintainer doc. Defines the controlled vocabulary (for facet validation) and the corpus-local card schema. The audit workflow does not pass this file to sub-agents.

This corpus is a specialization of `kb-card-specification.md` for one consumption model: each card is **dispatched** to its own audit sub-agent (one card → one sub-agent), read in total isolation — not retrieved from a pool by facet, grep, or link. The deltas from the base spec follow from that.

## How this corpus specializes the KB card spec

| Spec feature | Here | Why |
|---|---|---|
| `links` + linker | dropped | cards are dispatched, never traversed — each is read alone |
| `tags` (grep index) | dropped | no agent greps the pool |
| Facets (retrieval filter) | repurposed as the **dispatch facet** `applies_to_target` | the workflow selects which cards to run for a given target type |
| `group`, `confidence` facets | dropped from the card → provenance map | the sub-agent acts on neither; `group` is derivable from `rule_id` (workflow computes it), `confidence` is maintainer evidence-strength |
| Inline citation | a compact locator stays in the card (`## Source`); the full citation + analysis go to the provenance map | the auditor consumer and the human reviewer benefit from the locator; the prose stays attribution-free, so C-E2's core concern holds. A documented deviation from C-A5 (provenance-out-of-card), justified by this corpus's verification need |
| Numbers in claims | kept in the card | C-E3 — the number is the load-bearing part |
| Self-containedness (group C) | strict — no sibling-rule IDs, no "the skill", no deixis | each sub-agent sees only its card + the target + the inventory |
| Cross-card concerns (ownership/defer, conflict priority) | in `audit-workflow.js` (`DEFER_TO`, `GROUP_PRIORITY`), keyed by `rule_id`/`group` | orchestration is the workflow's job, not the atom's |

## Frontmatter fields

| Field | Required | Meaning |
|---|---|---|
| `title` | yes | the rule as one complete declarative claim (C-A1) |
| `rule_id` | yes | stable ID; the sub-agent stamps it on every patch, and the workflow dedups / applies ownership by it (e.g. `R-01`, `C-A1`) |
| `applies_to_target` | yes | dispatch facet — which target types run this card; not derivable, so declared here |
| `check_kind` | yes | `mechanical` (sub-agent can decide + propose a concrete patch) or `semantic` (needs judgement → tends to `needs_human`) |
| `severity_default` | yes | default patch severity the sub-agent emits |
| `defines` | optional | terms this card is the authority on within the corpus (usually omitted) |

No `links`, no `tags`. `group` and `confidence` are not card fields — `group` is computed from `rule_id` (R-01 → G1) by the workflow; `confidence` is recorded as `evidence` in the provenance map. The academic source stays as a compact `## Source` footer (see body schema).

## Allowed values

- `applies_to_target`: `context-file` · `skill` · `agent-prompt` · `kb-card` · `kb-corpus`
- `check_kind`: `mechanical` · `semantic`
- `severity_default`: `high` · `medium` · `low` · `info`
- `group` (mapper / workflow-derived, not a card field): `G1-routing` · `G2-tiering` · `G3-structure` · `G4-pointers` · `G5-sourcing` · `G6-constraints` · `G7-antipatterns` · `G8-security` · `G9-kb-card`
- `confidence` (recorded as `evidence` in the map, not a card field): `high` · `moderate` · `low`

## Body block schema (one schema across the corpus, C-F1)

In this order: `## Thesis` → `## Rationale` → `## Example` → `## Limits` → `## Validator` → `## Patch output` → `## Source`.

- **Thesis** — the rule, one checkable claim.
- **Rationale** — why it holds: the mechanism and its kept numbers (no source attribution — that is the `## Source` footer).
- **Example** — a fenced contrast pair, ≤ ~3 lines (C-F3): `bad: … / good: …` in the R-cards; the C-cards use the base spec's `rejected: … / accepted: …` labels — they model the convention of the corpora they audit.
- **Limits** — the rule's own scope and applicability bound; caveats and extrapolations (C-C3). States its boundary without naming sibling rules.
- **Validator** — the operative check the sub-agent runs (what to grep, what to flag, the validator question). Corpus-local block, added because an audit rule has an operative check distinct from its rationale.
- **Patch output** — the consumer block (C-D2, one per card, one name per corpus): when (the audit sub-task), who (this rule's audit sub-agent), where (emit a patch with this `rule_id` against the dispatch-supplied schema, or `needs_human` for a semantic call).
- **Source** — a compact provenance footer: the article + § / RFC + § / book + § the rule rests on, plus any one-line caveat. Not in-prose attribution (Thesis/Rationale stay attribution-free), so the spirit of C-E2 holds. Note: the audit sub-agent is read-only and usually cannot fetch the source at runtime, so the locator chiefly serves human verification of `needs_human` patches and model grounding; the full citation lives in the map.

## Provenance

The full citation, evidence basis, origin reference file, ownership, and house-heuristic flags live in `rule-cards-provenance.md` — keyed by `rule_id`, never loaded at runtime. The card's `## Source` footer carries only a compact locator of the same citation.

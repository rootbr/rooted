---
title: Frontmatter holds consumer fields only; provenance and dates belong in the provenance map
rule_id: C-A5
applies_to_target: [kb-card]
check_kind: mechanical
severity_default: high
---

# Frontmatter holds consumer fields only; provenance and dates belong in the provenance map

## Thesis
Frontmatter must contain only the fields the runtime consumer uses for retrieval and application. Service metadata — source citations, author, creation or revision dates, internal IDs — belongs in the external provenance map, not in the card.

## Rationale
Frontmatter is the retrieval index, and its value is the smallest set of high-signal tokens. Each service field dilutes that index: it adds tokens the consumer never filters or acts on, and it can be mistaken for a retrieval facet, confusing both extraction and application. Keeping provenance in a separate map, keyed back to the card, preserves the round-trip without loading dead weight at runtime.

## Example
```
rejected: frontmatter with  source: "Smith 2019"   created: 2026-01-04
accepted: frontmatter with retrieval facets only; source + date live in the provenance map
```

## Limits
Covers the frontmatter whitelist only. A compact source locator placed in the card body as a footer is a separate matter and is not a frontmatter field. A corpus may legitimately add a retrieval facet to its whitelist; the check flags only fields outside the agreed consumer set.

## Validator
Compare each frontmatter key against the allowed consumer-field whitelist; flag any key carrying provenance, dates, authorship, or internal service metadata. Validator question: does the consumer read this field to retrieve or apply the card, or is it maintainer bookkeeping that belongs in the map?

## Patch output
When auditing a card whose frontmatter carries a non-consumer field, emit one patch (`rule_id: C-A5`, `location.field` = the offending key, severity high) proposing its removal from frontmatter and relocation to the provenance map. The presence of a non-whitelisted key is mechanically decidable, so no `needs_human` flag.

## Source
KB card spec, identity/retrievability rules, group A (smallest set of high-signal tokens; service fields confuse retrieval and application).

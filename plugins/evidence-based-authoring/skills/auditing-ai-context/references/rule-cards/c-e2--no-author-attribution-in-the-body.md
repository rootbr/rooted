---
title: A card names an idea by what it is, never by the author or publication it came from
rule_id: C-E2
applies_to_target: [kb-card]
check_kind: mechanical
severity_default: high
---

# A card names an idea by what it is, never by the author or publication it came from

## Thesis
The body, title, and terminology must not attribute a method or idea to an author, publication, or upstream source. Name the idea by what it is and what it does, not by who proposed it. Attribution belongs in the external provenance map.

## Rationale
A consumer reading the card in isolation has none of the cited authors in context, so "X's method" or "the technique from <paper>" is unparseable — author-bound jargon names nothing the reader can resolve and is pure dead weight. An in-body attribution is also itself a piece of provenance, and provenance is kept in the map, not in the card the consumer acts on.

## Example
```
rejected: Apply Smith's two-session rule to long meetings.
accepted: Split any meeting longer than 90 minutes into two sessions.
```

## Limits
Covers attribution of an idea to its originator inside the card. A compact source locator in a dedicated footer block is the sanctioned place for provenance and is a separate matter. Using a person's name as a domain role the consumer acts on — not as the credited originator of the idea — is not attribution.

## Validator
Scan the title, thesis, rationale, and terminology against the store's source-name list and for possessive or citation patterns ("<Name>'s method", "the <Name> technique", "as <Author> showed", "per <publication>"). Flag any idea named by its originator. Validator question: is this idea named by what it is, or by who wrote it?

## Patch output
When auditing a card that attributes an idea to an author or publication in its prose, emit one patch (`rule_id: C-E2`, location of the attribution, severity high) rewriting it to name the idea by what it is and moving any provenance to the map. The presence of an attribution token is mechanically decidable, so no `needs_human` flag in the clear case.

## Source
KB card spec, faithfulness rules, group E (author-bound jargon is dead weight; provenance belongs in the map).

---
title: A card carries no source-deixis such as "this chapter", "the source", or "as noted earlier"
rule_id: C-C1
applies_to_target: [kb-card]
check_kind: mechanical
severity_default: medium
---

# A card carries no source-deixis such as "this chapter", "the source", or "as noted earlier"

## Thesis
A card must contain no deictic reference to the material it was distilled from: never "this chapter", "the source", "as we saw", "as noted earlier", or "above". The card is read with no source document in context, so such pointers resolve to nothing.

## Rationale
A card is retrieved and read in isolation — the chapter, section, or surrounding text it came from is not present. A phrase like "as noted earlier" points at context the consumer does not have, leaving a dangling reference that the reader cannot resolve and that signals the card was lifted from a document rather than written to stand alone.

## Example
```
rejected: As the previous section showed, split long meetings.
accepted: Split any meeting longer than 90 minutes into two sessions.
```

## Limits
Bare "the author" used as a role inside the consumer's own domain — for instance, the author of a requirement under review — is not source-deixis and is fine. The check targets references to the distillation source and its internal structure, not every occurrence of words like "author" or "above".

## Validator
Grep the body for source-deictic phrases: "this chapter", "this section", "the source", "the text", "as (we|noted) (saw|earlier|above)", "as mentioned", "above". Flag each hit unless it is a domain-role use that does not point at the distillation source. Validator question: does this phrase point at context the isolated reader lacks?

## Patch output
When auditing a card containing source-deixis, emit one patch (`rule_id: C-C1`, location of the phrase, severity medium) rewriting the sentence to stand alone without the dangling reference. The presence of a deictic token is mechanically decidable, so no `needs_human` flag in the clear case.

## Source
KB card spec, self-containedness rules, group C (the card is read with no source in context).

---
title: An invariant keeps its number across revisions and a retired number is never given to another rule
rule_id: META-09
domain: meta
triggers: ['^\s*\d+[.]\s+\*\*', '(?i)supersed|retired|renumber']
scope: base-compare
check_kind: mechanical
severity_default: minor
---

# An invariant keeps its number across revisions and a retired number is never given to another rule

## Thesis
An invariant keeps the number it was first published under. A revision that inserts, reorders or retires invariants leaves every surviving rule on the number it held at the base; a retired invariant stays in the list under its number, marked `Superseded by Inv <M>`, `Deprecated` or `Retired`, and that number is never given to another rule; a new invariant takes the next unused number. A number that moves or changes hands silently redirects every finding, tolerance and cross-reference that cites it.

## Rationale
A finding, a tolerance note and a link between invariants (`Refines Inv 2`) all cite a rule by number, and the number is the only handle a reader carries from one revision of the config to the next. When a revision inserts a rule at 2 and shifts the cache rule to 3, every citation of `Inv 2` now names a different rule and nothing in the config says so; when a retired number is reused, two rules have shared one identifier across the config's history. A replaced decision record keeps its file `nnnn-title.md` and takes the status `superseded by ADR-0123`, so a reference by number keeps resolving; the identifier of each requirement should be unique. Keeping the retired line in place, marked, costs one line and keeps every citation meaningful across revisions.

## Example
```java
bad:  2. **Totals never go negative**: `Totals#transfer` rejects a negative balance.
         Violation: a negative balance written by `Totals#transfer`.
      3. **Cache loads stay cheap**: `Cache#load` allocates under 256 bytes per call.
         Violation: a larger allocation inside `Cache#load`.   (Inv 2 at the base)
good: 2. **Cache loads stay cheap**: `Cache#load` allocates under 256 bytes per call.
         Violation: a larger allocation inside `Cache#load`.
      3. **Totals never go negative**: `Totals#transfer` rejects a negative balance.
         Violation: a negative balance written by `Totals#transfer`.
```

## Limits
Applies to a number the base config already carried. A config with no invariant list at the base, and an invariant appended under the next unused number, draw no finding. An edit to an invariant's text under its own number — a tightened bound, a reworded clause, an added `Enforced by` or `Refines` — is a revision of the same rule, not a change of hands. A retired invariant kept in the list under its number and marked superseded, deprecated or retired is correct, and so is a successor that takes the next unused number.

## Validator
Open the config at HEAD and at the base. List the numbered invariants at the base as number, title and subject. For each base number, find at HEAD the rule with that title and subject: it sits under the same number, possibly with revised text; or it sits under another number; or it is gone while its number now carries a rule with another title or subject and no kept line marked `superseded`, `deprecated` or `retired`. Validator question: **has a rule that held a number at the base moved off that number, or has that number been given to another rule?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: META-09`, severity minor, `file` = the config path, `symbol` = `Inv <N>` for the number the rule held at the base, `code` = the invariant line now under that number, or the moved rule's line, quoted verbatim from the diff, `fix` = the base rule kept under its number — marked superseded where it is retired — and the new rule under the next unused number, `rationale` naming the citations by number that the move silently redirects).

## Source
MADR `template/adr-template.md` (`adr/madr`, `main`) — frontmatter `status: "{proposed | rejected | accepted | deprecated | … | superseded by ADR-0123}"`: a replaced record keeps its file `nnnn-title.md` and takes the status `superseded by ADR-0123`, so a reference by number keeps resolving; `README.md` — "For each ADR, copy the template to `nnnn-title.md`". arXiv:2103.02255 §4.1 — "id: The identifier of the requirement … The id of each requirement should be unique". Neither source says a record or requirement is never renumbered; the card infers it from a superseded record keeping its number and from an id that stays unique.

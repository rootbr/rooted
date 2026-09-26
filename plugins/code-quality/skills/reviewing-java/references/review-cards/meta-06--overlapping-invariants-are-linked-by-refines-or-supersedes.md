---
title: Two invariants over one subject are linked by refines or supersedes, never left as two independent rules
rule_id: META-06
domain: meta
triggers: ['^\s*\d+[.]\s+\*\*', '[Ii]nvariant', '(?i)refines|supersede|replaces|deprecated', '\bmust\b|\bnever\b']
scope: file
check_kind: semantic
severity_default: minor
---

# Two invariants over one subject are linked by refines or supersedes, never left as two independent rules

## Thesis
When an invariant narrows, restates or replaces another — the same subject, and a forbidden state that is a subset, superset or rewording of the other's — its text names the other by number (`Refines Inv 2`, `Supersedes Inv 5`), and a replaced invariant is marked superseded rather than deleted or left standing as a live rule. Two unlinked invariants over one territory are one finding on the later one.

## Rationale
A duplicated requirement is the same rule described in different words, and duplication produces inconsistency the moment one copy is changed and the other is not: the reviewer then holds two rules over the same change, one of which the author has already moved past. Two live rules over one span also produce two findings with two suggested fixes for one line, and no way to tell which the project means. A decision record keeps its number when it is replaced and records the successor in its status — `superseded by ADR-0123` — so a reference to the old number still resolves and the reader is sent to the rule that now holds. The same link between invariants tells a reviewer which rule to enforce, and lets a finding on the general rule be dropped when the diff complies with the specific one.

## Example
```java
bad:  2. **No blocking I/O on the hot path**: No method on the hot path performs
         blocking I/O. Violation: a blocking call on the hot path.
      6. **tick never calls Socket#read**: `RequestLoop#tick` calls no `Socket#read`.
         Violation: `Socket#read` inside `RequestLoop#tick`.
good: 6. **tick never calls Socket#read**: Refines Inv 2 for `RequestLoop#tick`:
         it calls no `Socket#read`, `Socket#write` or `InputStream#read` without
         a timeout. Violation: any of those calls inside `RequestLoop#tick`.
```

## Limits
Applies to two invariants whose subjects intersect and whose forbidden states overlap. Two invariants on one class with disjoint forbidden states — one on allocation, one on locking — are separate rules and need no link. A link in either direction (`Refines Inv 2` on the specific rule, or `Refined by Inv 6` on the general one) satisfies the card.

## Validator
Open the config at HEAD and take each numbered invariant the diff adds or changes. For each, read every other invariant whose subject — class, method, package or resource — intersects its own, and compare forbidden states: a rewording, a subset or a superset means overlap. Check both invariants' text for a link by number — `refines`, `refined by`, `supersedes`, `superseded by`, `replaces`. Validator question: **does this invariant overlap another on the same subject with no link by number between the two?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: META-06`, severity minor, `file` = the config path, `symbol` = `Inv <N>` for the added invariant's number, `code` = the two invariant lines quoted verbatim, the added one from the diff, `fix` = the added invariant rewritten with the `Refines Inv N` or `Supersedes Inv N` clause and, for a replacement, the older line marked superseded, `rationale` naming the two findings one change would draw and the copy that drifts).

## Source
MADR `template/adr-template.md` (`adr/madr`, `main`) — frontmatter `status: "{proposed | rejected | accepted | deprecated | … | superseded by ADR-0123}"`: a replaced record keeps its number and points at its successor. arXiv:2103.02255 §2.1 — "the duplication of two requirements may cause inconsistency when one requirement is changed while another not". arXiv:2412.01657 §1 — duplicate requirements, "where the same functionality is described differently", "lead to unintentional redundancy in implementation efforts".

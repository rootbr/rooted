---
title: A change that accepts a decision record also updates the architecture documentation in the repository that describes what the decision changes
rule_id: ARCH-43
domain: architecture
step: [document, review]
applies_to: [prose]
triggers: ['(?i)\bstatus[*_]{0,2}\s*:\s*[*_\x22`]*\s*accepted\b|^\s*accepted\s*$', 'signal:added_file']
scope: callers
check_kind: semantic
severity_default: minor
---

# A change that accepts a decision record also updates the architecture documentation in the repository that describes what the decision changes

## Thesis
When a change adds a decision record in the accepted state or with no status line, or moves an existing record to accepted, and the repository holds architecture documentation — an architecture overview, an arc42 or C4 document, a component-diagram source, a team manual — that describes a component, dependency or technology the decision adds, removes or replaces, or a component an added one attaches to, the change that accepts the record updates those passages to the decision.

## Rationale
A decision record is not a complete description of the system or its architecture. An accepted record is, in general, no longer substantially modified: it is a historical document rather than a living specification, and formal documentation of the decided behaviour is to be maintained elsewhere. Where a team documents its architecture in such living documents, those documents are to be updated whenever a new record is accepted, so that they, rather than the record, carry the current architecture. A decision affects elements of the architecture description, so the passages describing those elements are the ones the update reaches.

## Example
```go
bad:  // docs/decisions/0007-orders-in-sqlite.md -- Status: Accepted
      // docs/architecture/model.go, the component-diagram source:
      var storage = Container("storage", "keeps orders", "PostgreSQL")
good: // docs/decisions/0007-orders-in-sqlite.md -- Status: Accepted
      // docs/architecture/model.go, the component-diagram source:
      var storage = Container("storage", "keeps orders", "SQLite")
```

## Limits
The rule starts at acceptance: a record added as proposed owes no update until the change that accepts it, and a record that carries no status line counts as accepted in the change that adds it to the main line. Documentation kept outside the repository, such as a wiki or another collaboration tool, falls under the same expectation but lies beyond what a diff shows, and the rule does not reach it. A repository that holds no architecture documentation, or whose documentation names none of the elements the decision affects, owes no update. Stale mentions of a deleted element in documentation other than the architecture description, and documentation of user-facing behaviour, lie outside this rule.

## Validator
Grep the hunk for a decision record entering the accepted state: an added file under a decisions or records directory whose status line is accepted or absent, or an existing record whose status line changes to accepted. Read the record's decision and consequences and list the components, dependencies and technologies it adds, removes or replaces, and the components each added one attaches to. Open the repository's architecture documentation — an architecture overview, an arc42 or C4 document, a component-diagram source, a team manual — and search it for each listed element and for the element it replaces. Check whether the same change edits each passage that describes one of those elements. Validator question: **Does the change accept a decision record while architecture documentation in the repository still describes an element the decision removes or replaces, or a component an added element attaches to, as it stood before the decision?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: ARCH-43`, severity minor, `file` = the architecture documentation file, `symbol` = the section or heading of the stale passage, `code` = the record's status or decision line and the stale passage, quoted verbatim, `fix` = the passage rewritten to the decided state in the documentation's own format, `rationale` = an accepted record is a historical document while the architecture documentation is the living description, and it now contradicts the accepted decision).

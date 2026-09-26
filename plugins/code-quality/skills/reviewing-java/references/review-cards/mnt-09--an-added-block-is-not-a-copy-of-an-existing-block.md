---
title: A block of statements added in the diff is not a copy of an existing block that differs only in names or literals
rule_id: MNT-09
domain: maintainability
triggers: []
scope: file
check_kind: semantic
severity_default: minor
---

# A block of statements added in the diff is not a copy of an existing block that differs only in names or literals

## Thesis
A sequence of statements the diff adds — a method body, a loop, a `try` block, a mapping — is not a clone of a sequence already present in the same file or elsewhere in the diff, identical except for identifier names or literal values; the shared logic is one method, parameterized by what differs.

## Rationale
Two copies of one logic are two places every fix and every rule change must reach, and nothing but memory links them: a study of inconsistent changes to clones in industrial and open-source systems found such changes frequent and a significant share of the unintentional ones to be faults. The copy also doubles the code a reader must compare to learn that the two are the same. A clone detector reports token-level duplicates after the fact; a reviewer sees the copy in the diff itself when the added block mirrors one in the file.

## Example
```java
bad:  BigDecimal shipTotal(Order o) { BigDecimal t = ZERO; for (Line l : o.lines()) { if (l.ships()) t = t.add(l.amount()); } return t; }
      BigDecimal taxTotal(Order o)  { BigDecimal t = ZERO; for (Line l : o.lines()) { if (l.taxed()) t = t.add(l.amount()); } return t; }
good: BigDecimal total(Order o, Predicate<Line> which) {
          return o.lines().stream().filter(which).map(Line::amount).reduce(ZERO, BigDecimal::add);
      }
```

## Limits
Structural repetition that is not logic — a builder call per field, a table of constants, test cases that differ in data — is not a clone. Two blocks that will evolve separately by design, named in the project context, are tolerated. A copy across files that the diff does not show is out of reach at file scope.

## Validator
For each added block of three or more statements, open the file and look for a block with the same statement sequence and structure, differing only in identifiers or literals; also compare added blocks with each other. Validator question: **does this added block repeat an existing block's statements with only names or literals changed?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: MNT-09`, severity minor, `file`, `symbol`, `code` = the added block and the first line of its twin quoted verbatim from the diff, `fix` = the one method with the difference as a parameter, `rationale` naming the two places a change must now reach).

## Source
Juergens, Deissenboeck, Hummel, Wagner, "Do Code Clones Matter?", ICSE 2009, DOI 10.1109/ICSE.2009.5070547 — inconsistent changes to clones are frequent and a significant fraction of the unintentional ones are faults. PMD CPD documentation — the copy-paste detector reports duplicates at or above a token count (`--minimum-tokens`), the mechanical form of this check.

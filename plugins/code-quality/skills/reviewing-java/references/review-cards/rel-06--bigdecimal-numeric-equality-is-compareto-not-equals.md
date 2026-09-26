---
title: Numeric equality of two BigDecimal values is tested with compareTo, because equals also compares scale
rule_id: REL-06
domain: reliability
triggers: ['BigDecimal', '[.]equals\(', 'assertEquals\(', 'Set<BigDecimal>', 'Map<BigDecimal']
scope: hunk
check_kind: mechanical
severity_default: major
---

# Numeric equality of two BigDecimal values is tested with compareTo, because equals also compares scale

## Thesis
Code that asks whether two `BigDecimal` values are the same number writes `a.compareTo(b) == 0` (or `signum` of the difference), not `a.equals(b)`, and does not use `BigDecimal` as a `HashSet` element or `HashMap` key unless every value is normalized to one scale.

## Rationale
`BigDecimal.equals` returns true only when value and scale both match: `new BigDecimal("1.0").equals(new BigDecimal("1.00"))` is false, and `hashCode` follows `equals`, so a set of prices can hold both and `contains` misses a value that is numerically present. Values arrive with different scales from different sources — a literal, a database column, a division, `setScale` — so an equality check that compiles and passes a unit test with same-scale inputs fails in production with inputs of another scale. `compareTo` orders by numeric value alone and is the class's own recommendation for numerical equality; its natural ordering is documented as inconsistent with `equals`.

## Example
```java
bad:  if (paid.equals(due)) markSettled();
      Set<BigDecimal> seen = new HashSet<>(); seen.add(price);
good: if (paid.compareTo(due) == 0) markSettled();
      Set<BigDecimal> seen = new TreeSet<>(); seen.add(price);
```

## Limits
An `equals` that deliberately distinguishes `1.0` from `1.00` — a formatter, a test of scale handling — is correct with a comment saying so. Values normalized with `stripTrailingZeros()` or `setScale(n)` on both sides before the comparison are equal under `equals` when numerically equal, and a hash collection of such normalized values is not flagged. A `TreeSet` or `TreeMap` uses `compareTo` and is the correct form.

## Validator
On the triggered hunk find each `equals` call, `assertEquals` argument pair, `HashSet`/`HashMap`/`Set.of`/`Map.of` element or key whose static type is `BigDecimal`. Check whether both operands are normalized to one scale in the same method. Validator question: **does this comparison or hash lookup treat two `BigDecimal` values of the same number and different scale as unequal?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: REL-06`, severity major, `file`, `symbol`, `code` = the comparison or collection use quoted verbatim from the diff, `fix` = `compareTo(...) == 0` or a normalized scale before the hash collection, `rationale` naming the scale-sensitive `equals`).

## Source
`java.math.BigDecimal#equals(Object)` Javadoc, Java SE 21 — returns true "if and only if the specified Object is a BigDecimal whose value and scale are equal to this BigDecimal's"; `#compareTo(BigDecimal)` — "Note: this class has a natural ordering that is inconsistent with equals"; comparing its result to 0 "is analogous to checking the numerical equality of double values". Error Prone `BigDecimalEquals` — `new BigDecimal("1.0").equals(new BigDecimal("1.00"))` is false.

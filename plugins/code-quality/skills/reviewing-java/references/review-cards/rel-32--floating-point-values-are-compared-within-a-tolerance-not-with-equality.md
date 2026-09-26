---
title: Two computed floating-point values are compared within a tolerance, never with == or equals
rule_id: REL-32
domain: reliability
triggers: ['(?i)[!=]=\s*\w*(total|sum|amount|ratio|rate|avg|mean|score|weight|balance)\w*', '(Double|Float)[.]equals\(', '[.]equals\(\s*\d+[.]\d', 'assertEquals\(', '==\s*\d+[.]\d', 'Double[.]compare\(']
scope: hunk
check_kind: mechanical
severity_default: minor
---

# Two computed floating-point values are compared within a tolerance, never with == or equals

## Thesis
When at least one operand of an equality test is a `double` or `float` that came out of arithmetic — a sum, a product, a division, a parsed decimal — the test is `Math.abs(a - b) < epsilon` with an epsilon suited to the magnitude, not `a == b`, `a.equals(b)`, `Double.compare(a, b) == 0`, or an `assertEquals` without a delta.

## Rationale
Floating-point arithmetic rounds at every operation, so two computations of the same mathematical quantity by different routes — `0.1 + 0.2` and `0.3`, a total summed in two orders — differ in the last bits. An exact comparison then reports them unequal, and code that branches on equality takes the wrong path for inputs a test never used. Comparison "within some range" is the form the analysers recommend; a value that must be exact belongs in `BigDecimal` rather than in a tighter epsilon.

## Example
```java
bad:  if (computedTotal == expectedTotal) markBalanced();
      assertEquals(0.3, 0.1 + 0.2);
good: if (Math.abs(computedTotal - expectedTotal) < 1e-9) markBalanced();
      assertEquals(0.3, 0.1 + 0.2, 1e-9);
```

## Limits
A comparison against a sentinel the code itself assigned — `x == 0.0` after `x = 0.0`, `Double.isNaN`, a check for `Double.MAX_VALUE` — is exact by construction and is not flagged. Comparing two values that were both assigned the same literal is not flagged. Equality on integers stored in a `double` within 2^53 is exact.

## Validator
On the triggered hunk find each `==`, `!=`, `equals`, `Double.compare(...) == 0` or delta-less `assertEquals` whose operands are `double` or `float`, and read where the operands come from: a literal or sentinel, or arithmetic and parsing. Validator question: **is a floating-point value produced by arithmetic tested for exact equality?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: REL-32`, severity minor, `file`, `symbol`, `code` = the comparison quoted verbatim from the diff, `fix` = `Math.abs(a - b) < epsilon` or an `assertEquals` with a delta, `rationale` naming the rounding that makes exact equality fail).

## Source
SpotBugs `FE_FLOATING_POINT_EQUALITY` — "This operation compares two floating point values for equality. Because floating point calculations may involve rounding, calculated float and double values may not be accurate ... For values that need not be precise, consider comparing for equality within some range, for example: if ( Math.abs(x - y) < .0000001 ). See the Java Language Specification, section 4.2.4". JLS §4.2.4 "Floating-Point Operations" (unfetched; cited as the analyser anchors it).

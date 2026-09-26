---
title: A BigDecimal division names a scale and RoundingMode or a MathContext, so a non-terminating quotient cannot throw
rule_id: REL-31
domain: reliability
triggers: ['[.]divide\(', 'BigDecimal', 'RoundingMode']
scope: hunk
check_kind: mechanical
severity_default: major
---

# A BigDecimal division names a scale and RoundingMode or a MathContext, so a non-terminating quotient cannot throw

## Thesis
`BigDecimal.divide` is called with a scale and a `RoundingMode`, or with a `MathContext`, whenever the divisor is not a constant whose quotient is known to terminate; the one-argument `divide(BigDecimal)` is used only where the exact quotient is provably representable.

## Rationale
The one-argument `divide` returns the exact quotient, and "if the exact quotient cannot be represented (because it has a non-terminating decimal expansion) an ArithmeticException is thrown". Whether the expansion terminates depends on the runtime values: `10 / 4` succeeds and `10 / 3` throws, so code that divides an amount by a count, a rate or a user-supplied number passes every test with friendly values and fails in production on the first divisor with a factor other than 2 or 5. Naming the scale and rounding mode makes the result defined for every divisor and states the rounding the business rule wants.

## Example
```java
bad:  BigDecimal share = total.divide(BigDecimal.valueOf(participants));
good: BigDecimal share = total.divide(BigDecimal.valueOf(participants), 2, RoundingMode.HALF_EVEN);
```

## Limits
A division by a constant power of ten or two (`divide(BigDecimal.valueOf(100))`) terminates for every dividend and is not flagged. A division whose thrown `ArithmeticException` is deliberately caught to detect a non-terminating case is correct with a comment saying so.

## Validator
On the triggered hunk find each `divide(` on a `BigDecimal` and count its arguments. Flag the one-argument form unless the divisor is a literal constant whose quotient terminates for every dividend. Validator question: **can this one-argument division receive a divisor that makes the quotient non-terminating?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: REL-31`, severity major, `file`, `symbol`, `code` = the division quoted verbatim from the diff, `fix` = `divide(divisor, scale, RoundingMode.X)` or `divide(divisor, mathContext)`, `rationale` naming the `ArithmeticException` on a non-terminating quotient).

## Source
`java.math.BigDecimal#divide(BigDecimal)` Javadoc, Java SE 21 — "Returns a BigDecimal whose value is (this / divisor), and whose preferred scale is (this.scale() - divisor.scale()); if the exact quotient cannot be represented (because it has a non-terminating decimal expansion) an ArithmeticException is thrown"; `#divide(BigDecimal, int, RoundingMode)` and `#divide(BigDecimal, MathContext)` — the rounded forms.

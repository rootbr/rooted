---
title: A BigDecimal is constructed from a String or BigDecimal.valueOf, never from a double literal or variable
rule_id: REL-05
domain: reliability
triggers: ['new BigDecimal\(', 'BigDecimal[.]valueOf\(', 'BigDecimal']
scope: hunk
check_kind: mechanical
severity_default: major
---

# A BigDecimal is constructed from a String or BigDecimal.valueOf, never from a double literal or variable

## Thesis
A `BigDecimal` that must hold a decimal value exactly is created with `new BigDecimal("0.1")`, `BigDecimal.valueOf(0.1)` or from an integer, never with `new BigDecimal(0.1)` or `new BigDecimal(someDouble)`.

## Rationale
`new BigDecimal(double)` translates the binary floating-point value exactly, and most decimal fractions have no exact binary representation: `new BigDecimal(0.1)` equals 0.1000000000000000055511151231257827021181583404541015625, because the `double` passed in is already not 0.1. The error is then carried with full precision through every later operation, so two amounts that should be equal are not, sums are off by tiny fractions, and rounding at a scale of two hides the difference until a reconciliation fails. The `String` constructor and `BigDecimal.valueOf(double)`, which goes through `Double.toString`, produce the decimal the source text shows.

## Example
```java
bad:  BigDecimal rate = new BigDecimal(0.1);
      BigDecimal price = new BigDecimal(request.amount());   // amount() is a double
good: BigDecimal rate = new BigDecimal("0.1");
      BigDecimal price = BigDecimal.valueOf(request.amount());
```

## Limits
Applies where the decimal value is what the code means: money, rates, quantities, percentages. A deliberate conversion that wants the exact binary value of a `double` — a numeric-analysis routine that documents it — is correct with the `double` constructor and a comment saying so. An argument of type `int` or `long` is exact and is not flagged.

## Validator
On the triggered hunk find each `new BigDecimal(` and check the static type of its argument. Flag when the argument is a `double` or `float` literal, variable, field, method result or arithmetic expression. Validator question: **is a `double` or `float` value passed to the `BigDecimal` constructor?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: REL-05`, severity major, `file`, `symbol`, `code` = the constructor call quoted verbatim from the diff, `fix` = `new BigDecimal("...")` for a literal or `BigDecimal.valueOf(x)` for a variable, `rationale` naming the inexact binary value that the constructor preserves).

## Source
`java.math.BigDecimal#BigDecimal(double)` Javadoc, Java SE 21 — "The results of this constructor can be somewhat unpredictable. One might assume that writing new BigDecimal(0.1) in Java creates a BigDecimal which is exactly equal to 0.1 ... but it is actually equal to 0.1000000000000000055511151231257827021181583404541015625. This is because 0.1 cannot be represented exactly as a double"; the `String` constructor "is perfectly predictable". SpotBugs `DMI_BIGDECIMAL_CONSTRUCTED_FROM_DOUBLE` — "You probably want to use the BigDecimal.valueOf(double d) method". SEI CERT Oracle Coding Standard for Java, NUM10-J "Do not construct BigDecimal objects from floating-point literals". Caveat: the SpotBugs detector flags only a `double` "that doesn't translate well to a decimal number" and passes an exactly representable one such as `new BigDecimal(0.5)`; the rule here flags every `double` or `float` argument, resting on the constructor Javadoc and NUM10-J.

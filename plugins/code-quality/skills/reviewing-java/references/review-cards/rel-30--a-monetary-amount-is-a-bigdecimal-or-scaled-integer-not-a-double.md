---
title: A monetary or otherwise exact decimal amount is held in BigDecimal or a scaled integer, never in double or float
rule_id: REL-30
domain: reliability
triggers: ['(?i)\b(double|float)\b[\s\[\]]*\w*(price|amount|total|balance|cost|fee|rate|tax|sum|money)', 'BigDecimal', '[.]doubleValue\(\)', 'Math[.]round\(']
scope: hunk
check_kind: mechanical
severity_default: major
---

# A monetary or otherwise exact decimal amount is held in BigDecimal or a scaled integer, never in double or float

## Thesis
A value that must be exact in decimal — money, a tax rate, a quantity billed, a percentage applied to money — is declared as `BigDecimal` (or as a `long` in the smallest unit, such as cents) in fields, parameters, DTOs and arithmetic; it is not computed or stored as `double` or `float`, and a `BigDecimal` is not converted with `doubleValue()` for arithmetic.

## Rationale
A binary floating-point type cannot represent most decimal fractions: 0.1 as a `double` is 0.1000000000000000055511151231257827021181583404541015625, and every sum, product and rounding of such values carries the error forward. Totals that should match differ in the last bits, `Math.round` lands on the wrong cent for values that sit on a half, and a comparison that should be equal is not, so a reconciliation or an invoice is off by amounts nobody can explain from the code. `BigDecimal` holds the decimal exactly and applies the rounding the code names; a scaled integer does the same for a fixed scale.

## Example
```java
bad:  double total = 0; for (Line l : lines) total += l.price() * l.qty();
      double tax = total * 0.19;
good: BigDecimal total = lines.stream().map(l -> l.price().multiply(BigDecimal.valueOf(l.qty())))
          .reduce(BigDecimal.ZERO, BigDecimal::add);
      BigDecimal tax = total.multiply(new BigDecimal("0.19")).setScale(2, RoundingMode.HALF_EVEN);
```

## Limits
Applies to amounts that must reconcile exactly. Measurements, statistics, physics, coordinates, ratios for display and scores are correctly `double`. A `double` used only to render a rounded display value from an exact source is out of scope. A project context naming a fixed-point `long` convention (minor units) satisfies the rule.

## Validator
On the triggered hunk find each `double`/`float`/`Double` field, parameter, local or DTO property whose name or use denotes money or an exact decimal quantity, each arithmetic on such values, and each `doubleValue()` on a `BigDecimal` feeding arithmetic. Validator question: **is an amount that must be exact in decimal computed or stored in binary floating point?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: REL-30`, severity major, `file`, `symbol`, `code` = the declaration or arithmetic quoted verbatim from the diff, `fix` = the same value as `BigDecimal` with an explicit `RoundingMode`, or a `long` in minor units, `rationale` naming the representation error).

## Source
`java.math.BigDecimal#BigDecimal(double)` Javadoc, Java SE 21 — "0.1 cannot be represented exactly as a double (or, for that matter, as a binary fraction of any finite length)". SpotBugs `FE_FLOATING_POINT_EQUALITY` — "Because floating point calculations may involve rounding, calculated float and double values may not be accurate. For values that must be precise, such as monetary values, consider using a fixed-precision type such as BigDecimal". SEI CERT Oracle Coding Standard for Java, NUM04-J "Do not use floating-point numbers if precise computation is required" (unfetched; cited as its provenance line anchors it).

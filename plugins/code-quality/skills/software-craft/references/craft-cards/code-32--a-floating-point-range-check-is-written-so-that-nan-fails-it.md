---
title: A range check on a floating-point value is written so that NaN fails it, by accepting only values shown to lie inside the range
rule_id: CODE-32
domain: code
step: [implement, handle-errors]
applies_to: [universal]
triggers: ['[<>]=?\s*[-\w.()\[\]]+\s*(\|\||\bor\b)\s*(\\?\s*$|[-\w.()\[\]]+\s*[<>])|^\s*(\|\||or\b)\s*[-\w.()\[\]]+\s*[<>]']
scope: hunk
check_kind: mechanical
severity_default: minor
---

# A range check on a floating-point value is written so that NaN fails it, by accepting only values shown to lie inside the range

## Thesis
A check that keeps a floating-point value within a range bounded below and above lets the value through only when its comparisons show it inside the range: at or above the lower bound and at or below the upper bound, with a strict comparison for a bound the range excludes. Every ordered comparison with NaN is false, so this accepting form rejects NaN. A check written instead as a test for lying outside the range, below the lower bound or above the upper bound, follows the rule only when a NaN test or a finiteness test on the same value has rejected NaN on every path to it.

## Rationale
An ordered comparison (`<`, `<=`, `>`, `>=`) with NaN on either side is false: NaN is neither less than, nor greater than, nor equal to any value, itself included, so the trichotomy of comparison does not hold. This behaviour complies with IEEE 754, and the comparison operators on binary floating-point types share it across mainstream languages. A guard that rejects the value when it is below the lower bound or above the upper bound therefore evaluates to false for NaN, skips its rejection, and lets NaN continue as though it lay inside the range. A guard that rejects unless the value is at or above the lower bound and at or below the upper bound finds its in-range test false for NaN and rejects it. For every value but NaN the two forms decide alike, since only a NaN operand leaves a comparison unordered, so rewriting one form into the other changes control flow for NaN alone; operator-based comparisons make it easy to forget that a floating-point comparison has a fourth outcome, unordered, besides less, equal and greater. NaN reaches a check from arithmetic, such as the square root of a negative number where that operation returns NaN rather than raising an error, and from conversions that return NaN for text that is not a numeric literal. Past the check it is infectious: almost all calculations with a NaN operand yield NaN, so it spreads into the values computed from it. The accepting form lets through only a value whose comparisons place it inside the range; a NaN or finiteness test ahead of an out-of-range test, or a three-way comparison that handles the unordered outcome itself, reaches the same result.

## Example
```rust
bad:  if ratio < 0.0 || ratio > 1.0 {
          return Err(format!("not a ratio: {ratio}"));
      }
good: if !(0.0..=1.0).contains(&ratio) {
          return Err(format!("not a ratio: {ratio}"));
      }
```

## Limits
The rule reaches values of binary floating-point types, whose ordered comparisons with NaN are false; a check on integer values, or on a decimal type, is outside it. Where a NaN test or a finiteness test on the same value runs on every path to the check, the out-of-range form decides as the accepting form does and follows the rule. Data that uses NaN as its marker for a missing value, with later steps that skip or handle missing values, may let NaN past a range check on purpose; a comment, a test or the project's documented data convention saying so rejects the finding. The card reaches checks against both a lower and an upper bound and covers only how their comparisons treat NaN; whether a check is needed, which bounds it uses and what the code does when it fails are judged by their own rules.

## Validator
Grep the added lines for two ordered comparisons joined by a logical or, on one line or split across a line break (`x < low || x > high`, `x > high or x < low`, `x < low || high < x`). For each hit, decide whether the compared value is floating-point: the hunk declares or converts it as a floating-point type, compares it with a literal that has a fractional part, the value has the language's default number type and that type is binary floating point, or it is a parameter with no declared type whose name or bounds mark a fractional quantity such as a probability, a ratio or a measurement; a value of an integer type or of a decimal type is outside the card. Read what the condition guards: a rejection (a raise, a returned error, a skip, a filter that drops the value, a fallback value) or, when the whole condition is negated, an acceptance. Take every ordered comparison that has the value as an operand as false, evaluate the condition, and read which path NaN takes. Look in the hunk for a NaN test or a finiteness test on the same value earlier on the path or earlier in the same condition (`is_nan`, `isNaN`, `isnan`, `IsNaN`, `x != x`, `is_finite`, `isFinite`, `isfinite`), and for a comment or test that lets NaN through on purpose as a missing value. Validator question: **With every ordered comparison on the value taken as false, does an added range check on a floating-point value send NaN down the path meant for values inside the range, with no NaN or finiteness test before it and no stated intent to let NaN through?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: CODE-32`, severity minor, `file`, `symbol`, `code` = the added range-check condition quoted verbatim from the diff, `fix` = the condition rewritten to accept only values inside the range (the in-range test negated, or a range-containment call) or preceded by a NaN test on the value, in the file's language, `rationale` = naming the floating-point value, the comparisons that are all false for NaN, and the path NaN takes past the check).

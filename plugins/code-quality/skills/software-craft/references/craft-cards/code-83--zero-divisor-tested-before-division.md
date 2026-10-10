---
title: A division or remainder whose divisor can be zero at run time, in arithmetic where a zero divisor raises, panics or is undefined, is reached only after a test that the divisor is not zero or is done with a checked division
rule_id: CODE-83
domain: code
step: [implement, handle-errors]
applies_to: [universal]
triggers: ['[\w)\]]\s*(?:/|//|%)=?\s*\(?\s*(?:len\(|[\w.]+[.](?:length|size|count|len)\b|[\w.]*(?:[cC]ount|[sS]ize|[lL]en(?:gth)?|[tT]otal|[dD]enom\w*|[dD]ivisor)\b)|[.](?:div|rem|divide|remainder|div_euclid|rem_euclid|Quo|Rem|Div|Mod)\(|\bMath[.](?:floorDiv|floorMod)\(|\bdivmod\(', '(?<![/*:])\b\w+\)?\s+(?:/|//|%)=?\s+(?!\d)[A-Za-z_(]']
scope: file
check_kind: semantic
severity_default: major
---

# A division or remainder whose divisor can be zero at run time, in arithmetic where a zero divisor raises, panics or is undefined, is reached only after a test that the divisor is not zero or is done with a checked division

## Thesis
A division or remainder whose divisor can be zero at run time, in arithmetic where a zero divisor raises an exception, panics or has an undefined result, runs only after the code has tested the divisor against zero and handled the zero case, or is written as a checked division that returns an absent value for a zero divisor. The test may be a precondition at the routine's entry that rejects a zero divisor. A divisor can be zero at run time when it is not a non-zero constant, its type admits zero, and nothing on the path to the division shows it to be non-zero: for example a parameter, a value from input, or the length of a collection that can be empty.

## Rationale
In most languages, integer division and remainder by zero raise an exception, panic at run time, or have an undefined result; in some languages floating-point division by zero raises as well. The outcome can be abnormal program termination and denial of service. A compiler may reject a divisor that is a constant zero, but a divisor that is zero only at run time fails when the division executes. A zero test placed after the division comes too late: either the comparison is useless or there is division by zero. Testing the divisor first, or dividing through a checked operation that returns an absent value for a zero divisor, turns the failure into a case the code handles. Guidelines direct checkers to flag a division by an integral value that could be zero, checkers flag a divisor from input that they cannot prove non-zero, and the defect is catalogued as CWE-369.

## Example
```python
bad:  def mean(values):
          return sum(values) / len(values)
good: def mean(values):
          if len(values) == 0:
              raise ValueError("mean of no values")
          return sum(values) / len(values)
```

## Limits
Binary floating-point division whose result the language or its implementation defines by IEEE 754, so that a zero divisor yields an infinity or NaN and does not fail, is outside the rule; that infinity or NaN, and an integer converted from it, are judged by their own rules. Floating-point division that raises on a zero divisor is inside. A divisor that is a non-zero constant, or whose type excludes zero, is outside. Where a zero divisor raises or panics, a handler around the division that catches that failure and handles it also meets the rule. Arithmetic that defines integer division by zero to return zero does not fail and is outside; there a zero flows silently into the result, and that arithmetic's own guidance points to its partial or checked division to avoid it. Where the divisor is an argument of a routine callable from outside its module and the routine checks no precondition on it, the missing entry check is judged by its own rule as well.

## Validator
Grep the hunk for added `/`, `//` and `%` operators, their compound assignments, and division or remainder calls (`div`, `rem`, `divmod`, floor-division helpers) whose divisor is not a non-zero numeric literal; skip an operator that is not arithmetic, such as string formatting, path joining, a comment or a regular expression. Open the file and find the divisor's type and where its value comes from. Set aside binary floating-point division in arithmetic that yields an infinity or NaN for a zero divisor, a divisor whose type excludes zero, and a non-zero constant divisor. Trace every path from the routine's entry to the division: a test against zero that branches away from the division, a precondition that rejects zero, an emptiness check on the collection whose length is the divisor, a checked division, or a handler that catches the zero-division failure each clears that path; a zero test that comes after the division clears nothing. Validator question: **Does an added division or remainder take a divisor that can be zero at run time, in arithmetic where a zero divisor raises, panics or is undefined, with no zero test, precondition, checked division or zero-division handler before it on some path?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: CODE-83`, severity major, `file`, `symbol`, `code` = the division or remainder expression with its divisor, quoted verbatim from the diff, `fix` = the zero test and its handling placed before the division, or the checked division, in the file's language, `rationale` = the divisor, why it can be zero at run time, and what the division then does).

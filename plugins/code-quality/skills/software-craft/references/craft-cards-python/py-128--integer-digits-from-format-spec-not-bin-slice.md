---
title: An integer's binary, octal or hex digits without the prefix come from the b, o or x format spec, not from cutting the first two characters off bin, oct or hex output, which mangles a negative number
rule_id: PY-128
domain: code
step: [implement, review]
applies_to: [python]
triggers: ['\b(?:bin|oct|hex)\(.+?\)\[\s*2\s*:\s*\]', '\b(?:bin|oct|hex)\(.+?\)\[\s*2\s*:']
scope: hunk
check_kind: mechanical
severity_default: minor
---

# An integer's binary, octal or hex digits without the prefix come from the b, o or x format spec, not from cutting the first two characters off bin, oct or hex output, which mangles a negative number

## Thesis
Code that wants an integer's binary, octal or hexadecimal digits without the `0b`, `0o` or `0x` prefix formats the integer with the `b`, `o` or `x` presentation type and no `#` option, as in `f"{n:b}"` or `format(n, "b")`, rather than slicing `bin(n)[2:]`, `oct(n)[2:]` or `hex(n)[2:]`.

## Rationale
`bin`, `oct` and `hex` return the integer's digits prefixed with `0b`, `0o` or `0x`, and a negative integer's minus sign comes before that prefix: `bin(-10)` is `'-0b1010'`, `oct(-56)` is `'-0o70'` and `hex(-42)` is `'-0x2a'`. A fixed `[2:]` slice therefore cuts the sign and the `0` from a negative result, so `bin(-10)[2:]` is `'b1010'`, which keeps the prefix letter and loses the sign. The `b`, `o` and `x` presentation types output the number in base 2, 8 or 16, the prefix appears only with the `#` option (`format(14, '#b')` is `'0b1110'`, `format(14, 'b')` is `'1110'`), and the default sign option uses a sign only for negative numbers, so `f"{-10:b}"` is `'-1010'`. For a non-negative integer both spellings give the same digits, and the f-string is the more concise and readable one.

## Example
```python
bad:  bits = bin(delta)[2:]  # 'b1010' when delta is -10
good: bits = f"{delta:b}"  # '-1010' when delta is -10
```

## Limits
Where the value cannot be negative, the slice gives the right digits and the finding is one of readability only. Where the prefix is wanted, the `#` option keeps it in the same spelling, as in `f"{n:#x}"`, which gives `'0xff'` for 255, and the `X` type gives upper-case hex digits.

## Validator
Grep the hunk for a `bin(`, `oct(` or `hex(` call followed by a `[2:]` slice. Trace the argument to where its value comes from and check whether any path can make it negative: a difference, an offset, a signed field decoded from input, a parameter with no non-negative guard. Validator question: **Does the hunk take an integer's digits by slicing the first two characters off `bin`, `oct` or `hex` output where the `b`, `o` or `x` format spec gives them?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-128`, severity minor, `file`, `symbol`, `code` = the `bin(...)[2:]`, `oct(...)[2:]` or `hex(...)[2:]` expression, `fix` = the same value as `f"{value:b}"`, `f"{value:o}"` or `f"{value:x}"`, `rationale` = whether a negative value can reach the slice, where it yields the prefix letter without the sign, or readability alone when it cannot).

---
title: A Python base-2 or base-10 logarithm calls math.log2(x) or math.log10(x), not math.log(x, 2) or math.log(x, 10), which is usually less accurate
rule_id: PY-158
domain: code
step: [implement]
applies_to: [python]
triggers: ['\bmath[.]log\s*\([^#]*,\s*(2|10)([.]0)?\s*\)', '(?<![\w.])log\s*\([^#]*,\s*(2|10)([.]0)?\s*\)', '\blog\s*\([^#]*,\s*(math[.])?e\s*\)']
scope: hunk
check_kind: mechanical
severity_default: minor
---

# A Python base-2 or base-10 logarithm calls math.log2(x) or math.log10(x), not math.log(x, 2) or math.log(x, 10), which is usually less accurate

## Thesis
A Python logarithm to base 2 is computed with `math.log2(x)` and one to base 10 with `math.log10(x)`, in place of `math.log(x, 2)` and `math.log(x, 10)`, and a natural logarithm is `math.log(x)` with no `math.e` base argument.

## Rationale
The two-argument `math.log(x, base)` is calculated as `log(x)/log(base)`; `math.log2(x)` is usually more accurate than `log(x, 2)`, and `math.log10(x)` is usually more accurate than `log(x, 10)`. The results of the two forms may differ due to floating-point rounding. With one argument `math.log` returns the natural logarithm, to base e, so specifying `math.e` as the base is redundant.

## Example
```python
bad:  import math
      from math import log
      depth = math.ceil(math.log(size, 2))  # 30 when size == 2**29
      scale = log(value, 10)
      rate = math.log(ratio, math.e)
good: import math
      depth = math.ceil(math.log2(size))    # 29 when size == 2**29
      scale = math.log10(value)
      rate = math.log(ratio)
```

## Limits
A base other than 2, 10 or e keeps the two-argument `math.log(x, base)`, which returns the logarithm of x to the given base. The accuracy gain is that the dedicated functions are usually more accurate, which is not a guarantee of an exact result.

## Validator
Grep the hunk for `math.log(` or a bare `log(` whose second argument is `2`, `10`, `2.0`, `10.0`, `e` or `math.e`. For a bare `log`, open the file's imports and confirm that the name is `math.log`, imported as `from math import log`, and not `cmath.log`, `numpy.log` or another function. Validator question: **Does the hunk call math.log with a base of 2, 10 or e where math.log2, math.log10 or one-argument math.log computes the same logarithm?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-158`, severity minor, `file`, `symbol`, `code` = the `math.log(x, base)` call verbatim from the diff, `fix` = `math.log2(x)`, `math.log10(x)` or `math.log(x)`, in Python, `rationale` = the dedicated function is usually more accurate than the two-argument form, which is calculated as `log(x)/log(base)`, or the `math.e` base is redundant).

## Source
- CPython Doc/library/math.rst §math.log2 (https://raw.githubusercontent.com/python/cpython/main/Doc/library/math.rst) — 'Return the base-2 logarithm of *x*. This is usually more accurate than ``log(x, 2)``.' (fetched)
- CPython Doc/library/math.rst §math.log10 (https://raw.githubusercontent.com/python/cpython/main/Doc/library/math.rst) — 'Return the base-10 logarithm of *x*.  This is usually more accurate than ``log(x, 10)``.' (fetched)
- CPython Doc/library/math.rst §math.log (https://raw.githubusercontent.com/python/cpython/main/Doc/library/math.rst) — 'With one argument, return the natural logarithm of *x* (to base *e*).'; 'With two arguments, return the logarithm of *x* to the given *base*, calculated as ``log(x)/log(base)``.' (fetched)
- Ruff FURB163 redundant-log-base (astral-sh/ruff crates/ruff_linter/src/rules/refurb/rules/redundant_log_base.rs) — 'Instead of passing 2 or 10 as the base, use `math.log2` or `math.log10` respectively, as these dedicated variants are typically more accurate than `math.log`.'; 'The default base of `math.log` is `e`, so specifying it explicitly is redundant.'; 'may differ due to floating-point rounding' (fetched)

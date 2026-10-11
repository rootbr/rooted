---
title: A Python emptiness test on a value that is strictly a sequence or string uses its truth value, never len() alone as the condition or a comparison with an empty literal
rule_id: PY-08
domain: code
step: [implement, review]
applies_to: [python]
triggers: ['\b(if|elif|while)\s+(not\s+)?len\([^)]*\)\s*:', '\b(and|or|assert)\s+(not\s+)?len\([^)]*\)\s*($|:|,|\)|\band\b|\bor\b)', '[=!]=\s*(\[\]|\(\)|""|\x27\x27|str\(\)|list\(\)|tuple\(\))', '(\[\]|""|\x27\x27)\s*[=!]=']
scope: file
check_kind: semantic
severity_default: suggestion
---

# A Python emptiness test on a value that is strictly a sequence or string uses its truth value, never len() alone as the condition or a comparison with an empty literal

## Thesis
In Python, an emptiness test on a value that is strictly a sequence or a string — a str, list or tuple — uses the fact that empty sequences are false, `if seq:` and `if not seq:`, never `len(seq)` alone as the condition, as in `if len(seq):` or `if not len(seq):`, and never a comparison with an empty literal, as in `seq != []` or `name == ""`.

## Rationale
Empty sequences are considered false in a boolean context, so a str, list or tuple tests its own emptiness: the call to `len` can be removed, and comparing a string to `""` is unnecessary because an empty string is falsy. The idiom holds only for a value that is strictly a sequence or a string. If the value can be something else Python considers falsy, such as `None`, `0` or another empty container, `if not x:` is not equivalent to the comparison it replaces, and following the rewrite blindly in weakly typed code creates hard-to-debug issues. Comparing the length against a scalar, such as `if len(x) > 1:`, is the other correct form.

## Example
```python
bad:  if len(pending):
          flush(pending)
      if items != []:
          render(items)
good: if pending:
          flush(pending)
      if items:
          render(items)
```

## Limits
A value that can also be `None`, `0` or another falsy object that is not a sequence keeps its explicit comparison, because `if not x:` would also accept those values. A check that does not consider the type of the variable being compared has a high false positive rate, so the type is established before a comparison is flagged. A length compared against a scalar, such as `len(seq) > 1` or `len(seq) == 0`, is outside the rule, and so is a dict or set compared with `{}` or `set()`, which lies outside the sequences and strings the rule covers.

## Validator
Grep the hunk for `len(...)` used alone as the test of if, elif, while or assert or as an operand of `and` or `or`, and for `==` or `!=` against `[]`, `()`, `""`, `''`, `str()`, `list()` or `tuple()` on either side. For each hit, open the file and establish the tested value's type from its annotation, its assignment or the call that produced it. Validator question: **Is a value that is strictly a str, list or tuple tested for emptiness by `len()` alone as the condition or by `==` or `!=` against an empty literal?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-08`, severity suggestion, `file`, `symbol`, `code` = the condition with `len()` or the empty-literal comparison, verbatim, `fix` = the truth-value test, such as `if pending:` or `if not name:`, `rationale` = that an empty str, list or tuple is false, so the call or the comparison is unnecessary, with the value's type that makes the rewrite equivalent).

## Source
- PEP 8 §Programming Recommendations (https://raw.githubusercontent.com/python/peps/main/peps/pep-0008.rst) — 'For sequences, (strings, lists, tuples), use the fact that empty sequences are false:' (fetched)
- Ruff PLC1802 len-test (astral-sh/ruff crates/ruff_linter/src/rules/pylint/rules/len_test.rs) — 'Empty sequences are considered false in a boolean context. You can either remove the call to `len` or compare the length against a scalar.' (fetched)
- Pylint use-implicit-booleaness-not-len (C1802) (pylint-dev/pylint doc/data/messages/u/use-implicit-booleaness-not-len/bad.py) — 'or compare the length against a scalar (``if len(x) > 1``).' (fetched)
- Pylint use-implicit-booleaness-not-comparison (C1803) (pylint-dev/pylint doc/data/messages/u/use-implicit-booleaness-not-comparison/bad.py) — 'Following this check blindly in weakly typed code base can create hard to debug issues. If the value can be something else that is falsey but not a sequence (for example ``None``, an empty string, or ``0``) the code will not be equivalent.' (fetched)
- Pylint use-implicit-booleaness-not-comparison-to-string (C1804) (pylint-dev/pylint doc/data/messages/u/use-implicit-booleaness-not-comparison-to-string/bad.py) — 'Empty string are considered false in a boolean context. Following this check blindly in weakly typed code base can create hard to debug issues.' (fetched)
- Ruff PLC1901 compare-to-empty-string (astral-sh/ruff crates/ruff_linter/src/rules/pylint/rules/compare_to_empty_string.rs) — 'An empty string is falsy, so it is unnecessary to compare it to `""`. If the value can be something else Python considers falsy, such as `None`, `0`, or another empty container, then the code is not equivalent.' (fetched)
- Ruff PLC1901 compare-to-empty-string (astral-sh/ruff crates/ruff_linter/src/rules/pylint/rules/compare_to_empty_string.rs) — 'High false positive rate, as the check is context-insensitive and does not consider the type of the variable being compared' (fetched)
- Caveat: the style guide states the idiom for sequences (strings, lists, tuples); dict and set comparisons are not carried.

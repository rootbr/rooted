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

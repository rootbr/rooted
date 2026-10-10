---
title: A Python test for None is written with is or is not, never with == or != and never through type(None)
rule_id: PY-03
domain: code
step: [implement, review]
applies_to: [python]
triggers: ['[=!]=\s*None\b', '\bNone\s*[=!]=', 'isinstance\([^,]+,\s*type\(None\)\)', '\btype\([^)]*\)\s*(is|==)\s*type\(None\)']
scope: hunk
check_kind: mechanical
severity_default: minor
---

# A Python test for None is written with is or is not, never with == or != and never through type(None)

## Thesis
A Python test for None is written `x is None` or `x is not None`, not `x == None`, `x != None`, `isinstance(x, type(None))` or `type(x) is type(None)`, except where x belongs to a library that overrides `==` or `!=`, where `is` may not be equivalent to the written comparison.

## Rationale
Comparisons to singletons like None should always be done with `is` or `is not`, never the equality operators. `x is y` is true if and only if x and y are the same object, and there is only ever one instance of None, so `x is None` checks for it directly, more efficiently and readably than `isinstance(x, type(None))` or a comparison of `type(x)` with `type(None)`. `==` and `!=` go through the operand's `__eq__` and `__ne__`, which a library can override, so for such an operand `is` and `is not` may not be equivalent to `==` and `!=`.

## Example
```python
bad:  if result == None:
          result = load()
good: if result is None:
          result = load()
```

## Limits
Where the operand belongs to a library that overrides `__eq__` or `__ne__`, rewriting `== None` as `is None` may alter runtime behaviour, and the comparison stays as written.

## Validator
Grep the hunk for `== None`, `!= None`, `None ==`, `None !=`, `isinstance(..., type(None))` and a comparison of `type(...)` with `type(None)`. Open the operand's type where the hunk or its imports show it; when its class overrides `__eq__` or `__ne__` and the comparison builds a library expression rather than a truth value, leave it. Validator question: **Does the hunk test a value for None with `==`, `!=`, `isinstance(x, type(None))` or a comparison of `type(x)` with `type(None)`, on an operand whose class does not override `__eq__` or `__ne__`?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-03`, severity minor, `file`, `symbol`, `code` = the None comparison as written, `fix` = `x is None` or `x is not None`, such as `if result is None:`, `rationale` = None is the only instance of its type, so the test is an identity test, and `==` runs the operand's `__eq__`).

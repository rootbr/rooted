---
title: A Python negated membership, identity or equality test is written x not in y, x is not y or a != b, never with not applied to the positive test
rule_id: PY-157
domain: code
step: [implement, refactor]
applies_to: [python]
triggers: ['\bnot\s+[\w.\[\]()]+\s+(in|is)\b', '\bnot\s+[\w.\[\]()]+\s*==\s*[^=]']
scope: hunk
check_kind: mechanical
severity_default: suggestion
---

# A Python negated membership, identity or equality test is written x not in y, x is not y or a != b, never with not applied to the positive test

## Thesis
A negated membership test in Python is written `x not in y`, a negated identity test `x is not y` and a negated equality test `a != b`, in place of `not x in y`, `not x is y` and `not a == b`.

## Rationale
`x not in s` returns the negation of `x in s`, and `x is not y` yields the inverse truth value of `x is y`, so the two-word operator computes the same result as `not` applied to the positive test; the two expressions being functionally identical, the operator form is the more readable one. For equality, user-defined classes that customize comparison should, if possible, make `x == y` and `not x != y` give the same result, and inverting the result of a boolean comparison is needlessly complex where the opposite comparison, `a != b`, states the same test.

## Example
```python
bad:  if not key in cache:
          cache[key] = load(key)
      if not left == right:
          report(left, right)
good: if key not in cache:
          cache[key] = load(key)
      if left != right:
          report(left, right)
```

## Limits
An ordering comparison under `not`, such as `not a < b`, is outside the rule: the consistency rules expect `x < y` and `not x >= y` to give the same result for a total ordering, and any ordered comparison of a number to a not-a-number value is false, so `not a < b` is true while `a >= b` is false when `a` is `float('NaN')`. The consistency between `==` and `!=` is a rule user-defined classes should follow if possible, so for operands of a class whose `__ne__` is not the inverse of its `__eq__` the two forms can differ and the rewrite is checked against those methods.

## Validator
Grep the hunk for `not` followed by an operand and then `in`, `is` or `==`. Confirm from the expression that `not` negates the whole comparison — `not x in y` parses as `not (x in y)` — and that the operator is `in`, `is` or `==`, not `<`, `<=`, `>` or `>=`. For `==` between instances of a user-defined class, open the class and confirm that it defines no `__ne__` or one that returns the inverse of `__eq__`. Validator question: **Does the hunk apply not to a membership, identity or equality comparison whose negated operator, not in, is not or !=, states the same test?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-157`, severity suggestion, `file`, `symbol`, `code` = the negated test verbatim from the diff, `fix` = the same test written `x not in y`, `x is not y` or `a != b`, in Python, `rationale` = the operator form computes the same result as `not` over the positive test and is the more readable one).

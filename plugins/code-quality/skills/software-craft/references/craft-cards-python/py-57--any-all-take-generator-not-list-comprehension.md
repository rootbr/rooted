---
title: Python any and all receive a generator expression rather than a list comprehension, so they stop at the first deciding element without building the whole list
rule_id: PY-57
domain: performance
step: [implement, review]
applies_to: [python]
triggers: ['\b(any|all)\(\s*\[', '\b(sum|min|max)\(\s*\[[^\]]*\bfor\b']
scope: hunk
check_kind: mechanical
severity_default: minor
---

# Python any and all receive a generator expression rather than a list comprehension, so they stop at the first deciding element without building the whole list

## Thesis
`any()` and `all()` receive a generator expression, not a list comprehension. `min()`, `max()` and `sum()` also receive a generator expression in place of an inline list comprehension whose list serves only that call.

## Rationale
A list comprehension inside `any()` or `all()` forces the entire list to be created in memory before the check begins, which prevents the short-circuit these functions are designed to leverage: `any()` stops at the first true element and `all()` at the first false one. A generator expression keeps that exit, so evaluation ends at the deciding element instead of calculating all the elements, while the comprehension forces a full iteration of the input. In a case where an early short-circuit is possible, the generator form of `all()` measured almost 40x faster. The condition, and any side effect it has, therefore runs for every element under the comprehension and only up to the deciding element under the generator. `min()`, `max()` and `sum()` have no short-circuit: for them the temporary list is unnecessary and wastes memory for large iterables, while speed may not improve, since if the entire iterable has to be traversed the comprehension version may even be a bit faster. For these three the generator form also avoids building the temporary list.

## Example
```python
bad:  if any([user.is_admin for user in users]):
          grant(user_ids)
      total = sum([order.amount for order in orders])
good: if any(user.is_admin for user in users):
          grant(user_ids)
      total = sum(order.amount for order in orders)
```

## Limits
Where the code relies on the condition's side effects for every element, the generator changes behavior, because it evaluates lazily and stops early; the rewrite is unsafe to apply mechanically there. A set comprehension counts as unnecessary only where the function does not care about duplicate elements, so `sum()` over a set comprehension, which drops duplicates first, is outside the rule. In `min()`, `max()` and `sum()` the generator may not improve performance and may even slightly regress it, though the difference will usually be small; the gain there is usually memory.

## Validator
Grep the hunk for `any([` and `all([`, and for `sum([`, `min([` or `max([` followed by a `for` clause. Open the call and confirm that the bracketed argument is a list comprehension written inline and that `any`, `all`, `sum`, `min` and `max` are the builtins, not names rebound in the module. Read the comprehension's element expression and pass it when it calls something whose side effect the surrounding code needs for every element, such as a check that records errors read after the call.
Validator question: **Does `any()`, `all()`, `min()`, `max()` or `sum()` receive an inline list comprehension whose element expression has no side effect the code needs on every element?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-57`, severity minor, `file`, `symbol`, `code` = the call with its list comprehension, `fix` = the same call with the square brackets removed, as `any(user.is_admin for user in users)`, `rationale` = the list comprehension builds the whole list and evaluates every element before the call, which gives up the short-circuit of `any()` and `all()` and allocates a temporary list for `min()`, `max()` and `sum()`).

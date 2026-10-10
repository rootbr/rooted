---
title: Python lists are flattened with itertools.chain or a comprehension, never with sum and an empty list start, because each addition copies the accumulated list
rule_id: PY-58
domain: performance
step: [implement, review]
applies_to: [python]
triggers: ['\bsum\(.*,\s*(start\s*=\s*)?\[\s*\]\s*\)', '\bsum\(.*,\s*(start\s*=\s*)?list\(\s*\)\s*\)']
scope: hunk
check_kind: mechanical
severity_default: major
---

# Python lists are flattened with itertools.chain or a comprehension, never with sum and an empty list start, because each addition copies the accumulated list

## Thesis
A list of lists is flattened with `list(itertools.chain.from_iterable(lists))`, `[item for sublist in lists for item in sublist]`, `functools.reduce(operator.iadd, lists, [])` or, on Python 3.15 and later, `[*sublist for sublist in lists]`, in place of `sum(lists, [])` or `sum(lists, start=[])`.

## Rationale
`sum()` adds the start value and the items of its iterable from left to right, and for lists each `+` concatenation creates a new list and copies all previous elements into it. Flattening this way is therefore quadratic in the number of lists, while each of the replacements is linear in the number of lists. Each intermediate concatenation also allocates a new list, creating memory overhead. `itertools.chain.from_iterable()` yields elements from each sub-list in sequence without creating intermediate list copies, and the documentation of `sum()` suggests `itertools.chain` for concatenating a series of iterables. Because the cost grows quadratically, code that works fine in development with small datasets may become unusable in production.

## Example
```python
bad:  flat = sum(rows, [])
      ids = sum([group.ids for group in groups], start=[])
good: flat = list(itertools.chain.from_iterable(rows))
      ids = [item for group in groups for item in group.ids]
```

## Limits
`sum()` over numbers, the items its documentation names as normal, lies outside the rule; the rule covers an empty list given as the start value to concatenate or flatten lists. The replacements accept any iterable, while `sum()` with a list start requires lists, so code that relies on `sum()` raising an error for a non-list item silently succeeds once rewritten.

## Validator
Grep the hunk for `sum(` whose second argument or `start=` keyword is `[]` or `list()`. Open the call and confirm that `sum` is the builtin and that its iterable yields lists that the call concatenates, as in `sum(rows, [])` or `sum(id_lists, start=[])`.
Validator question: **Does a `sum()` call take an empty list as its start value to concatenate lists?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-58`, severity major, `file`, `symbol`, `code` = the sum call with its empty-list start, `fix` = `list(itertools.chain.from_iterable(lists))` or `[item for sublist in lists for item in sublist]`, `rationale` = sum adds with `+`, which creates a new list and copies every element accumulated so far at each step, so the flattening is quadratic in the number of lists).

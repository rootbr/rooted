---
title: A Python loop whose body only appends a transformed or filtered item to a new list, or sets a key of a new dict, is written as a comprehension, and so is a map() over a lambda
rule_id: PY-156
domain: code
step: [implement, refactor]
applies_to: [python]
triggers: ['[.]append\s*\(', '\bmap\s*\(\s*lambda\b', '^\s*for\s+[A-Za-z_][\w, ()]*\s+in\s+.+:\s*(#.*)?$']
scope: hunk
check_kind: semantic
severity_default: minor
---

# A Python loop whose body only appends a transformed or filtered item to a new list, or sets a key of a new dict, is written as a comprehension, and so is a map() over a lambda

## Thesis
A Python `for` loop that starts from a new empty list or dict and whose body only appends an expression of the loop variable, optionally under one `if`, or only sets one key of that dict, is written as a list or dict comprehension; a loop that appends every item unchanged is written `list(items)`; and `map(lambda ...)`, alone or as the argument of `list()`, `set()` or `dict()`, is written as the generator expression or comprehension that inlines the lambda's body.

## Rationale
A `for` loop that builds a list creates, or overwrites, a variable named by its loop target that still exists after the loop completes; the comprehension computes the same list without that side effect and is more concise and readable. A lambda passed to `map()` adds function-call overhead for each element of the iterable, which the generator expression or comprehension avoids, in addition to being more readable. The speed gain is a micro-optimization with a negligible impact on performance in most cases: on benchmark loops over 1,000 to 10,000 integers the list comprehension runs about 10% faster than the loop on Python 3.11 and about 25% faster on Python 3.10, the dict comprehension about 10% faster on Python 3.11, and `list(items)` about 2x faster than the copying loop on Python 3.11. In a study of 101 performance-related questions about Python idioms on a programming question-and-answer site, developers often got confused about the performance impact of the idioms and relied on toy code or project experience whose performance outcomes are often contradictory. Preliminary experiments at scale found that list comprehension, generator expression, `zip` and `itertools.zip_longest` idioms can save up to 7,000 MB and up to 32.25 seconds.

## Example
```python
bad:  names = []
      for user in users:
          if user.active:
              names.append(user.name)
      ids = list(map(lambda u: u.id, users))
good: names = [user.name for user in users if user.active]
      ids = [u.id for u in users]
```

## Limits
A loop that appends to an existing list, or sets keys of an existing dict, keeps that object: the list takes `extend()` with a generator expression and the dict takes `update()` with a dict comprehension. When the source of an unchanged copy is already a list, `items.copy()` gives the same copy as `list(items)`. A `map` object and a generator expression are not interchangeable when the mapped expression raises: once an exception propagates out of a generator, the generator is closed and every later `next()` raises `StopIteration`, while a `map` object is not closed and iteration can resume after the error, so a caller that resumes iteration after an error keeps `map()`. A `map()` over a built-in function or a function written in C, rather than a lambda, is outside the rule, because that form can be very efficient.

## Validator
Grep the hunk for `.append(`, `map(lambda` and `for ... in ...:` lines. For each loop, open the lines above it and confirm that the list or dict it fills is bound to `[]`, `{}`, `list()` or `dict()` just before the loop and is not read inside it, and that the body is one `append` of an expression of the loop variable, optionally under one `if`, or one `result[key] = value`, with no other statement and no `break`. For a `map(lambda ...)` call, confirm that it is bare or the only argument of `list()`, `set()` or `dict()`, and that no caller resumes iterating it after an exception. Validator question: **Does the hunk fill a new list or dict with a loop whose body only appends one expression of the loop variable or sets one key, or map a lambda over an iterable, where a comprehension, a generator expression or `list(items)` gives the same result?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-156`, severity minor, `file`, `symbol`, `code` = the empty-collection binding with its loop, or the `map(lambda ...)` call, verbatim from the diff, `fix` = the list or dict comprehension, generator expression or `list(items)` that replaces it, in Python, `rationale` = the loop variable left bound after the loop or the per-element lambda call, with readability as the gain and the speedup named as negligible in most code).

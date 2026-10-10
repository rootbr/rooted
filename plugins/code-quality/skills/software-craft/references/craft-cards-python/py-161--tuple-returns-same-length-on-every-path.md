---
title: A function that returns tuples returns the same number of elements on every path unless its signature declares an arbitrary-length tuple
rule_id: PY-161
domain: code
step: [design, implement, review]
applies_to: [python]
triggers: ['^\s*return\s+\(.*,.*\)\s*(#.*)?$', '^\s*return\s+[\w.]+\s*,']
scope: file
check_kind: semantic
severity_default: major
---

# A function that returns tuples returns the same number of elements on every path unless its signature declares an arbitrary-length tuple

## Thesis
A Python function whose return statements return tuples returns tuples of one length on every code path, adding a placeholder value such as `None` or `0` to a shorter tuple, unless its return annotation is a homogeneous arbitrary-length `tuple[X, ...]`.

## Rationale
When a function returns tuples of varying lengths, callers cannot reliably unpack the return value without checking its length first, and the function signature provides no indication that the return type varies, so developers must read the implementation or discover the behaviour through runtime errors. An assignment to a target list without a starred target requires an iterable with the same number of items as there are targets, so `total, mean = stats([])` fails with ValueError when the empty-input path returns a 1-tuple. Such runtime errors from tuple unpacking may not surface during initial testing if the code path that returns the other length is not exercised. One length on every path lets every caller unpack the result into one fixed target list; for complex return types, a `typing.NamedTuple` return type gives the elements clear field names and enforces a consistent structure.

## Example
```python
bad:  def stats(values):
          if not values:
              return (0,)
          total = sum(values)
          return (total, total / len(values))
good: def stats(values):
          if not values:
              return (0, 0)
          total = sum(values)
          return (total, total / len(values))
```

## Limits
A function whose return annotation is a homogeneous arbitrary-length tuple, `tuple[X, ...]`, is outside the rule: that type is equivalent to a union of tuples containing zero or more `X` elements, so returns of different lengths match the declared type. The rule compares the tuples one function returns on its different paths; a path that returns a value other than a tuple display, such as `None`, and a tuple built with a starred element are outside it.

## Validator
Grep the hunk for return statements that return a tuple, `return (a, b)` or `return a, b`. Open the enclosing function in the file and collect every return statement of its own body, leaving out those of nested functions, lambdas and classes; count the elements of each returned tuple display, leaving out a return whose value is not a tuple display or whose tuple has a starred element. Read the function's return annotation and leave out the function when it is `tuple[X, ...]` or `Tuple[X, ...]`. Validator question: **Does one function return tuple displays of two or more different lengths on different paths while its return annotation is not an arbitrary-length `tuple[X, ...]`?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-161`, severity major, `file`, `symbol`, `code` = the return statement whose tuple length differs from the function's other returns, verbatim from the diff, `fix` = that return padded to the common length with a placeholder such as `None` or `0`, or every path returning one `typing.NamedTuple`, `rationale` = that a caller unpacking the result into a fixed number of targets fails at run time on the path that returns the other length).

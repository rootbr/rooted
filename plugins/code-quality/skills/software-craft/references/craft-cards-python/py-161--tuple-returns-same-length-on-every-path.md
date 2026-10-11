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

## Source
- SonarSource sonar-python S8495 functions-should-return-tuples-of-consistent-length (SonarSource/sonar-python python-checks/src/main/resources/org/sonar/l10n/py/rules/python/S8495.html) — 'This rule raises an issue when a function returns tuples of different lengths in different code paths.' (fetched); Why is this an issue? — 'When a function returns tuples of varying lengths, it creates an inconsistent API that is difficult to use correctly. Callers cannot reliably unpack the return value without checking its length first, which leads to fragile code.' (fetched); same — 'The function signature provides no indication that the return type varies, so developers must read the implementation or discover the behavior through runtime errors.' (fetched); same, example — 'x, y = result  # ValueError if value' (fetched); What is the potential impact? — 'Runtime errors from tuple unpacking may not surface during initial testing if certain code paths are not fully exercised' (fetched); How to fix it — 'Make all return statements return tuples of the same length. Add placeholder values (like None or 0) to shorter tuples to maintain consistency.' (fetched); Going the extra mile — 'For complex return types, consider using typing.NamedTuple to make the return value self-documenting.' (fetched); same — 'Named tuples provide clear field names and enforce a consistent structure' (fetched)
- CPython Doc/reference/simple_stmts.rst §Assignment statements (python/cpython Doc/reference/simple_stmts.rst) — 'Else: The object must be an iterable with the same number of items as there are targets in the target list, and the items are assigned, from left to right, to the corresponding targets.' (fetched)
- Typing spec docs/spec/tuples.rst §Tuple Type Form (python/typing docs/spec/tuples.rst) — 'Arbitrary-length homogeneous tuples can be expressed using one type and an ellipsis, for example ``tuple[int, ...]``. This type is equivalent to a union of tuples containing zero or more ``int`` elements' (fetched)
- Caveat: the Sonar check names no exemption; the `tuple[X, ...]` limit follows from the typing spec's definition of that type.

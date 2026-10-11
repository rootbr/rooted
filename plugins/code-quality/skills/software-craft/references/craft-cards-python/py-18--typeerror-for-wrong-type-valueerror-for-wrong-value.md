---
title: A Python check that rejects an argument for its type raises TypeError, and one that rejects a right-typed argument for its value raises ValueError
rule_id: PY-18
domain: errors
step: [design, implement, handle-errors]
applies_to: [python, exceptions, dynamic-types]
triggers: ['^\s*if\s+not\s+isinstance\(', '^\s*if\b.*\btype\(\w+\)\s*(is|==|!=|in)\b', '^\s*raise\s+ValueError\b']
scope: hunk
check_kind: mechanical
severity_default: minor
---

# A Python check that rejects an argument for its type raises TypeError, and one that rejects a right-typed argument for its value raises ValueError

## Thesis
In Python, a branch that rejects an argument after an `isinstance` or `type()` check raises `TypeError`, and a branch that rejects an argument of the right type for its value, such as a number outside expected boundaries, raises `ValueError`, unless a more precise exception such as `IndexError` describes the situation.

## Rationale
Python's built-in exceptions divide the two failures. `TypeError` is raised when an operation or function is applied to an object of inappropriate type; `ValueError` is raised when an operation or function receives an argument that has the right type but an inappropriate value, and the situation is not described by a more precise exception such as `IndexError`. The documentation states that passing arguments of the wrong type, such as a list when an int is expected, should result in a `TypeError`, and passing arguments with the wrong value, such as a number outside expected boundaries, should result in a `ValueError`. A type check that raises `ValueError` reports a wrong type under the class the documentation gives to a wrong value.

## Example
```python
bad:  if not isinstance(timeout, (int, float)):
          raise ValueError(f"timeout must be a number, not {type(timeout).__name__}")
good: if not isinstance(timeout, (int, float)):
          raise TypeError(f"timeout must be a number, not {type(timeout).__name__}")
      if timeout < 0:
          raise ValueError(f"timeout must be >= 0, got {timeout}")
```

## Limits
When an object is meant to support a given operation but has not yet provided an implementation, `NotImplementedError` is the proper exception to raise, not `TypeError`. A value failure that a more precise exception such as `IndexError` describes raises that exception. A type check whose branch raises nothing, because it converts the argument or dispatches on its type, is outside the rule.

## Validator
Grep the hunk for `isinstance(`, `issubclass(` and `type(...)` comparisons, and for `raise ValueError`. Open the function and pair each `raise` with the condition that guards it. Classify the condition as a type test on an argument or as a value test on an argument whose type is right: range, sign, length, membership, format. Count a raised class that subclasses `TypeError` as `TypeError`. Validator question: **Does a branch that rejects an argument for its type raise a class that is not TypeError or a subclass of it, or a branch that rejects a right-typed argument for its value raise TypeError?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-18`, severity minor, `file`, `symbol`, `code` = the type or value check and the `raise` it guards, `fix` = `raise TypeError(...)` under the type check and `raise ValueError(...)` under the value check, `rationale` = the documentation gives `TypeError` to an argument of inappropriate type and `ValueError` to a right-typed argument with an inappropriate value).

## Source
- CPython Doc/library/exceptions.rst §TypeError (https://docs.python.org/3/library/exceptions.html) — 'Raised when an operation or function is applied to an object of inappropriate type.' (fetched)
- CPython Doc/library/exceptions.rst §TypeError (https://docs.python.org/3/library/exceptions.html) — 'Passing arguments of the wrong type (e.g. passing a list when an int is expected) should result in a TypeError … passing arguments with the wrong value (e.g. a number outside expected boundaries) should result in a ValueError' (fetched)
- CPython Doc/library/exceptions.rst §TypeError (https://docs.python.org/3/library/exceptions.html) — 'If an object is meant to support a given operation but has not yet provided an implementation, NotImplementedError is the proper exception to raise.' (fetched)
- CPython Doc/library/exceptions.rst §ValueError (https://docs.python.org/3/library/exceptions.html) — 'Raised when an operation or function receives an argument that has the right type but an inappropriate value, and the situation is not described by a more precise exception such as IndexError' (fetched)
- Ruff TRY004 type-check-without-type-error (astral-sh/ruff crates/ruff_linter/src/rules/tryceratops/rules/type_check_without_type_error.rs) — 'The Python documentation states that `TypeError` should be raised upon encountering an inappropriate type.' (fetched)

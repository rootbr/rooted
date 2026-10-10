---
title: The message of a Python assert statement is a value such as a string, never a print() call whose None result becomes the AssertionError's argument
rule_id: PY-174
domain: errors
step: [implement, test, review]
applies_to: [python]
triggers: ['^\s*assert\b.*,\s*print\(', '\bassert\b[^#]*\bprint\(']
scope: hunk
check_kind: mechanical
severity_default: minor
---

# The message of a Python assert statement is a value such as a string, never a print() call whose None result becomes the AssertionError's argument

## Thesis
The second expression of a Python `assert` statement is the message itself, such as a string literal or an f-string, never a `print()` call.

## Rationale
The extended form `assert expression1, expression2` is equivalent to `if __debug__:` followed by `if not expression1: raise AssertionError(expression2)`, so when the assertion fails the evaluated value of the second expression becomes the contents of the `AssertionError`. The `print` function always returns `None`, so a `print()` call in that place outputs the message to `stdout` before raising an empty `AssertionError(None)`. Passing the message directly as the second expression keeps it in the exception, where `stderr` captures it in a well-formatted context.

## Example
```python
bad:  assert count > 0, print("count must be positive")
good: assert count > 0, "count must be positive"
```

## Limits
The second expression is evaluated only when `__debug__` is true and the assertion fails, so a passing assertion never calls `print()`. Any second expression whose value is the message text conforms.

## Validator
Grep the hunk for `assert` statements whose second expression, after the top-level comma, starts with `print(`; open the statement when it spans several lines. Validator question: **Is the second expression of this `assert` statement a call to `print()`?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-174`, severity minor, `file`, `symbol`, `code` = the `assert` statement, `fix` = the same `assert` with the text of the `print()` call as the message, as in `assert count > 0, "count must be positive"`, `rationale` = `print()` returns `None`, so the message goes to `stdout` and the `AssertionError` carries `None`).

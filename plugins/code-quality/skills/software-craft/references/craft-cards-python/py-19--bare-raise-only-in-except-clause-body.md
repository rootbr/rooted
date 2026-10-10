---
title: A bare raise in Python sits in the body of an except clause, never in a finally block or in a function that relies on being called from a handler
rule_id: PY-19
domain: errors
step: [handle-errors, review]
applies_to: [python, exceptions]
triggers: ['^\s*raise\s*(#.*)?$', '^\s*finally\s*:']
scope: file
check_kind: mechanical
severity_default: major
---

# A bare raise in Python sits in the body of an except clause, never in a finally block or in a function that relies on being called from a handler

## Thesis
In Python, a `raise` with no expression stands in the body of an `except` clause. In a `finally` block the code lets the exception propagate on its own, and in a helper function or any other place outside an `except` block it raises an exception it names.

## Rationale
A bare `raise` re-raises the exception that is currently being handled, the active exception, and when there is no active exception a `RuntimeError` is raised instead. In a function called in an `except` block it re-raises the exception that block caught, and that is not reliable, because nothing prevents a developer from calling the function from a different context, where no exception is active and `RuntimeError` is raised. In a `finally` block it has an active exception to re-raise only when an exception from the `try` block is not caught or when an exception is raised by an `except` or `else` block, and in both cases it is better to let the exception propagate automatically than to re-raise it.

## Example
```python
bad:  def fail(message):
          logger.error(message)
          raise  # RuntimeError when the caller handles no exception
good: try:
          write(record)
      except OSError:
          logger.exception("write failed")
          raise
      if not record.valid:
          raise ValidationError(record)
```

## Limits
In the body of an `except` clause the bare `raise` is the intended form: the exception currently being handled is the one that clause caught. The rule covers `raise` with no expression; `raise error` and `raise NewError(...) from error` name their exception and are outside it.

## Validator
Grep the hunk for a `raise` line with no expression and for `finally:` lines. Open the enclosing function in the file and walk outward from the `raise` through its enclosing blocks up to the function boundary, noting whether an `except` clause body is among them before a `finally` block or the function boundary is reached. Validator question: **Does a bare raise sit outside every except clause body of its own function, in a finally block, in the plain function body or at module level?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-19`, severity major, `file`, `symbol`, `code` = the bare `raise` line and the block header that encloses it, `fix` = in a `finally` block the bare `raise` removed so the exception propagates on its own; elsewhere `raise ValidationError(message)` naming the exception, or the bare `raise` moved into the caller's own `except` body, `rationale` = a bare raise re-raises whatever exception is active when it runs and raises `RuntimeError` when none is).

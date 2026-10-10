---
title: A Python exception class derives from Exception or one of its subclasses, not directly from BaseException, SystemExit, KeyboardInterrupt or GeneratorExit, unless catching it is almost always wrong
rule_id: PY-17
domain: errors
step: [design, implement]
applies_to: [python, exceptions, object-oriented]
triggers: ['^\s*class\s+\w+\s*\((.*,\s*)?(BaseException|SystemExit|KeyboardInterrupt|GeneratorExit)\s*[,)]', '^\s*class\s+\w+\s*\(.*\bBaseException\b']
scope: hunk
check_kind: mechanical
severity_default: major
---

# A Python exception class derives from Exception or one of its subclasses, not directly from BaseException, SystemExit, KeyboardInterrupt or GeneratorExit, unless catching it is almost always wrong

## Thesis
A user-defined Python exception class inherits from `Exception` or one of its subclasses, not from `BaseException` directly and not from `SystemExit`, `KeyboardInterrupt` or `GeneratorExit`; direct inheritance from `BaseException` is kept for an exception where catching it is almost always the wrong thing to do.

## Rationale
Python roots its hierarchy in `BaseException`, from which `SystemExit`, `KeyboardInterrupt` and `Exception` derive, so that code can use `except Exception:` without preventing the software from stopping. `SystemExit` inherits from `BaseException`, not from `Exception`, so that it is not accidentally caught by code that catches `Exception`, and `GeneratorExit` directly inherits from `BaseException` because it is technically not an error. A user-defined class that inherits from `BaseException` and not from `Exception` is, by the same placement, not caught by code that catches `Exception`. All built-in, non-system-exiting exceptions are derived from `Exception`, and all user-defined exceptions should also be derived from it.

## Example
```python
bad:  class RetryAbort(BaseException):  # passes every except Exception: handler
          """A job gave up after its retries."""
good: class RetryAbort(Exception):
          """A job gave up after its retries."""
```

## Limits
The sources divide on direct inheritance from `BaseException`. One position reserves it for exceptions where catching them is almost always the wrong thing to do, as with `SystemExit` and `KeyboardInterrupt`, which are expected to propagate up until the application stops. The stricter position holds that `BaseException` is not meant to be directly inherited by user-defined classes and that exceptions should typically be derived from `Exception`, directly or indirectly, and reports every class that derives from `BaseException`, `KeyboardInterrupt`, `SystemExit` or `GeneratorExit`. The separating condition is the first position's: a class whose catching is almost always the wrong thing to do may derive from `BaseException` directly; every other user-defined exception derives from `Exception`. That reservation names direct inheritance from `BaseException` only.

## Validator
Grep the hunk for `class` statements whose bases name `BaseException`, `SystemExit`, `KeyboardInterrupt` or `GeneratorExit`. Open the class, its docstring, its `raise` sites in the hunk and the handlers meant to catch it. Decide whether it is a stop signal that catching is almost always wrong, or a failure some caller is meant to catch and handle. Validator question: **Does a user-defined exception class inherit from SystemExit, KeyboardInterrupt or GeneratorExit, or directly from BaseException while it signals a failure that callers are meant to catch?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-17`, severity major, `file`, `symbol`, `code` = the `class` line with its bases, `fix` = `class RetryAbort(Exception):` or a subclass of an existing `Exception` subclass, `rationale` = a class that inherits from `BaseException` instead of `Exception` is not caught by code that catches `Exception`).

---
title: A Python logger.exception() call never passes a false exc_info, and a record that must carry no traceback is logged with logger.error()
rule_id: PY-108
domain: errors
step: [implement, refactor, review]
applies_to: [python, exceptions]
triggers: ['[.]exception\(.*\bexc_info\s*=\s*(?:False|None|0)\b', '\bexc_info\s*=\s*False\b']
scope: hunk
check_kind: mechanical
severity_default: minor
---

# A Python logger.exception() call never passes a false exc_info, and a record that must carry no traceback is logged with logger.error()

## Thesis
A Python call to `Logger.exception()` or `logging.exception()` passes no `exc_info` that evaluates as false, and a record at `ERROR` level that must carry no exception information is logged with `logger.error()`.

## Rationale
`Logger.exception()` logs a message with level `ERROR` on its logger, interprets its arguments as `Logger.debug()` does, and adds exception info to the logging message; it captures the exception automatically and accepts an optional `exc_info` argument that overrides this behaviour. The logging reference ties exception information to this argument: if `exc_info` does not evaluate as false, exception information is added to the logging message, and setting `exc_info` to `False` disables the automatic capture of the exception and stack trace. `logger.error()` has equivalent behaviour to `logger.exception()` with `exc_info` set to `False`, and is clearer in intent.

## Example
```python
bad:  try:
          send(payload)
      except OSError:
          logger.exception("retry %d failed", attempt, exc_info=False)
good: try:
          send(payload)
      except OSError:
          logger.error("retry %d failed", attempt)
```

## Limits
A call that wants the traceback keeps `logger.exception()` and drops the `exc_info` argument. The rule reaches the `exc_info` of an `exception()` call only; the logging reference adds that `exception()` should only be called from an exception handler, and `logger.error()` with an `exc_info` that does not evaluate as false adds exception information as well. The disabling effect is stated for `exc_info=False`; `None` and `0`, which Python's truth value testing counts as false, are flagged on the reference's condition that exception information is added when `exc_info` does not evaluate as false.

## Validator
Grep the hunk for `exc_info=` and for `.exception(`. Open each `exception()` call on a logger, a `logging.LoggerAdapter` or the `logging` module, which may span several lines, and read its `exc_info` keyword. Count `False`, `None`, `0` and any other literal that evaluates as false as false; for a name, trace its value in the function, and for a `**kwargs` mapping, trace whether it carries `exc_info`. Validator question: **Does an exception() call of a logger or of the logging module in the hunk pass an exc_info that evaluates as false?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-108`, severity minor, `file`, `symbol`, `code` = the `exception()` call with its false `exc_info` quoted verbatim from the diff, `fix` = the same message and arguments logged with `logger.error(...)` and no `exc_info`, or `logger.exception(...)` without `exc_info` where the traceback is wanted, `rationale` = names that a false exc_info disables the capture of the exception and stack trace that exception() adds, and that error() has equivalent behaviour and is clearer in intent).

## Source
- Ruff LOG007 exception-without-exc-info (astral-sh/ruff crates/ruff_linter/src/rules/flake8_logging/rules/exception_without_exc_info.rs) — 'The `logging.exception()` method captures the exception automatically, but accepts an optional `exc_info` argument to override this behavior.' (fetched)
- Ruff LOG007 exception-without-exc-info (astral-sh/ruff crates/ruff_linter/src/rules/flake8_logging/rules/exception_without_exc_info.rs) — 'Setting `exc_info` to `False` disables the automatic capture of the exception and stack trace.' (fetched)
- Ruff LOG007 exception-without-exc-info (astral-sh/ruff crates/ruff_linter/src/rules/flake8_logging/rules/exception_without_exc_info.rs) — 'which has equivalent behavior to `logging.exception()` with `exc_info` set to `False`, but is clearer in intent' (fetched)
- CPython Doc/library/logging.rst §Logger Objects, Logger.exception (https://raw.githubusercontent.com/python/cpython/main/Doc/library/logging.rst) — 'Logs a message with level :const:`ERROR` on this logger. The arguments are interpreted as for :meth:`debug`. Exception info is added to the logging message.' (fetched)
- CPython Doc/library/logging.rst §Logger Objects, Logger.exception (https://raw.githubusercontent.com/python/cpython/main/Doc/library/logging.rst) — 'This method should only be called from an exception handler.' (fetched)
- CPython Doc/library/logging.rst §Logger Objects, Logger.debug (https://raw.githubusercontent.com/python/cpython/main/Doc/library/logging.rst) — 'If *exc_info* does not evaluate as false, it causes exception information to be added to the logging message.' (fetched)
- CPython Doc/library/logging.rst §Logger Objects, Logger.error (https://raw.githubusercontent.com/python/cpython/main/Doc/library/logging.rst) — 'Logs a message with level :const:`ERROR` on this logger. The arguments are interpreted as for :meth:`debug`.' (fetched)
- CPython Doc/library/logging.rst §Module-Level Functions, exception() (https://raw.githubusercontent.com/python/cpython/main/Doc/library/logging.rst) — 'Logs a message with level :const:`ERROR` on the root logger.' (fetched)
- CPython Doc/builtins/stdtypes.rst §Truth Value Testing (https://raw.githubusercontent.com/python/cpython/main/Doc/builtins/stdtypes.rst) — 'constants defined to be false: ``None`` and ``False``' (fetched)
- CPython Doc/builtins/stdtypes.rst §Truth Value Testing (https://raw.githubusercontent.com/python/cpython/main/Doc/builtins/stdtypes.rst) — 'zero of any numeric type: ``0``' (fetched)
- Caveat: the disabling effect is stated for `exc_info=False`; for `None` and `0` the card rests on the reference's evaluates-as-false condition.

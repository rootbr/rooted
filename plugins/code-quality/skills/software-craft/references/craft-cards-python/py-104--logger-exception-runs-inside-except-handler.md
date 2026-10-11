---
title: A Python logger.exception() call or a logging call with exc_info=True runs inside an except handler, and code outside one logs with error() or passes the exception instance itself as exc_info
rule_id: PY-104
domain: errors
step: [handle-errors, implement, review]
applies_to: [python, exceptions]
triggers: ['[.]exception\(', '\bexc_info\s*=\s*True\b']
scope: callers
check_kind: semantic
severity_default: minor
---

# A Python logger.exception() call or a logging call with exc_info=True runs inside an except handler, and code outside one logs with error() or passes the exception instance itself as exc_info

## Thesis
A Python logger.exception() call, or a logging call with exc_info=True, executes while an except block is handling an exception; code that logs an error where no exception is being handled calls logger.error() without exc_info, or, when it holds an exception object, passes that instance as exc_info.

## Rationale
Logger.exception() adds exception information to the logging message, and the logging documentation states that it should only be called from an exception handler. A true exc_info that is neither an exception tuple nor an exception instance makes the logging module call sys.exc_info() to get the exception information, and sys.exc_info() returns a tuple of three None values if no exception is being handled anywhere on the stack. Outside a handler, .exception() and exc_info=True therefore attach None as the exception information, leading to confusing messages whose text ends in NoneType: None. An exception instance passed as exc_info is used as given.

## Example
```python
bad:  if not path.exists():
          logger.exception("config file %s not found", path)
good: if not path.exists():
          logger.error("config file %s not found", path)
```

## Limits
What counts is where the call executes, not where it is written: a function defined in an except block but called outside of it may not have access to an active exception at runtime, while a helper defined elsewhere and called from the body of an except block runs while that exception is being handled.

## Validator
Grep the file for .exception( on a logger or the logging module and for exc_info=True. For each hit, open the enclosing function and trace where it executes, following the enclosing function's callers across the repository: directly in the body of an except block, in a function called only from except blocks, or elsewhere (a plain branch, or a callback or closure that runs after the handler has finished). Validator question: **Does a logger.exception() call or a logging call with exc_info=True execute where no exception is being handled?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-104`, severity minor, `file`, `symbol`, `code` = the logging call verbatim, `fix` = `logger.error(...)` without exc_info, or `exc_info=err` with the exception instance the code holds, `rationale` = outside a handler the record's exception information is None and its text ends in NoneType: None).

## Source
- Ruff LOG004 log-exception-outside-except-handler (astral-sh/ruff crates/ruff_linter/src/rules/flake8_logging/rules/log_exception_outside_except_handler.rs) — 'Calling `.exception()` outside of an exception handler attaches `None` as exception information, leading to confusing messages' and 'ERROR:root:example NoneType: None' and 'This rule checks whether a call is _defined_ inside an exception handler, not whether it _executes_ inside one.' and 'despite the fact that the call may not have access to an active exception at runtime' (fetched)
- Ruff LOG014 exc-info-outside-except-handler (astral-sh/ruff crates/ruff_linter/src/rules/flake8_logging/rules/exc_info_outside_except_handler.rs) — 'Using `exc_info=True` outside of an exception handler attaches `None` as the exception information, leading to confusing messages' (fetched)
- CPython Doc/library/logging.rst §Logger Objects, Logger.exception (https://raw.githubusercontent.com/python/cpython/main/Doc/library/logging.rst) — 'Exception info is added to the logging message. This method should only be called from an exception handler.' (fetched)
- CPython Doc/library/logging.rst §Logger Objects, Logger.debug (https://raw.githubusercontent.com/python/cpython/main/Doc/library/logging.rst) — 'If an exception tuple (in the format returned by :func:`sys.exc_info`) or an exception instance is provided, it is used; otherwise, :func:`sys.exc_info` is called to get the exception information.' (fetched)
- CPython Doc/library/sys.rst §exc_info() (https://raw.githubusercontent.com/python/cpython/main/Doc/library/sys.rst) — 'If no exception is being handled anywhere on the stack, this function return a tuple containing three ``None`` values.' (fetched)

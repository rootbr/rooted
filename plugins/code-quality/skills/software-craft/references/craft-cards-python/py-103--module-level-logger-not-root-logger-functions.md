---
title: Python module code of a program or library logs through a module-level logger from logging.getLogger(__name__), not through the logging.debug, info, warning, error, exception, critical or log functions of the root logger
rule_id: PY-103
domain: errors
step: [implement, review]
applies_to: [python]
triggers: ['\blogging[.](?:debug|info|warning|warn|error|exception|critical|log)\(', '^\s*from\s+logging\s+import\s+.*\b(?:debug|info|warning|warn|error|exception|critical)\b']
scope: file
check_kind: mechanical
severity_default: minor
---

# Python module code of a program or library logs through a module-level logger from logging.getLogger(__name__), not through the logging.debug, info, warning, error, exception, critical or log functions of the root logger

## Thesis
Outside a very short script or a quick demonstration of logging facilities, Python module code logs through a module-level logger, logger = logging.getLogger(__name__), and calls its level-specific methods, rather than the module-level functions logging.debug(), info(), warning(), error(), exception(), critical() or log(), which log on the root logger.

## Rationale
The module-level functions log on the root logger: debug() is a convenience function that calls Logger.debug() on the root logger, and info(), for one, logs a message with level INFO on the root logger. Using the root logger causes the messages to have no source information, making them less useful for debugging. If no handlers are defined for the root logger, debug(), info(), warning(), error() and critical() call basicConfig() automatically, and basicConfig() does nothing if the root logger already has handlers configured unless force=True; so a module-level call that runs before the entry point configures logging installs that default configuration, and a later basicConfig() call at the entry point without force=True does nothing. Most programs will want to carefully and explicitly control the logging configuration, and the logging documentation therefore prefers a module-level logger with its level-specific methods.

## Example
```python
bad:  logging.info("cache warmed in %.1f s", elapsed)
good: logger = logging.getLogger(__name__)
      logger.info("cache warmed in %.1f s", elapsed)
```

## Limits
For very short scripts or quick demonstrations of logging facilities, the module-level functions may be convenient, and the card does not flag them there. Configuration calls at the entry point, such as logging.basicConfig(), are not logging calls and are outside the card.

## Validator
Grep the file for calls logging.debug(, logging.info(, logging.warning(, logging.warn(, logging.error(, logging.exception(, logging.critical( or logging.log(, and for a from logging import of those names followed by a bare call. Open the file and judge whether it is module code of a program or library (an importable or package module) or a very short script or quick demonstration of logging. Validator question: **Does module code of a program or library, not a very short script or quick demonstration, log through one of the logging module's module-level functions on the root logger?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-103`, severity minor, `file`, `symbol`, `code` = the module-level logging call verbatim, `fix` = a module-level `logger = logging.getLogger(__name__)` and the same call on `logger`, `rationale` = the record is logged on the root logger with no source information and the call may apply the default configuration before the entry point configures logging).

## Source
- Ruff LOG015 root-logger-call (astral-sh/ruff crates/ruff_linter/src/rules/flake8_logging/rules/root_logger_call.rs) — 'Using the root logger causes the messages to have no source information, making them less useful for debugging.' (fetched)
- CPython Doc/library/logging.rst §Module-Level Functions, debug() (https://raw.githubusercontent.com/python/cpython/main/Doc/library/logging.rst) — 'This is a convenience function that calls :meth:`Logger.debug`, on the root logger.' and 'Logs a message with level :const:`INFO` on the root logger.' and 'For very short scripts or quick demonstrations of ``logging`` facilities, ``debug`` and the other module-level functions may be convenient. However, most programs will want to carefully and explicitly control the logging configuration, and should therefore prefer creating a module-level logger and calling :meth:`Logger.debug` (or other level-specific methods) on it' (fetched)
- CPython Doc/library/logging.rst §Module-Level Functions, basicConfig() (https://raw.githubusercontent.com/python/cpython/main/Doc/library/logging.rst) — 'The functions :func:`debug`, :func:`info`, :func:`warning`, :func:`error` and :func:`critical` will call :func:`basicConfig` automatically if no handlers are defined for the root logger.' and 'This function does nothing if the root logger already has handlers configured, unless the keyword argument *force* is set to ``True``.' (fetched)
- CPython Doc/howto/logging.rst §Advanced Logging Tutorial (https://raw.githubusercontent.com/python/cpython/main/Doc/howto/logging.rst) — 'A good convention to use when naming loggers is to use a module-level logger, in each module which uses logging, named as follows' (fetched)

---
title: A key in the extra mapping of a Python logging call never names a LogRecord attribute such as name, msg, args, module, message or asctime
rule_id: PY-107
domain: errors
step: [implement, review]
applies_to: [python]
triggers: ['\bextra\s*=\s*\{[^}]*[\x22\x27](?:args|asctime|created|exc_info|exc_text|filename|funcName|levelname|levelno|lineno|message|module|msecs|msg|name|pathname|process|processName|relativeCreated|stack_info|taskName|thread|threadName)[\x22\x27]\s*:', '\bextra\s*=\s*dict\([^)]*\b(?:args|asctime|created|exc_info|exc_text|filename|funcName|levelname|levelno|lineno|message|module|msecs|msg|name|pathname|process|processName|relativeCreated|stack_info|taskName|thread|threadName)\s*=']
scope: hunk
check_kind: mechanical
severity_default: major
---

# A key in the extra mapping of a Python logging call never names a LogRecord attribute such as name, msg, args, module, message or asctime

## Thesis
Each key of the `extra` mapping passed to a Python `logging` call is a name the logging system does not use: none of the attribute names in the logging reference's LogRecord attributes table, such as `name`, `msg`, `args`, `module`, `message` or `asctime`.

## Rationale
The `logging` module passes the values given through the `extra` keyword argument to the `LogRecord` constructor. A key that clashes with a built-in `LogRecord` attribute, among them `name`, `msg`, `args`, `created`, `filename`, `funcName`, `levelname`, `levelno`, `lineno`, `module`, `msecs`, `message`, `pathname`, `process`, `processName`, `relativeCreated`, `thread` and `threadName`, raises `KeyError` when the `LogRecord` is constructed, so the logging statement fails at run time. The logging reference states that the keys in the dictionary passed in `extra` should not clash with the keys used by the logging system, and refers to its LogRecord attributes section for which keys the logging system uses.

## Example
```python
bad:  logger.info("user signed in", extra={"name": user.name})
good: logger.info("user signed in", extra={"user_name": user.name})
```

## Limits
The `extra` mapping exists to populate the record with user-defined attributes, which can then be used as the caller likes; the reference's example passes `clientip` and `user`, which a `Formatter` format string expects in the attribute dictionary of the `LogRecord`. The rule does not reach a key that a format string expects and a call leaves out; for that case the reference states that the message will not be logged because a string formatting exception will occur. The run-time `KeyError` is stated for the attribute names listed in the Rationale; for the other names of the table, such as `asctime`, the reference states that `extra` keys should not clash with them.

## Validator
Grep the hunk for `extra=` in a call of a logger method (`debug`, `info`, `warning`, `error`, `exception`, `critical`, `log`) or of the `logging` module function of the same name. Read every key of a dict literal or `dict(...)` call passed as `extra`; for a name passed as `extra`, trace it to where its keys are set in the function. Trace the call target to a `logging.Logger`, a logger from `logging.getLogger` or the `logging` module, since a match by the receiver's name alone is a heuristic. Compare each key with the attribute names of the LogRecord attributes table: `args`, `asctime`, `created`, `exc_info`, `exc_text`, `filename`, `funcName`, `levelname`, `levelno`, `lineno`, `message`, `module`, `msecs`, `msg`, `name`, `pathname`, `process`, `processName`, `relativeCreated`, `stack_info`, `taskName`, `thread`, `threadName`. Validator question: **Does a key of an extra mapping passed to a logging call in the hunk equal an attribute name of the LogRecord attributes table?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-107`, severity major, `file`, `symbol`, `code` = the logging call with its `extra` mapping quoted verbatim from the diff, `fix` = the same call with the clashing key renamed to a name of its own, such as `extra={"user_name": user.name}`, and any format string that reads the key renamed with it, `rationale` = names the LogRecord attribute the key clashes with and that a clashing key raises KeyError when the LogRecord is constructed).

## Source
- Ruff G101 logging-extra-attr-clash (astral-sh/ruff crates/ruff_linter/src/rules/flake8_logging_format/violations.rs) — 'These values are then passed to the `LogRecord` constructor.' (fetched)
- Ruff G101 logging-extra-attr-clash (astral-sh/ruff crates/ruff_linter/src/rules/flake8_logging_format/violations.rs) — 'Providing a value via `extra` that clashes with one of the attributes of the `LogRecord` constructor will raise a `KeyError` when the `LogRecord` is constructed.' (fetched)
- SonarSource python S8554 (SonarSource/sonar-python python-checks/src/main/resources/org/sonar/l10n/py/rules/python/S8554.html) §Attribute Name Collisions — 'is constructed, causing the logging statement to fail at runtime' (fetched)
- CPython Doc/library/logging.rst §Logger Objects, Logger.debug (https://raw.githubusercontent.com/python/cpython/main/Doc/library/logging.rst) — 'The keys in the dictionary passed in *extra* should not clash with the keys used by the logging system.' (fetched)
- CPython Doc/library/logging.rst §Logger Objects, Logger.debug (https://raw.githubusercontent.com/python/cpython/main/Doc/library/logging.rst) — 'created for the logging event with user-defined attributes. These custom attributes can then be used as you like.' (fetched)
- CPython Doc/library/logging.rst §Logger Objects, Logger.debug (https://raw.githubusercontent.com/python/cpython/main/Doc/library/logging.rst) — 'has been set up with a format string which expects' (fetched)
- CPython Doc/library/logging.rst §Logger Objects, Logger.debug (https://raw.githubusercontent.com/python/cpython/main/Doc/library/logging.rst) — 'If these are missing, the message will not be logged because a string formatting exception will occur.' (fetched)
- CPython Doc/library/logging.rst §LogRecord attributes (https://raw.githubusercontent.com/python/cpython/main/Doc/library/logging.rst) — 'The following table lists (in alphabetical order) the attribute names, their meanings and the corresponding placeholder in a %-style format string.' (fetched)
- Caveat: the KeyError is stated for the attributes of the LogRecord constructor and for the eighteen names the Sonar rule lists; for the other names of the table the evidence states the should-not-clash norm only.

---
title: A Python logging call passes the variable parts of its message as arguments to a %-style template instead of building the message before the call with an f-string, str.format, the % operator, + or a str() or repr() conversion
rule_id: PY-101
domain: errors
step: [implement, refactor, review]
applies_to: [python]
triggers: ['[.](?:debug|info|warning|warn|error|exception|critical)\(\s*f[\"'']', '[.](?:debug|info|warning|warn|error|exception|critical)\(\s*[\"''][^\"'']*[\"'']\s*[.]format\(', '[.](?:debug|info|warning|warn|error|exception|critical)\(\s*[\"''][^\"'']*[\"'']\s*%\s*[\w(]', '[.](?:debug|info|warning|warn|error|exception|critical)\(\s*(?:\w+|[\"''][^\"'']*[\"''])\s*\+', '[.](?:debug|info|warning|warn|error|exception|critical)\(\s*[\"''][^\"'']*%[^\"'']*[\"'']\s*,.*\b(?:str|repr|hex|oct)\(']
scope: hunk
check_kind: mechanical
severity_default: minor
---

# A Python logging call passes the variable parts of its message as arguments to a %-style template instead of building the message before the call with an f-string, str.format, the % operator, + or a str() or repr() conversion

## Thesis
A Python call to a logging method that takes a %-placeholder template as its first argument (debug(), info(), warning(), error(), exception() or critical()) passes a string literal as that template and the variable values as subsequent arguments, or in extra, and leaves the message unbuilt before the call: no f-string, str.format(), % operator or + concatenation builds it, and no argument is eagerly converted to a string with str(), repr(), hex() or oct() before it is passed.

## Rationale
The logging module treats the first argument as the message format string and merges the arguments into it with the string formatting operator, and that formatting is deferred until it cannot be avoided; no % formatting is performed on the message when no arguments are supplied. An f-string, str.format(), % or + expression makes Python format the string eagerly, even if the logging statement is never executed, for example when the log level is above the level of the statement. Passing the values as arguments lets the logger skip formatting entirely when the record is filtered out by level, which matters when the arguments have an expensive __str__ or __repr__. The arguments are formatted as strings automatically, so converting them before the call is unnecessary and less efficient. Some logging implementations collect the unexpanded pattern-string as a queryable field, and values passed in extra are made available to all handlers.

## Example
```python
bad:  logger.info(f"loaded {count} rows from {path}")
good: logger.info("loaded %d rows from %s", count, path)
```

## Limits
The convention is contested, and the project's linter configuration separates the cases. One position, the deferring side, holds that a message built before the call is formatted even when it is never output. The other position, the f-string side, calls f-strings another reasonable option, selected by enabling logging-not-lazy and logging-format-interpolation and disabling logging-fstring-interpolation; a project whose linter configuration explicitly disables logging-fstring-interpolation (Pylint W1203) or G004 (Ruff) has taken that side, so its f-strings are its convention and the card does not flag them, while str.format(), the % operator and + stay in scope. Deferral covers the formatting only: computing the arguments passed to the call can also be expensive, and the documented way to avoid that work is a guard on logger.isEnabledFor(level), which returns true if the event would be created for that level. A logging function whose first argument is not a %-placeholder pattern-string is outside the card.

## Validator
Grep the hunk for a call to .debug(, .info(, .warning(, .warn(, .error(, .exception( or .critical( whose first argument is an f-string, a string literal followed by .format( or by %, or a + concatenation, or whose argument is wrapped in str(), repr(), hex() or oct(). Confirm the receiver is a logger from the logging module (a logging.getLogger() result or the logging module itself). For an f-string hit, open the project's linter configuration (pyproject.toml, setup.cfg, .pylintrc, ruff.toml) and drop the hit when it explicitly disables logging-fstring-interpolation or G004. Validator question: **Does a call to a %-template logging method build its message before the call with an f-string the linter configuration does not permit, str.format(), the % operator or +, or eagerly convert an argument to a string with str(), repr(), hex() or oct()?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-101`, severity minor, `file`, `symbol`, `code` = the logging call verbatim, `fix` = the same call with a string-literal %-template as its first argument and the values as subsequent arguments or in `extra`, `rationale` = the message is formatted before the call even when the logger's level filters the record out).

## Source
- Ruff G004 logging-f-string (astral-sh/ruff crates/ruff_linter/src/rules/flake8_logging_format/violations.rs) — 'Using f-strings to format a logging message requires that Python eagerly format the string, even if the logging statement is never executed (e.g., if the log level is above the level of the logging statement)' and 'As an alternative to `extra`, passing values as arguments to the logging method can also be used to defer string formatting until required.' and 'the use of `extra` will ensure that the values are made available to all handlers' (fetched)
- Ruff G001 logging-string-format (astral-sh/ruff crates/ruff_linter/src/rules/flake8_logging_format/violations.rs) — 'Using `str.format` to format a logging message requires that Python eagerly format the string' (fetched)
- Ruff G002 logging-percent-format (astral-sh/ruff crates/ruff_linter/src/rules/flake8_logging_format/violations.rs) — 'Using `printf`-style format strings to format a logging message requires that Python eagerly format the string' (fetched)
- Ruff G003 logging-string-concat (astral-sh/ruff crates/ruff_linter/src/rules/flake8_logging_format/violations.rs) — 'Using concatenation to format a logging message requires that Python eagerly format the string' (fetched)
- Ruff RUF065 logging-eager-conversion (astral-sh/ruff crates/ruff_linter/src/rules/ruff/rules/logging_eager_conversion.rs) — 'Checks for eager string conversion of arguments to `logging` calls.' and 'Arguments to `logging` calls will be formatted as strings automatically, so it is unnecessary and less efficient to eagerly format the arguments before passing them in.' (fetched)
- Pylint logging-fstring-interpolation (W1203) (pylint-dev/pylint doc/data/messages/l/logging-fstring-interpolation/details.rst) — 'lets the logger skip formatting entirely when the record is filtered out by level. This matters when the arguments have an expensive ``__str__`` or ``__repr__``.' (fetched)
- Pylint logging-not-lazy (W1201) (pylint-dev/pylint doc/data/messages/l/logging-not-lazy/details.rst) — 'Another reasonable option is to use f-strings. If you want to do that, you need to enable ``logging-not-lazy`` and disable ``logging-fstring-interpolation``.' (fetched)
- Pylint logging-format-interpolation (W1202) (pylint-dev/pylint doc/data/messages/l/logging-format-interpolation/details.rst) — 'Another reasonable option is to use f-string. If you want to do that, you need to enable ``logging-format-interpolation`` and disable ``logging-fstring-interpolation``.' (fetched)
- SonarSource python S8554 (SonarSource/sonar-python python-checks/src/main/resources/org/sonar/l10n/py/rules/python/S8554.html) — 'Python performs the string formatting operation immediately, even if the log message won’t be output due to the current log level.' (fetched)
- CPython Doc/library/logging.rst §Logger Objects, Logger.debug (https://raw.githubusercontent.com/python/cpython/main/Doc/library/logging.rst) — 'The *msg* is the message format string, and the *args* are the arguments which are merged into *msg* using the string formatting operator.' and 'No % formatting operation is performed on *msg* when no *args* are supplied.' (fetched)
- CPython Doc/howto/logging.rst §Optimization (https://raw.githubusercontent.com/python/cpython/main/Doc/howto/logging.rst) — 'Formatting of message arguments is deferred until it cannot be avoided. However, computing the arguments passed to the logging method can also be expensive' and 'returns true if the event would be created by the Logger for that level of call.' (fetched)
- Google Python style guide §3.10.1 Logging (https://raw.githubusercontent.com/google/styleguide/gh-pages/pyguide.md) — 'For logging functions that expect a pattern-string (with %-placeholders) as their first argument: Always call them with a string literal (not an f-string!) as their first argument with pattern-parameters as subsequent arguments. Some logging implementations collect the unexpanded pattern-string as a queryable field.' (fetched)

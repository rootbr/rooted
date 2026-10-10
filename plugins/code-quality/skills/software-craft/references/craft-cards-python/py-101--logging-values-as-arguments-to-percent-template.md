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

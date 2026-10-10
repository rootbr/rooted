---
title: A Python raise of a new exception inside an except block writes from err, or from None when the replacement is deliberate, so the traceback reports a cause and not an error during handling
rule_id: PY-11
domain: errors
step: [implement, handle-errors, review]
applies_to: [python, exceptions]
triggers: ['^\s*raise\s+[A-Za-z_][\w.]*\(.*\)\s*(#.*)?$', '^\s*raise\s+[A-Za-z_][\w.]*\s*(#.*)?$', '^\s*except\b.*\bas\s+\w+\s*:']
scope: file
check_kind: mechanical
severity_default: minor
---

# A Python raise of a new exception inside an except block writes from err, or from None when the replacement is deliberate, so the traceback reports a cause and not an error during handling

## Thesis
A `raise` of a new exception inside an `except` block carries a `from` clause: `raise New(...) from err` sets the caught exception as the new one's cause, and `raise New(...) from None`, written when the replacement is deliberate, comes with the relevant details of the caught exception transferred into the new one. A bare `raise` and a re-raise of the caught exception itself raise no new exception and are outside the rule.

## Rationale
Python chains exceptions on its own: when a new exception is raised inside an `except` block without `from`, the exception being handled is attached to it implicitly as `__context__`, `__cause__` stays unset, and the traceback prints the first exception, then "During handling of the above exception, another exception occurred", then the new one. The `from` clause distinguishes an exception the handler raises on purpose from an error in exception handling; without it, debugging may become slightly more difficult. `raise ... from err` indicates that the new exception is a direct consequence of the caught one: the traceback prints "The above exception was the direct cause of the following exception" and the original traceback is not lost, which fits the likely case of a new exception that is a friendly re-wrapping of the first and gives a better link between the two tracebacks. `raise ... from None` disables the automatic chaining; a deliberate replacement written that way carries the relevant details itself, such as the attribute name or the text of the original exception in the new message.

## Example
```python
bad:  try:
          text = path.read_text()
      except OSError as err:
          raise ConfigError(f"cannot read {path}")
good: try:
          text = path.read_text()
      except OSError as err:
          raise ConfigError(f"cannot read {path}") from err
```

## Limits
A bare `raise` re-raises the exception being handled, and `raise err` with the handler's own name raises the caught object again; neither raises a new exception, so neither is reported. The choice between the two forms follows intent: `from err` where the new exception is a direct consequence of the caught one, `from None` where the caught exception is deliberately replaced. The rule reaches `raise` statements written in the handler's body; a function called from the handler that raises on its own is outside it.

## Validator
Grep the hunk for `raise` lines without `from`. Open the file and walk up from each one to its enclosing block: keep it when it sits in the body of an `except` or `except*` handler and not inside a `def` or `class` nested in that handler. Drop a bare `raise` and a `raise` of the handler's own `as` name. Validator question: **Does a `raise` of a new exception inside an `except` handler lack a `from` clause?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-11`, severity minor, `file`, `symbol`, `code` = the `except` header and the `raise` line quoted verbatim from the diff, `fix` = the same `raise` ending in `from err` with the handler bound `as err`, or ending in `from None` with the caught details passed into the new exception, `rationale` = without `from` the caught exception is chained only as `__context__` and the traceback presents the new one as an error during handling, not as its consequence).

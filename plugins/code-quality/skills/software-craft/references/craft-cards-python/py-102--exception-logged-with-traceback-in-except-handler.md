---
title: A Python logging call in an except handler that records the caught exception at error level uses logger.exception() or passes exc_info, not the exception only as message text or a format argument
rule_id: PY-102
domain: errors
step: [handle-errors, implement, review]
applies_to: [python, exceptions]
triggers: ['[.]error\(.*,\s*(?:e|ex|exc|err|error|exception)\s*\)', '[.]error\(\s*f[\"''].*\{(?:e|ex|exc|err|error)\b', '[.]error\(.*\b(?:str|repr)\(\s*(?:e|ex|exc|err|error)\s*\)']
scope: file
check_kind: mechanical
severity_default: minor
---

# A Python logging call in an except handler that records the caught exception at error level uses logger.exception() or passes exc_info, not the exception only as message text or a format argument

## Thesis
Inside a Python except block, a logging call that records the caught exception at ERROR level is logger.exception(...), or a call that passes exc_info as True or as the exception instance, so that the record carries the exception information with its traceback; logger.error(...) with the exception only interpolated into the message or passed as a format argument logs the exception without its traceback.

## Rationale
When exc_info does not evaluate as false, the logging module adds exception information to the record: given an exception tuple or an exception instance it uses that, and otherwise it calls sys.exc_info() to get the exception information. Logger.exception() logs at ERROR level, interprets its arguments as debug() does, and adds the exception information itself. logging.exception() logs the exception and the traceback, while logging.error() without exc_info logs only the exception, and the traceback is often useful for debugging.

## Example
```python
bad:  try:
          charge(order_id)
      except PaymentError as exc:
          logger.error("charge failed for order %s: %s", order_id, exc)
good: try:
          charge(order_id)
      except PaymentError:
          logger.exception("charge failed for order %s", order_id)
```

## Limits
A logger.error(..., exc_info=True) call inside the handler carries the traceback and satisfies the card; logger.exception() captures it without requiring exc_info=True and is the purpose-built method for logging exceptions. The card covers records at ERROR level; which level an expected, recovered failure takes is a separate question the card does not answer.

## Validator
Grep the hunk for an .error( call whose message interpolates, or whose arguments pass, a caught-exception name (e, ex, exc, err, error, exception), directly or through str() or repr(). Open the file and confirm that the call sits in the body of an except block binding that name and that it passes no exc_info. Validator question: **Does a logging call at ERROR level inside an except block record the caught exception only as message text or a format argument, without exc_info and not through logger.exception()?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-102`, severity minor, `file`, `symbol`, `code` = the logging call verbatim, `fix` = `logger.exception(...)` with the same template less the exception argument, `rationale` = the record carries the exception's text without its traceback).

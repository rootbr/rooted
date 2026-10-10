---
title: A Python __exit__ method lets the passed-in exception propagate by returning a false value and never re-raises it
rule_id: PY-20
domain: errors
step: [implement, handle-errors]
applies_to: [python, exceptions, object-oriented]
triggers: ['^\s*def\s+__exit__\s*\(', '^\s*raise\s+(exc\w*|value|e|err)\s*(#.*)?$']
scope: file
check_kind: mechanical
severity_default: minor
---

# A Python __exit__ method lets the passed-in exception propagate by returning a false value and never re-raises it

## Thesis
A Python context manager's `__exit__` that receives an exception returns a true value to suppress it and a false value to let it propagate; it does not raise the passed-in exception, either by `raise exc_value` or by a bare `raise` outside an `except` block, and it raises an exception only when its own exit work fails.

## Rationale
`__exit__` reports its decision through its return value: if an exception is supplied and the method wishes to suppress it, preventing it from being propagated, it returns a true value; otherwise the exception is processed normally upon exit from the method. Re-raising the passed-in exception is the caller's responsibility, not the method's, and raising it from `__exit__` makes the stack trace difficult to understand.

## Example
```python
bad:  def __exit__(self, exc_type, exc_value, traceback):
          self.connection.close()
          if exc_value is not None:
              raise exc_value
good: def __exit__(self, exc_type, exc_value, traceback):
          self.connection.close()
          return False
```

## Limits
When the exit work itself fails, for example closing the connection raises, `__exit__` may raise that exception. A bare `raise` inside an `except` block of `__exit__` that handles its own cleanup failure is outside the rule. A method that returns `None` by falling off its end returns a false value, and the exception is processed normally.

## Validator
Grep the hunk for `def __exit__` and open the method in the file. Name its exception parameter, the second parameter after `self` or `args[1]` when it takes `*args`. Trace every `raise` in the method: one that raises that parameter, the parameter with a new traceback attached, or a bare `raise` that sits outside an `except` clause of the method. Validator question: **Does an __exit__ method raise the exception passed to it, or execute a bare raise outside an except clause?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-20`, severity minor, `file`, `symbol`, `code` = the `raise` line in `__exit__`, `fix` = the `raise` removed and `return False` so the exception propagates normally, `rationale` = re-raising the passed-in exception is the caller's responsibility and raising it from `__exit__` makes the stack trace difficult to understand).

---
title: A function parameter annotated bool or defaulting to True or False is keyword-only after a bare *, and no call passes a True or False literal by position
rule_id: PY-46
domain: design
step: [design, implement, review]
applies_to: [python]
triggers: ['^\s*(async\s+)?def\s+\w+\s*\(.*:\s*bool\b', '^\s*(async\s+)?def\s+\w+\s*\(.*=\s*(True|False)\s*[,)]', '^\s+\w+\s*:\s*(bool|bool\s*\|\s*None|Optional\[bool\])\s*(=\s*(True|False|None))?\s*,', '\w\([^()]*,\s*(True|False)\s*[,)]']
scope: hunk
check_kind: mechanical
severity_default: minor
---

# A function parameter annotated bool or defaulting to True or False is keyword-only after a bare *, and no call passes a True or False literal by position

## Thesis
A Python function parameter annotated with `bool` or with a type that has `bool` as an evident subtype (`bool | int`, `typing.Optional[bool]`), or given a `True` or `False` default, is declared after a bare `*`, so callers must pass it by keyword; the alternatives are separate implementations for the `True` and `False` cases or a parameter that takes an `Enum`. A call passes no `True` or `False` literal as a positional argument.

## Rationale
A Python parameter list has three kinds of parameter, positional-only, positional-or-keyword and keyword-only, and where neither `/` nor `*` is present every argument may be passed by position or by keyword, so `send(msg, True)` binds the flag without naming it. Calling a function with boolean positional arguments is confusing, as the meaning of the boolean value is not clear to the caller and to future readers of the code; a boolean also limits the function to only two possible behaviors, which makes it difficult to extend. A `*` placed in the parameter list just before the first keyword-only parameter makes the parameters after it keyword-only, so they must be passed by keyword argument; keyword-only fits parameters whose names have meaning and prevents callers from relying on the position of the argument.

## Example
```python
bad:  def send(message: str, retry: bool = False) -> None: ...
      send(msg, True)
good: def send(message: str, *, retry: bool = False) -> None: ...
      send(msg, retry=True)
```

## Limits
For a `bool`-annotated parameter, dunder methods that define operators, setters and `@override` definitions are exempt; for a parameter with a boolean default, methods decorated with `@typing.override` are exempt, since changing the signature of a subclass method that overrides a superclass method may cause type checkers to complain. Some calls are allowed by default, and a project extends the allowed calls through the `lint.flake8-boolean-trap.extend-allowed-calls` option; a literal passed positionally to an allowed call passes.

## Validator
Grep the hunk for `def` signatures and parameter lines carrying a `bool` annotation (`bool`, `bool | ...`, `Optional[bool]`) or a `True`/`False` default, and for calls with a `True` or `False` literal among the positional arguments. For each definition, open the whole signature and check whether the parameter stands before a bare `*` or `*args`; skip dunder methods that define operators, property setters and `@override` definitions. For each call, confirm the literal carries no `name=` and the callee is outside the project's allowed calls. Validator question: **Does the hunk declare a `bool`-annotated or `True`/`False`-defaulted parameter that callers can fill by position, or pass a `True` or `False` literal by position in a call?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-46`, severity minor, `file`, `symbol`, `code` = the `def` line or the call with the positional `True`/`False`, verbatim, `fix` = the signature with a bare `*` before the flag and the call naming it, such as `def send(message: str, *, retry: bool = False)` with `send(msg, retry=True)`, `rationale` = the flag a caller binds by position without naming it).

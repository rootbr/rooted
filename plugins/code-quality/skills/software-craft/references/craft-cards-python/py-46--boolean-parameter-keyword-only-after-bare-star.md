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

## Source
- Ruff FBT001 boolean-type-hint-positional-argument (astral-sh/ruff crates/ruff_linter/src/rules/flake8_boolean_trap/rules/boolean_type_hint_positional_argument.rs) — 'Calling a function with boolean positional arguments is confusing as the meaning of the boolean value is not clear to the caller and to future readers of the code.' (fetched)
- Ruff FBT001 boolean-type-hint-positional-argument (astral-sh/ruff crates/ruff_linter/src/rules/flake8_boolean_trap/rules/boolean_type_hint_positional_argument.rs) — 'a type hint containing `bool` as an evident subtype - e.g. `bool`, `bool | int`, `typing.Optional[bool]`, etc.' (fetched)
- Ruff FBT001 boolean-type-hint-positional-argument (astral-sh/ruff crates/ruff_linter/src/rules/flake8_boolean_trap/rules/boolean_type_hint_positional_argument.rs) — 'The use of a boolean will also limit the function to only two possible behaviors, which makes the function difficult to extend in the future.' (fetched)
- Ruff FBT001 boolean-type-hint-positional-argument (astral-sh/ruff crates/ruff_linter/src/rules/flake8_boolean_trap/rules/boolean_type_hint_positional_argument.rs) — 'Instead, consider refactoring into separate implementations for the `True` and `False` cases, using an `Enum`, or making the argument a keyword-only argument, to force callers to be explicit when providing the argument.' (fetched)
- Ruff FBT001 boolean-type-hint-positional-argument (astral-sh/ruff crates/ruff_linter/src/rules/flake8_boolean_trap/rules/boolean_type_hint_positional_argument.rs) — 'Dunder methods that define operators are exempt from this rule, as are setters and [`@override`][override] definitions.' (fetched)
- Ruff FBT002 boolean-default-value-positional-argument (astral-sh/ruff crates/ruff_linter/src/rules/flake8_boolean_trap/rules/boolean_default_value_positional_argument.rs) — 'Checks for the use of boolean positional arguments in function definitions, as determined by the presence of a boolean default value.' (fetched)
- Ruff FBT002 boolean-default-value-positional-argument (astral-sh/ruff crates/ruff_linter/src/rules/flake8_boolean_trap/rules/boolean_default_value_positional_argument.rs) — 'since changing the signature of a subclass method that overrides a superclass method may cause type checkers to complain' (fetched)
- Ruff FBT003 boolean-positional-value-in-call (astral-sh/ruff crates/ruff_linter/src/rules/flake8_boolean_trap/rules/boolean_positional_value_in_call.rs) — 'Checks for boolean positional arguments in function calls.' (fetched)
- Ruff FBT003 boolean-positional-value-in-call (astral-sh/ruff crates/ruff_linter/src/rules/flake8_boolean_trap/rules/boolean_positional_value_in_call.rs) — 'Some functions are whitelisted by default. To extend the list of allowed calls configure the [`lint.flake8-boolean-trap.extend-allowed-calls`] option.' (fetched)
- CPython Doc/tutorial/controlflow.rst §Special parameters (python/cpython Doc/tutorial/controlflow.rst) — 'positional-only, positional-or-keyword, and keyword-only' (fetched)
- CPython Doc/tutorial/controlflow.rst §Positional-or-Keyword Arguments (python/cpython Doc/tutorial/controlflow.rst) — 'If ``/`` and ``*`` are not present in the function definition, arguments may be passed to a function by position or by keyword.' (fetched)
- CPython Doc/tutorial/controlflow.rst §Keyword-Only Arguments (python/cpython Doc/tutorial/controlflow.rst) — 'To mark parameters as *keyword-only*, indicating the parameters must be passed by keyword argument, place an ``*`` in the arguments list just before the first *keyword-only* parameter.' (fetched)
- CPython Doc/tutorial/controlflow.rst §Recap (python/cpython Doc/tutorial/controlflow.rst) — 'Use keyword-only when names have meaning and the function definition is more understandable by being explicit with names or you want to prevent users relying on the position of the argument being passed.' (fetched)

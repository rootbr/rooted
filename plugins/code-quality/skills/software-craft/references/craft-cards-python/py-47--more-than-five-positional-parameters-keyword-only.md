---
title: A Python function with more than five positional parameters takes the ones whose role a call does not make plain as keyword-only after a bare *
rule_id: PY-47
domain: design
step: [design, implement, refactor, review]
applies_to: [python]
triggers: ['^\s*(async\s+)?def\s+\w+\s*\(([^*/)]*,){5,}', 'signal:many_parameters']
scope: hunk
check_kind: mechanical
severity_default: minor
---

# A Python function with more than five positional parameters takes the ones whose role a call does not make plain as keyword-only after a bare *

## Thesis
A Python function definition with more than five positional parameters, the default limit of Ruff's `max-positional-args` option, places a bare `*` before the parameters whose use at the call site is not self-evident, so callers must pass them by keyword; the alternatives are grouping related arguments into an object or splitting the function into smaller functions with fewer arguments.

## Rationale
A Python parameter list has three kinds of parameter, positional-only, positional-or-keyword and keyword-only, and where neither `/` nor `*` is present every argument may be passed by position or by keyword, so a call may fill every parameter with a bare value. Functions with many arguments are harder to understand, maintain and call, and especially so with many positional arguments, as providing arguments positionally is more error-prone and less clear to readers than providing them by name; for almost all interfaces, comprehensibility suffers beyond a handful of arguments. Positional arguments work well where the use cases are self-evident, such as `assertEqual(first, second, "assert msg")` or `zip(fruits, vegetables)`. A `*` placed just before the first keyword-only parameter makes the parameters after it keyword-only, so they must be passed by keyword argument.

## Example
```python
bad:  def drag(velocity, area, density, coefficient, temperature, altitude): ...
      drag(12.0, 0.5, 1.2, 0.3, 288.0, 100.0)
good: def drag(velocity, *, area, density, coefficient, temperature, altitude): ...
      drag(12.0, area=0.5, density=1.2, coefficient=0.3, temperature=288.0, altitude=100.0)
```

## Limits
Four or more positional parameters make sense where the call uses a very well-known and well-established convention, such as `rgba(1.0, 0.5, 0.3, 1.0)`, where using keywords all the time would be a waste of time. The limit of five is a default that a project configures through `lint.pylint.max-positional-args`. Methods decorated with `@typing.override` are exempt, since changing the signature of a subclass method may cause type checkers to complain if it means that the method incompatibly overrides a method defined on a superclass.

## Validator
Grep the hunk for `def` signatures with five or more commas before any `*`, `/` or closing parenthesis, and take the many-parameters signal. Open the whole signature, which may span lines, and count the parameters before the first bare `*` or `*args`, leaving out the `self` or `cls` of a method or classmethod; skip `@override` and `@overload` definitions. Compare the count with five, or with the project's configured `max-positional-args`. Validator question: **Does the hunk add or widen a function definition with more than five positional parameters (or more than the project's configured limit), not counting `self` or `cls`, outside `@override` and `@overload` definitions and outside a well-established positional convention such as an RGBA quadruple?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-47`, severity minor, `file`, `symbol`, `code` = the `def` line with its positional parameters, verbatim, `fix` = the signature with a bare `*` after the parameters whose role a call makes plain and the calls naming the rest, such as `def drag(velocity, *, area, density, coefficient, temperature, altitude)`, `rationale` = the count of positional parameters against the limit of five).

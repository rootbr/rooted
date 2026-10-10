---
title: A function bound to a name is written as a def statement, never as a lambda expression assigned to that name
rule_id: PY-43
domain: design
step: [implement, refactor, review]
applies_to: [python]
triggers: ['^\s*[\w.]+\s*(:\s*[^=]+)?=\s*lambda\b', '^\s*\w+\s*:\s*Callable\[.*\]\s*=\s*lambda\b']
scope: hunk
check_kind: mechanical
severity_default: minor
---

# A function bound to a name is written as a def statement, never as a lambda expression assigned to that name

## Thesis
A Python function that is bound to a name is defined with a def statement, `def f(x): return 2*x`, in place of an assignment statement that binds a lambda expression directly to the name, `f = lambda x: 2*x`.

## Rationale
A def statement gives the resulting function object its own name, `f`, while a lambda's function object carries the generic name `<lambda>` whatever variable it is assigned to; the def name is more useful for tracebacks and string representations, and a traceback through a lambda provides no specific name, which can make errors more challenging to identify and troubleshoot. A lambda's body may contain only an expression, and a lambda supports no docstring. The sole benefit a lambda expression offers over a def statement is that it can be embedded inside a larger expression, and an assignment statement that binds the lambda to a name eliminates that benefit.

## Example
```python
bad:  normalize: Callable[[str], str] = lambda text: text.strip().lower()
good: def normalize(text: str) -> str:
          return text.strip().lower()
```

## Limits
The rule covers an assignment statement that binds a lambda expression directly to a name; a lambda embedded inside a larger expression, such as `sorted(rows, key=lambda row: row.date)`, keeps the benefit a lambda offers and is outside it. Converting the assignment into a def changes an observable property of the callable, its name, from `<lambda>` to the name of the assigned variable, so code that relies on function metadata, such as logging, registration or introspection, may behave differently after the fix.

## Validator
Grep the hunk for `= lambda`. Check that the assignment's target is a single name, with or without an annotation such as `Callable[[str], str]`, and that the right-hand side is the lambda itself rather than a larger expression containing it (a call, a container literal, a conditional expression). Search the file for code that reads the function's `__name__` or registers it by name, and mention it in the fix. Validator question: **Does an assignment statement bind a lambda expression directly to a single name?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-43`, severity minor, `file`, `symbol` = the assigned name, `code` = the `name = lambda ...` line verbatim from the diff, `fix` = `def name(params):` with `return <expression>` as its body, any annotation carried onto the parameters and return, `rationale` = names that the function object is named `<lambda>` in tracebacks and string representations, carries no docstring, and that the assignment eliminates the one benefit a lambda has, being embedded inside a larger expression).

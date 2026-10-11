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

## Source
- PEP 8 §Programming Recommendations (https://raw.githubusercontent.com/python/peps/main/peps/pep-0008.rst) — 'Always use a def statement instead of an assignment statement that binds a lambda expression directly to an identifier:' (fetched)
- PEP 8 §Programming Recommendations (https://raw.githubusercontent.com/python/peps/main/peps/pep-0008.rst) — 'This is more useful for tracebacks and string representations in general.' (fetched)
- PEP 8 §Programming Recommendations (https://raw.githubusercontent.com/python/peps/main/peps/pep-0008.rst) — 'The use of the assignment statement eliminates the sole benefit a lambda expression can offer over an explicit def statement (i.e. that it can be embedded inside a larger expression)' (fetched)
- Ruff E731 lambda-assignment (astral-sh/ruff crates/ruff_linter/src/rules/pycodestyle/rules/lambda_assignment.rs) — 'Using a `def` statement leads to better tracebacks, and the assignment itself negates the primary benefit of using a `lambda` expression (i.e., that it can be embedded inside another expression).' (fetched)
- Ruff E731 lambda-assignment (astral-sh/ruff crates/ruff_linter/src/rules/pycodestyle/rules/lambda_assignment.rs) — 'This fix is marked as unsafe because converting a lambda assignment into a function definition changes observable properties of the callable.' (fetched)
- Ruff E731 lambda-assignment (astral-sh/ruff crates/ruff_linter/src/rules/pycodestyle/rules/lambda_assignment.rs) — 'In particular, a lambda function has the name `"<lambda>"`, while the generated function uses the name of the assigned variable.' (fetched)
- Ruff E731 lambda-assignment (astral-sh/ruff crates/ruff_linter/src/rules/pycodestyle/rules/lambda_assignment.rs) — 'Code that relies on function metadata, such as logging, registration, or introspection, may therefore behave differently after the fix.' (fetched)
- Pylint unnecessary-lambda-assignment (C3001) message description (pylint-dev/pylint doc/data/messages/u/unnecessary-lambda-assignment/bad.py) — 'Used when a lambda expression is assigned to variable rather than defining a standard function with the "def" keyword.' (fetched)
- SonarSource python S6661 (SonarSource/sonar-python python-checks/src/main/resources/org/sonar/l10n/py/rules/python/S6661.html) — 'Lambdas do not support docstrings' (fetched)
- SonarSource python S6661 (SonarSource/sonar-python python-checks/src/main/resources/org/sonar/l10n/py/rules/python/S6661.html) — 'Lambdas are anonymous functions, which means that when an error occurs during execution, the traceback will not provide a specific name associated with the lambda function. This can make it more challenging to identify and troubleshoot errors.' (fetched)
- Google Python Style Guide §2.10.3 Lambda Functions Cons (https://raw.githubusercontent.com/google/styleguide/gh-pages/pyguide.md) — 'Expressiveness is limited because the function may only contain an expression.' (fetched)

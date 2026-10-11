---
title: A Python lambda or nested function created in a loop and called after its iteration ends binds the loop variable through a default argument or functools.partial
rule_id: PY-04
domain: code
step: [implement, review]
applies_to: [python, functional]
triggers: ['lambda[^:]*:', '^(?: {8,}|\t{2,})def\s+\w+\(', '[.]append\(\s*lambda\b', '\[\s*lambda\b.*\bfor\s+\w+\s+in\b']
scope: hunk
check_kind: semantic
severity_default: major
---

# A Python lambda or nested function created in a loop and called after its iteration ends binds the loop variable through a default argument or functools.partial

## Thesis
A Python lambda or nested function defined in a loop, including the for clause of a comprehension, and called in a later iteration or after the loop finishes, such as a callback stored in a list or registered for later, binds each variable it reads that the loop redefines, such as the loop variable, at definition time through a default argument (`lambda item=item: ...`) or `functools.partial`, or receives the value as an argument when it is called.

## Rationale
A variable that a function reads from an enclosing scope is not local to the function: it is accessed when the function is called, not when it is defined. A function defined in a loop and called in another iteration or after the loop finishes therefore sees the variable's last value instead of the value of the iteration where the function was defined, and all closures created by the loop use the same value for the closed-over variable. A comprehension's for clauses work as nested blocks, so a lambda created in a comprehension reads the comprehension's loop variable in the same way. A default value is executed only once, when the function is defined, so the parameter keeps the iteration's value even when the variable is reassigned in following iterations; `functools.partial` is the other way to bind the loop variable, and passing the variable as an argument when the function is called removes the dependence on the enclosing variable.

## Example
```python
bad:  for item in items:
          callbacks.append(lambda: process(item))
good: for item in items:
          callbacks.append(lambda item=item: process(item))
      for item in items:
          callbacks.append(functools.partial(process, item))
```

## Limits
A function called only within the iteration that defined it reads that iteration's value; the defect needs a call in another iteration or after the loop finishes. A lambda passed to map() in the loop is a later call when the iterator is consumed after the iteration, because map returns an iterator and only executes the lambda when required. The stricter position reports every function or lambda that references a variable defined in an enclosing loop and is not directly called in the same loop, because capturing it increases the risk of introducing a bug when the code is refactored or when dependencies are updated; this card's finding needs the later call to be shown.

## Validator
Find each lambda and def in the hunk that sits inside a for or while loop or a comprehension. List the names it reads that the loop binds or the loop body reassigns and that are neither its parameters nor bound by a default argument or functools.partial. Trace where the function goes: appended to a list, stored in a dict or an attribute, registered as a callback or handler, returned, yielded, passed to map(), filter() or an executor, or called only inside the iteration. Validator question: **Does a lambda or nested function defined in a loop or comprehension read a variable the loop redefines, without a default argument or functools.partial binding it, and get called in a later iteration or after the loop finishes?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-04`, severity major, `file`, `symbol`, `code` = the lambda or def line and the line that stores, registers or returns it, `fix` = the variable bound at definition, such as `lambda item=item: process(item)` or `functools.partial(process, item)`, `rationale` = the function reads the loop variable when it is called, so every closure sees the variable's last value).

## Source
- Python programming FAQ §Why do lambdas defined in a loop with different values all return the same result? (python/cpython Doc/faq/programming.rst) — 'This happens because ``x`` is not local to the lambdas, but is defined in the outer scope, and it is accessed when the lambda is called --- not when it is defined.' (fetched)
- Python programming FAQ §Why do lambdas defined in a loop with different values all return the same result? (python/cpython Doc/faq/programming.rst) — 'In order to avoid this, you need to save the values in variables local to the lambdas, so that they don't rely on the value of the global ``x``' (fetched)
- Python language reference §Displays for lists, sets and dictionaries (https://docs.python.org/3/reference/expressions.html#displays-for-lists-sets-and-dictionaries) — 'The elements of the new container are those that would be produced by considering each of the for or if clauses a block, nesting from left to right' (fetched)
- Ruff B023 function-uses-loop-variable (astral-sh/ruff crates/ruff_linter/src/rules/flake8_bugbear/rules/function_uses_loop_variable.rs) — 'The loop variable is not bound in the function definition, so it will always have the value it had in the last iteration when the function is called. Instead, consider using a default argument to bind the loop variable at function definition time. Or, use `functools.partial`.' (fetched)
- flake8-bugbear B023 (PyCQA/flake8-bugbear README.rst) — 'Functions defined inside a loop must not use variables redefined in the loop, because `late-binding closures are a classic gotcha' (fetched)
- Pylint cell-var-from-loop (W0640) message description (https://pylint.readthedocs.io/en/stable/user_guide/messages/warning/cell-var-from-loop.html) — 'A variable used in a closure is defined in a loop. This will result in all closures using the same value for the closed-over variable.' (fetched)
- SonarSource python S1515 (SonarSource/sonar-python python-checks/src/main/resources/org/sonar/l10n/py/rules/python/S1515.html) — 'If the function is called in another iteration or after the loop finishes, it will see the variables' last value instead of seeing the values corresponding to the iteration where the function was defined.' (fetched)
- SonarSource python S1515 (SonarSource/sonar-python python-checks/src/main/resources/org/sonar/l10n/py/rules/python/S1515.html) — 'Default values are only executed once, when the function is defined, which means that the parameter’s value will remain the same even when the variable is reassigned in following iterations. Another solution is to pass the variable as an argument to the function/lambda when it is called.' (fetched)
- SonarSource python S1515 (SonarSource/sonar-python python-checks/src/main/resources/org/sonar/l10n/py/rules/python/S1515.html) — 'This rule raises an issue when a function or lambda references a variable defined in an enclosing loop.' (fetched)
- SonarSource python S1515 (SonarSource/sonar-python python-checks/src/main/resources/org/sonar/l10n/py/rules/python/S1515.html) — 'No issue will be raised if the function or lambda is directly called in the same loop.' (fetched)
- SonarSource python S1515 (SonarSource/sonar-python python-checks/src/main/resources/org/sonar/l10n/py/rules/python/S1515.html) — 'it increases the risk of introducing a bug when the code is refactored or when dependencies are updated.' (fetched)
- SonarSource python S1515 (SonarSource/sonar-python python-checks/src/main/resources/org/sonar/l10n/py/rules/python/S1515.html) — 'It now returns an iterator and only executes the lambda when required.' (fetched)

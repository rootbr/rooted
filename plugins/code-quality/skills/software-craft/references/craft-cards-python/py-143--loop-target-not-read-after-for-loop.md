---
title: Code after a Python for loop never reads a name that only the loop target binds, because an empty iterable leaves that name unassigned
rule_id: PY-143
domain: code
step: [implement, review]
applies_to: [python]
triggers: ['^\s*for\s+[A-Za-z_][\w, ()]*\s+in\s+.+:\s*(#.*)?$', '^\s*break\s*(#.*)?$']
scope: file
check_kind: semantic
severity_default: major
---

# Code after a Python for loop never reads a name that only the loop target binds, because an empty iterable leaves that name unassigned

## Thesis
Code that runs after a Python for loop reads a name bound by the loop's target list only when that name is also bound on the path where the iterable is empty. A value the code needs after the loop is returned inside the loop body, or assigned there to a name bound before the loop, and the code after the loop gives an explicit result for an empty iterable.

## Rationale
The names in a for loop's target list are not deleted when the loop finishes, but if the sequence is empty the loop never assigns them. A read of such a name after the loop therefore succeeds on every input that yields an item and fails on an empty one. When the name is not found at all, NameError is raised; in a function, where the name is a local variable not yet bound at the point of use, UnboundLocalError, a subclass of NameError, is raised. After a loop that breaks at a match, the same read on a non-empty input without a match gets the last item, because the loop leaves its target bound to the item it assigned last. Returning at the match, or binding the result before the loop, makes the value defined on every path.

## Example
```python
bad:  for user in users:
          if user.active:
              break
      return user
good: for user in users:
          if user.active:
              return user
      return None
```

## Limits
A name that the code also binds before the loop, such as a result initialised to None, is bound on every path and is outside the rule. A read placed after a loop whose else clause returns, raises or binds the name is safe as well, because the else suite runs whenever the loop ends by exhausting its iterator and a break skips it. The target names of a comprehension are outside the rule: a comprehension runs in a separate nested scope, so the names its target list assigns do not reach the enclosing scope.

## Validator
List the names that the target list of each for statement in the hunk binds. Open the enclosing function, or the module for a top-level loop, and find every read of those names after the loop statement. For each read, trace the path on which the iterable is empty: check whether the name is assigned before the loop, and whether the loop's else clause returns, raises or assigns it. Validator question: **Does code after a for loop read a name that, when the iterable is empty, nothing but the loop's target list would have bound?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-143`, severity major, `file`, `symbol`, `code` = the for header and the read of its target after the loop, quoted verbatim from the diff, `fix` = the value returned or assigned inside the loop and an explicit result after it, such as `return user` at the match and `return None` after the loop, `rationale` = the loop target, the read after the loop and the NameError or UnboundLocalError an empty iterable raises at that read).

## Source
- CPython Doc/reference/compound_stmts.rst §The for statement (https://docs.python.org/3/reference/compound_stmts.html) — 'Names in the target list are not deleted when the loop is finished, but if the sequence is empty, they will not have been assigned to at all by the loop.'; 'When the iterator is exhausted'; 'the suite in the else clause, if present, is executed, and the loop terminates.'; 'statement executed in the first suite terminates the loop without executing the' (fetched)
- CPython Doc/reference/executionmodel.rst §Resolution of names (https://raw.githubusercontent.com/python/cpython/main/Doc/reference/executionmodel.rst) — 'When a name is not found at all, a :exc:`NameError` exception is raised.'; 'If the current scope is a function scope, and the name refers to a local variable that has not yet been bound to a value at the point where the name is used, an :exc:`UnboundLocalError` exception is raised.'; ':exc:`UnboundLocalError` is a subclass of :exc:`NameError`.' (fetched)
- CPython Doc/reference/expressions.rst §Comprehensions (https://raw.githubusercontent.com/python/cpython/main/Doc/reference/expressions.rst) — 'the comprehension is executed in a separate implicitly nested scope.' (fetched)
- Pylint undefined-loop-variable (W0631) (pylint-dev/pylint pylint/checkers/variables.py, message W0631) — 'Used when a loop variable (i.e. defined by a for loop or a list comprehension or a generator expression) is used outside the loop.' (fetched)
- Pylint undefined-loop-variable (W0631) example (pylint-dev/pylint doc/data/messages/u/undefined-loop-variable/bad.py) — 'return x  # [undefined-loop-variable]' (fetched)
- Caveat: the message description also names comprehension and generator-expression variables, which the language reference places in a nested scope of their own; the rule carries the for statement only.

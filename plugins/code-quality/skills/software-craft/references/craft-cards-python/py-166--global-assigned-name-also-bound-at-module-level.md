---
title: A name a Python function declares global and assigns is also bound at module level
rule_id: PY-166
domain: design
step: [implement, review]
applies_to: [python]
triggers: ['^\s+global\s+\w+']
scope: file
check_kind: mechanical
severity_default: minor
---

# A name a Python function declares global and assigns is also bound at module level

## Thesis
A name that a Python function declares `global` and assigns is also bound by a module-level statement of the same module — an assignment, an import, or a `def` or `class` statement — as `TOMATO = "black cherry"` is bound beside `update_tomato`.

## Rationale
A `global` statement makes all uses of the listed names in the function refer to their bindings in the top-level namespace, where the module's global namespace is searched first and the builtins namespace next; if the names are found in neither, new variables are created in the global namespace. Without a module-level binding, the variable therefore comes into being only when the function assigns it, and code that reads the name before then finds it nowhere and raises NameError. A module-level binding puts the name in the global namespace, the namespace searched first when the name is resolved in the top-level namespace.

## Example
```python
bad:  def update_tomato():
          global TOMATO
          TOMATO = "moneymaker"
good: TOMATO = "black cherry"
      def update_tomato():
          global TOMATO
          TOMATO = "moneymaker"
```

## Limits
A `global` statement whose name the function only reads and never assigns is outside this rule. Any module-level statement that binds the name satisfies it: a module-level assignment, a `def` or `class` statement at module level, or an import.

## Validator
Grep the hunk for `global` statements inside a function and list each name the function then binds: an assignment, an augmented assignment, a `for` target, a `with ... as` target, an import, a `def` or a `class`. For each such name, open the whole file and look for a binding at module scope — an assignment or annotated assignment with a value, an import, or a `def` or `class` statement, at column 0 or under a module-level `if`, `try` or `with`. Validator question: **Does a function in the hunk assign a name it declares `global` that no module-level statement of the file binds?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-166`, severity minor, `file`, `symbol`, `code` = the `global` statement and the assignment it governs, verbatim, `fix` = a module-level binding of the name with its initial value beside the function, as in `TOMATO = "black cherry"`, `rationale` = without it the variable exists only after the function runs and a read before then raises NameError).

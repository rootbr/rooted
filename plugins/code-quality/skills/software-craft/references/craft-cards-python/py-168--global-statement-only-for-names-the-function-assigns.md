---
title: A Python global statement names only variables its function assigns and never stands at module level
rule_id: PY-168
domain: design
step: [implement, refactor]
applies_to: [python]
triggers: ['^\s+global\s+\w+', '^global\s+\w+']
scope: file
check_kind: mechanical
severity_default: suggestion
---

# A Python global statement names only variables its function assigns and never stands at module level

## Thesis
A `global` statement in a Python function lists only names that the function assigns, and the top level of a module holds no `global` statement. A function that reads a module variable, or modifies its object without an assignment, does so without `global`.

## Rationale
The `global` statement causes the listed identifiers to be interpreted as globals, and it applies to the entire current scope. Inside a function it is needed for assignment: assigning to a global variable is impossible without it, while free variables may refer to globals without being declared global. A name used in a code block is resolved using the nearest enclosing scope. `global` is what allows an inner scope to modify a variable declared in the outer scope; when a module variable is modified in a function, the keyword is required only if there is an assignment operation in that function, so a declaration for a name the function never assigns is not needed. At the module level all variables are global, so a `global` statement there has no effect and is redundant.

## Example
```python
bad:  global DEBUG
      DEBUG = False
      def report():
          global DEBUG
          if DEBUG:
              print("report called")
good: DEBUG = False
      def report():
          if DEBUG:
              print("report called")
```

## Limits
A function that assigns a listed name anywhere in its body needs the declaration, since the statement applies to the entire scope and assigning to a global variable is impossible without it. A nested function whose enclosing function binds the same name would resolve a read to that enclosing scope; there `global` causes the name to be interpreted as the module's global, so the declaration has an effect and is outside the rule. A `global` statement in a class body applies to that class definition and causes the listed names to be interpreted as globals there; the module-level half of the rule reaches only the top level of a module.

## Validator
Grep the hunk for `global` statements. For one at the top level of a module, the answer is yes. For one inside a function, take each listed name and search that function's own body for a binding of it: a plain or augmented assignment, a `for` or `with ... as` target, `:=`, `del`, or an `import`, `def` or `class` statement for that name; a binding inside a nested `def`, `lambda` or class body belongs to that inner scope and does not count. Before flagging a name the function only reads, open the enclosing functions: when one of them binds the same name, the declaration redirects the read to the module and stays. Validator question: **Does the `global` statement stand at the top level of a module, or list a name that its function never binds and that no enclosing function binds?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-168`, severity suggestion, `file`, `symbol`, `code` = the `global` statement verbatim, `fix` = the statement removed, or the names the function never assigns dropped from its list, `rationale` = that a function reads a module variable without `global` and that at module level every variable is already global).

## Source
- Ruff PLW0602 global-variable-not-assigned (astral-sh/ruff crates/ruff_linter/src/rules/pylint/rules/global_variable_not_assigned.rs) — 'The `global` keyword allows an inner scope to modify a variable declared in the outer scope. If the variable is not modified within the inner scope, there is no need to use `global`.' (fetched)
- Pylint global-variable-not-assigned (W0602) (pylint-dev/pylint pylint/checkers/variables.py) — "When a variable defined in the global scope is modified in an inner scope, the 'global' keyword is required in the inner scope only if there is an assignment operation done in the inner scope." (fetched)
- Ruff PLW0604 global-at-module-level (astral-sh/ruff crates/ruff_linter/src/rules/pylint/rules/global_at_module_level.rs) — 'At the module level, all names are global by default, so the `global` keyword is redundant.' (fetched)
- Pylint global-at-module-level (W0604) (pylint-dev/pylint pylint/checkers/variables.py) — 'Used when you use the "global" statement at the module level since it has no effect.' (fetched)
- CPython Doc/reference/simple_stmts.rst §The global statement (https://raw.githubusercontent.com/python/cpython/main/Doc/reference/simple_stmts.rst) — 'The :keyword:`global` statement causes the listed identifiers to be interpreted as globals. It would be impossible to assign to a global variable without :keyword:`!global`, although free variables may refer to globals without being declared global.' (fetched)
- CPython Doc/reference/simple_stmts.rst §The global statement (https://raw.githubusercontent.com/python/cpython/main/Doc/reference/simple_stmts.rst) — 'The :keyword:`!global` statement applies to the entire current scope (module, function body or class definition).' (fetched)
- CPython Doc/reference/simple_stmts.rst §The global statement (https://raw.githubusercontent.com/python/cpython/main/Doc/reference/simple_stmts.rst) — 'At the module level, all variables are global, so a :keyword:`!global` statement has no effect.' (fetched)
- CPython Doc/reference/executionmodel.rst §Resolution of names (https://raw.githubusercontent.com/python/cpython/main/Doc/reference/executionmodel.rst) — 'When a name is used in a code block, it is resolved using the nearest enclosing scope.' (fetched)
- Caveat: the Pylint message texts are quoted from the checker source, since the messages have no details.rst page upstream.

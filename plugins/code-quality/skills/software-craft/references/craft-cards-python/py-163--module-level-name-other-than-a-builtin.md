---
title: A Python module-level assignment, def, class, import or global-declared name does not take the name of a builtin such as id, list, type, map or print
rule_id: PY-163
domain: design
step: [implement, refactor, review]
applies_to: [python]
triggers: ['^(id|type|list|dict|set|str|int|float|bytes|tuple|input|filter|map|max|min|sum|any|all|open|format|hash|len|iter|next|object|vars|dir|range|zip|print|compile|exec|eval|sorted|round|help)\s*(:[^=]+)?=(?!=)', '^(async\s+)?def\s+(id|type|list|dict|set|str|int|float|bytes|tuple|input|filter|map|max|min|sum|any|all|open|format|hash|len|iter|next|object|vars|dir|range|zip|print|compile|exec|eval|sorted|round|help)\s*\(', '^class\s+(id|type|list|dict|set|str|int|float|bytes|tuple|input|filter|map|max|min|sum|any|all|open|format|hash|len|iter|next|object|vars|dir|range|zip|print|compile|exec|eval|sorted|round|help)\b', '^from\s+\S+\s+import\s+(.*,\s*)?(id|type|list|dict|set|str|int|float|bytes|tuple|input|filter|map|max|min|sum|any|all|open|format|hash|len|iter|next|object|vars|dir|range|zip|print|compile|exec|eval|sorted|round|help)\s*(,|$)', '^import\s+\S+\s+as\s+(id|type|list|dict|set|str|int|float|bytes|tuple|input|filter|map|max|min|sum|any|all|open|format|hash|len|iter|next|object|vars|dir|range|zip|print|compile|exec|eval|sorted|round|help)\s*$', '^\s+global\s+(.*,\s*)?(id|type|list|dict|set|str|int|float|bytes|tuple|input|filter|map|max|min|sum|any|all|open|format|hash|len|iter|next|object|vars|dir|range|zip|print|compile|exec|eval|sorted|round|help)\b']
scope: file
check_kind: mechanical
severity_default: minor
---

# A Python module-level assignment, def, class, import or global-declared name does not take the name of a builtin such as id, list, type, map or print

## Thesis
A Python binding at module scope — an assignment, a `def` or `class` statement, an import or import alias, or a name a function declares `global` and assigns — uses a name other than that of a builtin such as `id`, `list`, `type`, `filter`, `map`, `open` or `print`.

## Rationale
The builtins namespace is the namespace of the `builtins` module, and names are resolved in the top-level namespace by searching the global namespace, the namespace of the module containing the code, first and the builtins namespace next. Once a module binds `print`, or a function declares `global len` and assigns `len = 1`, a lookup of that name that reaches the top-level namespace finds the module's binding, not the builtin. Shadowing a builtin at the global scope obscures its behaviour throughout the entire module and increases the risk of subtle bugs when the builtin is needed elsewhere, and readers may mistake the binding for the builtin and vice versa. An import alias such as `rich_print`, or access through the module as `rich.print`, leaves the builtin's name unbound in the module.

## Example
```python
bad:  from rich import print
      print("Some message")
good: from rich import print as rich_print
      rich_print("Some message")
```

## Limits
Positions split on bindings outside module scope. One position reports every binding that reuses a builtin name — variables, function arguments, class attributes referenced in the class scope, imports and lambda arguments — because readers may mistake the binding for the builtin; the other discourages shadowing only at the global scope and accepts local redefinitions because their impact is confined to a specific scope. The separating condition is where the binding lives: a binding at module level, or through a `global` declaration, obscures the builtin throughout the entire module and is reported whether or not current code calls the builtin; a binding confined to one function's scope, a parameter or a lambda argument is outside this rule, and so is a method or class attribute, which the every-scope position reports only when it is referenced from within the class scope. A project may mark builtins as exceptions in the `lint.flake8-builtins.ignorelist` configuration option; the `allowed-redefined-builtins` option of Pylint is not effective for redefinitions at the module level or for global variables.

## Validator
Grep the hunk for a module-scope binding whose name is a builtin's: an assignment or annotated assignment at column 0, a `def` or `class` statement at column 0, a `from ... import name` or `import ... as name`, and a `global name` inside a function that the function then assigns; a binding indented under a module-level `if`, `try`, `for` or `with` is still at module scope. Check each name against the names of the `builtins` module, open the file to confirm the binding is not inside a function or class body, and skip a name the project lists in `lint.flake8-builtins.ignorelist`. Validator question: **Does the hunk bind a builtin's name at module scope, directly or through a `global` declaration that a function assigns?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-163`, severity minor, `file`, `symbol`, `code` = the module-level binding, or the `global` statement and its assignment, verbatim, `fix` = the binding under a name that is not a builtin's, as in `from rich import print as rich_print`, or the module accessed by its name, as in `rich.print("Some message")`, `rationale` = the module's global namespace is searched before the builtins namespace, so the binding hides the builtin throughout the module).

## Source
- Pylint redefined-builtin (W0622) (pylint-dev/pylint doc/data/messages/r/redefined-builtin/details.rst) — 'Shadowing built-ins at the global scope is discouraged because it obscures their behavior throughout the entire module, increasing the risk of subtle bugs when the built-in is needed elsewhere. In contrast, local redefinitions are acceptable as their impact is confined to a specific scope, reducing unintended side effects and simplifying debugging.'; 'However, this option is not effective for redefinitions at the module level or for global variables.'; 'len = 1  # Shadows the built-in `len`' (fetched)
- CPython Doc/reference/executionmodel.rst §Resolution of names (python/cpython Doc/reference/executionmodel.rst) — 'Names are resolved in the top-level namespace by searching the global namespace, i.e. the namespace of the module containing the code block, and the builtins namespace, the namespace of the module :mod:`builtins`.  The global namespace is searched first.  If the names are not found there, the builtins namespace is searched next.' (fetched)
- Ruff A001 builtin-variable-shadowing (astral-sh/ruff crates/ruff_linter/src/rules/flake8_builtins/rules/builtin_variable_shadowing.rs) — 'Reusing a builtin name for the name of a variable increases the difficulty of reading and maintaining the code, and can cause non-obvious errors, as readers may mistake the variable for the builtin and vice versa.'; 'Builtins can be marked as exceptions to this rule via the' (fetched)
- Ruff A004 builtin-import-shadowing (astral-sh/ruff crates/ruff_linter/src/rules/flake8_builtins/rules/builtin_import_shadowing.rs) — 'Reusing a builtin for the name of an import increases the difficulty of reading and maintaining the code, and can cause non-obvious errors, as readers may mistake the variable for the builtin and vice versa.'; 'from rich import print as rich_print'; 'rich.print("Some message")' (fetched)
- Ruff A002 builtin-argument-shadowing (astral-sh/ruff crates/ruff_linter/src/rules/flake8_builtins/rules/builtin_argument_shadowing.rs) — 'Reusing a builtin name for the name of an argument increases the difficulty of reading and maintaining the code, and can cause non-obvious errors, as readers may mistake the argument for the builtin and vice versa.' (fetched)
- Ruff A003 builtin-attribute-shadowing (astral-sh/ruff crates/ruff_linter/src/rules/flake8_builtins/rules/builtin_attribute_shadowing.rs) — 'this rule only applies to those methods and attributes that both shadow a builtin _and_ are referenced from within the class scope' (fetched)
- Ruff A006 builtin-lambda-argument-shadowing (astral-sh/ruff crates/ruff_linter/src/rules/flake8_builtins/rules/builtin_lambda_argument_shadowing.rs) — 'Reusing a builtin name for the name of a lambda argument increases the difficulty of reading and maintaining the code and can cause non-obvious errors.' (fetched)
- Caveat: the every-scope position (Ruff A001, A002, A003, A004, A006) and the global-scope position (Pylint W0622) agree on module-level and global-declared bindings; the card carries that shared part only.

---
title: A module-level import comes before every other statement of the module except its docstring, __future__ imports, dunder assignments such as __all__ and a sys.path or os.environ change between imports
rule_id: PY-42
domain: design
step: [implement, review]
applies_to: [python]
triggers: ['^import\s+[\w.]+', '^from\s+[\w.]+\s+import\s']
scope: file
check_kind: mechanical
severity_default: minor
---

# A module-level import comes before every other statement of the module except its docstring, __future__ imports, dunder assignments such as __all__ and a sys.path or os.environ change between imports

## Thesis
At module level, a Python file puts its import statements at the top: just after any module comments and docstring, after any `from __future__` imports and the module-level dunders, names with two leading and two trailing underscores such as `__all__`, `__author__` and `__version__`, and before module globals, constants and other code. A `sys.path` modification (`sys.path.insert`, `sys.path.append` and the like) or an `os.environ` modification standing between imports is excepted; any other module code followed by an import mixes code and imports.

## Rationale
An import statement is executed where it stands: it finds the module, loading and initializing it if necessary, and defines a name in the current namespace just as an assignment statement would. A module's top-level statements are executable too; they initialize the module and are executed only the first time the module name is encountered in an import statement. Module code written above an import therefore runs before that import has loaded its module and bound its name, and the module's imports end up mixed with its code instead of standing together at the top of the file.

## Example
```python
bad:  import os
      home = os.environ["HOME"]
      from pathlib import Path
good: import os
      from pathlib import Path
      home = os.environ["HOME"]
```

## Limits
In a Jupyter notebook the check applies per cell: an import stands at the top of its cell. Moving an import above module code re-orders imports, and re-ordering imports can change the execution order of the imported code, which is why the automatic fix is marked unsafe. The rule covers module-level imports; an import inside a function or class body is outside it.

## Validator
Grep the hunk for an `import` or `from ... import` line at column 0. Open the file and list the module-level statements above that line. Pass over the docstring, comments, `from __future__` imports, assignments to module dunders (`__all__`, `__author__`, `__version__`), other imports (a module-level `try` or `if` block whose body is only imports counts as imports), and calls that modify `sys.path` or `os.environ`. Validator question: **Does a module-level import statement follow a module-level statement other than the docstring, a `from __future__` import, a module dunder assignment, another import, or a `sys.path` or `os.environ` modification?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-42`, severity minor, `file`, `symbol` = the imported module, `code` = the misplaced import line and the first module statement above it, verbatim from the diff, `fix` = the import moved up into the import block at the top of the file, below the docstring, the `from __future__` imports and the module dunders, `rationale` = names the module code that runs before the import and the mixing of code and imports).

## Source
- PEP 8 §Imports (https://raw.githubusercontent.com/python/peps/main/peps/pep-0008.rst) — 'Imports are always put at the top of the file, just after any module comments and docstrings, and before module globals and constants.' (fetched)
- PEP 8 §Module Level Dunder Names (https://raw.githubusercontent.com/python/peps/main/peps/pep-0008.rst) — '(i.e. names with two leading and two trailing underscores)' (fetched)
- PEP 8 §Module Level Dunder Names (https://raw.githubusercontent.com/python/peps/main/peps/pep-0008.rst) — 'should be placed after the module docstring but before any import statements' (fetched)
- PEP 8 §Module Level Dunder Names (https://raw.githubusercontent.com/python/peps/main/peps/pep-0008.rst) — 'Python mandates that future-imports must appear in the module before any other code except docstrings' (fetched)
- Google Python Style Guide §3.13 Imports formatting (https://raw.githubusercontent.com/google/styleguide/gh-pages/pyguide.md) — 'Imports are always put at the top of the file, just after any module comments and docstrings and before module globals and constants.' (fetched)
- Ruff E402 module-import-not-at-top-of-file (astral-sh/ruff crates/ruff_linter/src/rules/pycodestyle/rules/module_import_not_at_top_of_file.rs) — 'This rule makes an exception for both `sys.path` modifications (allowing for `sys.path.insert`, `sys.path.append`, etc.) and `os.environ` modifications between imports.' (fetched)
- Ruff E402 module-import-not-at-top-of-file (astral-sh/ruff crates/ruff_linter/src/rules/pycodestyle/rules/module_import_not_at_top_of_file.rs) — 'For Jupyter notebooks, this rule checks for imports that are not at the top of a *cell*.' (fetched)
- Ruff E402 module-import-not-at-top-of-file (astral-sh/ruff crates/ruff_linter/src/rules/pycodestyle/rules/module_import_not_at_top_of_file.rs) — 'This rule's fix is marked as unsafe as imports moved to the top of the file are placed above existing imports, in reverse order than they were in the file.' (fetched)
- Ruff E402 module-import-not-at-top-of-file (astral-sh/ruff crates/ruff_linter/src/rules/pycodestyle/rules/module_import_not_at_top_of_file.rs) — 'Re-ordering imports is unsafe as it can change the execution order of the imported code.' (fetched)
- Pylint wrong-import-position (C0413) message description (pylint-dev/pylint doc/data/messages/w/wrong-import-position/bad.py) — 'Used when code and imports are mixed.' (fetched)
- CPython Doc/reference/simple_stmts.rst §The import statement (https://raw.githubusercontent.com/python/cpython/main/Doc/reference/simple_stmts.rst) — 'find a module, loading and initializing it if necessary' (fetched)
- CPython Doc/reference/simple_stmts.rst §The import statement (https://raw.githubusercontent.com/python/cpython/main/Doc/reference/simple_stmts.rst) — 'define a name or names in the current namespace for the scope where the :keyword:`import` statement occurs, just as an assignment statement would' (fetched)
- CPython Doc/tutorial/modules.rst §More on Modules (https://raw.githubusercontent.com/python/cpython/main/Doc/tutorial/modules.rst) — 'A module can contain executable statements as well as function definitions. These statements are intended to initialize the module. They are executed only the *first* time the module name is encountered in an import statement.' (fetched)

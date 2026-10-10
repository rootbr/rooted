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

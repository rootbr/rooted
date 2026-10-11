---
title: A module imports the names it uses explicitly and writes from module import * only to republish an internal interface as part of its public API
rule_id: PY-41
domain: design
step: [implement, review]
applies_to: [python]
triggers: ['^\s*from\s+[\w.]+\s+import\s+\*', '\bimport\s+\*\s*(#.*)?$']
scope: file
check_kind: mechanical
severity_default: major
---

# A module imports the names it uses explicitly and writes from module import * only to republish an internal interface as part of its public API

## Thesis
A Python module imports what it uses as `import module`, accessing members as `module.name`, or as `from module import name`, listing every imported name; it writes `from module import *` only for the one defensible use of a wildcard import, republishing an internal interface as part of a public API, for example overwriting a pure Python implementation of an interface with the definitions from an optional accelerator module when exactly which definitions will be overwritten is not known in advance.

## Rationale
`from module import *` binds, in the local namespace of the scope where the statement occurs, every public name the other module defines: the names given in its `__all__`, or, when `__all__` is not defined, every name in its namespace that does not begin with an underscore. Which names arrive is decided by the other module, and imported names can change when a dependency is updated, so a wildcard import that works today might be broken tomorrow. A wildcard import makes it unclear which names are present in the namespace and from which module each was imported, confusing both readers and many automated tools: when a name is neither defined nor explicitly imported, it is unclear whether it is undefined or came in through the wildcard import. It introduces an unknown set of names that can conflict with names defined locally and possibly hide something already defined. Listing every imported name, or importing the module and accessing its members as `module.name`, lets a reader know where each name comes from.

## Example
```python
bad:  from geometry import *
      total = area(shape) + perimeter(shape)
good: from geometry import area, perimeter
      total = area(shape) + perimeter(shape)
```

## Limits
When a module republishes an internal interface as part of its public API through a wildcard import, the guidelines on public and internal interfaces still apply to the names republished this way. In an interactive session a wildcard import is acceptable to save typing. A wildcard import raises no issue in `__init__.py` files, where wildcard imports are a common way of populating these modules, nor in modules doing only imports, which are sometimes created as a proxy for third-party modules, although wildcard imports might still create issues in these cases.

## Validator
Grep the hunk for `import *`. Open the file and note whether it is an `__init__.py` file or a module doing only imports (a `try`/`except` choosing between two wildcard imports counts as imports); treat either as republishing. Elsewhere, read the module's `__all__` and the comments at the import, and trace whether the wildcard import republishes another module's interface as this module's public API, such as definitions of an optional accelerator module overriding pure Python ones. Validator question: **Does a module other than an `__init__.py` file or an imports-only module bind names with a wildcard import that does not republish an internal interface as part of the module's public API?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-41`, severity major, `file`, `symbol`, `code` = the `from module import *` line verbatim from the diff, `fix` = `from module import name1, name2` listing every name the file uses from that module, or `import module` with each use written `module.name`, `rationale` = names that the wildcard import binds a set of names the other module decides, so readers and tools cannot tell which names are present or where they come from, and an imported name can conflict with a local one).

## Source
- PEP 8 §Imports (https://raw.githubusercontent.com/python/peps/main/peps/pep-0008.rst) — 'should be avoided, as they make it unclear which names are present in the namespace, confusing both readers and many automated tools.' (fetched)
- PEP 8 §Imports (https://raw.githubusercontent.com/python/peps/main/peps/pep-0008.rst) — 'There is one defensible use case for a wildcard import, which is to republish an internal interface as part of a public API (for example, overwriting a pure Python implementation of an interface with the definitions from an optional accelerator module and exactly which definitions will be overwritten isn't known in advance).' (fetched)
- PEP 8 §Imports (https://raw.githubusercontent.com/python/peps/main/peps/pep-0008.rst) — 'When republishing names this way, the guidelines below regarding public and internal interfaces still apply.' (fetched)
- CPython Doc/reference/simple_stmts.rst §The import statement (https://raw.githubusercontent.com/python/cpython/main/Doc/reference/simple_stmts.rst) — 'If the list of identifiers is replaced by a star (``'*'``), all public names defined in the module are bound in the local namespace for the scope where the :keyword:`import` statement occurs.' (fetched)
- CPython Doc/reference/simple_stmts.rst §The import statement (https://raw.githubusercontent.com/python/cpython/main/Doc/reference/simple_stmts.rst) — 'The names given in ``__all__`` are all considered public and are required to exist.' (fetched)
- CPython Doc/reference/simple_stmts.rst §The import statement (https://raw.githubusercontent.com/python/cpython/main/Doc/reference/simple_stmts.rst) — 'If ``__all__`` is not defined, the set of public names includes all names found in the module's namespace which do not begin with an underscore character (``'_'``).' (fetched)
- CPython Doc/tutorial/modules.rst §More on Modules (https://raw.githubusercontent.com/python/cpython/main/Doc/tutorial/modules.rst) — 'In most cases Python programmers do not use this facility since it introduces an unknown set of names into the interpreter, possibly hiding some things you have already defined.' (fetched)
- CPython Doc/tutorial/modules.rst §More on Modules (https://raw.githubusercontent.com/python/cpython/main/Doc/tutorial/modules.rst) — 'However, it is okay to use it to save typing in interactive sessions.' (fetched)
- Ruff F403 undefined-local-with-import-star (astral-sh/ruff crates/ruff_linter/src/rules/pyflakes/rules/imports.rs) — 'Wildcard imports (e.g., `from module import *`) make it hard to determine which symbols are available in the current namespace, and from which module they were imported.' (fetched)
- Ruff F405 undefined-local-with-import-star-usage (astral-sh/ruff crates/ruff_linter/src/rules/pyflakes/rules/imports.rs) — 'If a module contains a wildcard import, and a name in the current namespace has not been explicitly defined or imported, then it's unclear whether the name is undefined or was imported by the wildcard import.' (fetched)
- SonarSource python S2208 (SonarSource/sonar-python python-checks/src/main/resources/org/sonar/l10n/py/rules/python/S2208.html) — 'It could lead to conflicts between names defined locally and the ones imported.' (fetched)
- SonarSource python S2208 (SonarSource/sonar-python python-checks/src/main/resources/org/sonar/l10n/py/rules/python/S2208.html) — 'It reduces code readability as developers will have a hard time knowing where names come from.' (fetched)
- SonarSource python S2208 (SonarSource/sonar-python python-checks/src/main/resources/org/sonar/l10n/py/rules/python/S2208.html) — 'Remember that imported names can change when you update your dependencies. A wildcard import that works today might be broken tomorrow.' (fetched)
- SonarSource python S2208 (SonarSource/sonar-python python-checks/src/main/resources/org/sonar/l10n/py/rules/python/S2208.html) — 'No issue will be raised in __init__.py files. Wildcard imports are a common way of populating these modules.' (fetched)
- SonarSource python S2208 (SonarSource/sonar-python python-checks/src/main/resources/org/sonar/l10n/py/rules/python/S2208.html) — 'No issue will be raised in modules doing only imports. Local modules are sometimes created as a proxy for third-party modules.' (fetched)
- SonarSource python S2208 (SonarSource/sonar-python python-checks/src/main/resources/org/sonar/l10n/py/rules/python/S2208.html) — 'Just keep in mind that wildcard imports might still create issues in these cases.' (fetched)
- SonarSource python S2208 (SonarSource/sonar-python python-checks/src/main/resources/org/sonar/l10n/py/rules/python/S2208.html) — 'Replace it with import mymodule and access module members as mymodule.myfunction.' (fetched)
- SonarSource python S2208 (SonarSource/sonar-python python-checks/src/main/resources/org/sonar/l10n/py/rules/python/S2208.html) — 'List every imported name.' (fetched)
- Pylint wildcard-import (W0401) message description (pylint-dev/pylint doc/data/messages/w/wildcard-import/bad.py) — 'Used when `from module import *` is detected.' (fetched)
- Pylint unused-wildcard-import (W0614) message description (pylint-dev/pylint doc/data/messages/u/unused-wildcard-import/bad.py) — 'Used when an imported module or variable is not used from a `'from X import *'` style import.' (fetched)

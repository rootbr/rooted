---
title: A new Python directory of modules meant as a regular package holds an __init__.py unless a PEP 420 namespace package is intended
rule_id: PY-167
domain: design
step: [implement, review]
applies_to: [python, build-config]
triggers: ['signal:added_file', '^from\s+[.]+\w*([.]\w+)*\s+import\s']
scope: base-compare
check_kind: semantic
severity_default: minor
---

# A new Python directory of modules meant as a regular package holds an __init__.py unless a PEP 420 namespace package is intended

## Thesis
A directory of Python modules that a change adds as a regular package holds an `__init__.py`; the file is left out only where a PEP 420 namespace package is intended. Namespace packages are less widely used, so a package directory without the file is typically meant to be a regular package, and the missing file is probably an oversight.

## Rationale
Python packages are directories that contain a file named `__init__.py`, and the file indicates that the directory is a package that can be imported the same way a module can. A directory without it can still be imported: a subdirectory inside a regular package that has no `__init__.py` is treated as an implicit namespace package (a namespace subpackage) rooted in that parent, so the import succeeds without the file. In setuptools package discovery the missing file does count. `find_packages()`, which `setup.cfg` spells `find:`, returns a list of the packages it could find, and with `find_packages()` all directories without an `__init__.py` are ignored; when `pkg` has no `__init__.py`, `pkg.namespace` beneath it is ignored by `find_packages()` and by `find:` alike, so those modules are missing from the package list that discovery returns. `find_namespace:` works like `find:` except that it counts a directory as a package even if it does not contain `__init__.py` directly, and `find_namespace_packages()` scans all directories.

## Example
```python
bad:  # added: src/pkg/sub/loader.py; absent: src/pkg/sub/__init__.py
      from .helpers import load
      setup(packages=find_packages(where="src"))  # setup.py
good: # added: src/pkg/sub/loader.py and an empty src/pkg/sub/__init__.py
      from .helpers import load
      setup(packages=find_packages(where="src"))  # setup.py
```

## Limits
Where a namespace package is intended, the directory stays without `__init__.py` and discovery uses `find_namespace_packages()` or `find_namespace:`, which count a directory as a package even if it does not contain `__init__.py` directly. A directory listed in the project's Ruff `namespace-packages` setting is marked as a namespace package, and module resolution treats it and all its subdirectories as if they contained an `__init__.py`; such a directory is outside the rule. With `[tool.setuptools.packages.find]` in `pyproject.toml`, setuptools considers implicit namespaces by default when scanning the project directory, so there the missing file drops nothing from discovery unless `namespaces = false` is set; the directory still imports as an implicit namespace package. The discovery half reaches setuptools' `find_packages()`, `find:` and `[tool.setuptools.packages.find]`, not another build backend.

## Validator
For each module the diff adds, take its directory; where the base version of the tree already holds that directory, pass over it, since the rule reaches a directory the change adds; otherwise check at the head whether that directory holds an `__init__.py`. Where it does not, look for signs that the directory is meant as a regular package: a module in it that imports a sibling relatively (`from .x import y`), an import elsewhere of its dotted path, a parent directory that holds `__init__.py`, a `find_packages()` call or `find:` directive whose `where` covers it. Then look for signs that a namespace package is intended: `find_namespace_packages()` or `find_namespace:` covering it, or the directory in the `namespace-packages` list of the Ruff configuration in `pyproject.toml` or `ruff.toml`. Validator question: **Does the change add modules to a directory without `__init__.py` that is meant as a regular package, with no namespace package declared for it?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-167`, severity minor, `file`, `symbol`, `code` = the added module's path and its first relative import line, `fix` = an empty `__init__.py` added in that directory, or `find_namespace_packages()` where a namespace package is meant, `rationale` = that a directory without `__init__.py` imports as an implicit namespace package while `find_packages()` and `find:` ignore it and the packages beneath it).

## Source
- Ruff INP001 implicit-namespace-package (astral-sh/ruff crates/ruff_linter/src/rules/flake8_no_pep420/rules/implicit_namespace_package.rs) — 'Namespace packages are less widely used, so a package that lacks an `__init__.py` file is typically meant to be a regular package, and the absence of the `__init__.py` file is probably an oversight.' (fetched)
- Ruff INP001 implicit-namespace-package (astral-sh/ruff crates/ruff_linter/src/rules/flake8_no_pep420/rules/implicit_namespace_package.rs) — 'Python packages are directories that contain a file named `__init__.py`. The existence of this file indicates that the directory is a Python package, and so it can be imported the same way a module can be imported.' (fetched)
- Ruff INP001 implicit-namespace-package (astral-sh/ruff crates/ruff_linter/src/rules/flake8_no_pep420/rules/implicit_namespace_package.rs) — 'Directories that lack an `__init__.py` file can still be imported' (fetched)
- CPython Doc/reference/import.rst §Regular packages (https://raw.githubusercontent.com/python/cpython/main/Doc/reference/import.rst) — 'A subdirectory inside a regular package that does not contain an ``__init__.py`` file is treated as an implicit :ref:`namespace package <reference-namespace-package>` (a "namespace subpackage") rooted in that parent.' (fetched)
- setuptools docs/userguide/package_discovery.rst §Finding simple packages (https://raw.githubusercontent.com/pypa/setuptools/main/docs/userguide/package_discovery.rst) — '``find:`` (``find_packages()``) takes a source directory and two lists of package name patterns to exclude and include, and then returns a list of ``str`` representing the packages it could find.' (fetched)
- setuptools docs/userguide/package_discovery.rst §Finding simple packages (https://raw.githubusercontent.com/pypa/setuptools/main/docs/userguide/package_discovery.rst) — '``pkg`` does not contain an ``__init__.py`` file, therefore ``pkg.namespace`` is ignored by ``find_packages()``' (fetched)
- setuptools docs/userguide/package_discovery.rst §Finding simple packages (https://raw.githubusercontent.com/pypa/setuptools/main/docs/userguide/package_discovery.rst) — '``pkg`` does not contain an ``__init__.py`` file, therefore ``pkg.namespace`` is ignored by ``find:``' (fetched)
- setuptools docs/userguide/package_discovery.rst §Finding simple packages (https://raw.githubusercontent.com/pypa/setuptools/main/docs/userguide/package_discovery.rst) — 'When using ``tool.setuptools.packages.find`` in ``pyproject.toml``, setuptools will consider :pep:`implicit namespaces <420>` by default when scanning your project directory.' (fetched)
- setuptools docs/userguide/package_discovery.rst §Finding namespace packages (https://raw.githubusercontent.com/pypa/setuptools/main/docs/userguide/package_discovery.rst) — 'When you use ``find_packages()``, all directories without an ``__init__.py`` file will be ignored.' (fetched)
- setuptools docs/userguide/package_discovery.rst §Finding namespace packages (https://raw.githubusercontent.com/pypa/setuptools/main/docs/userguide/package_discovery.rst) — 'would count a directory as a package even if it doesn't contain ``__init__.py`` file directly.' (fetched)
- setuptools docs/userguide/package_discovery.rst §Finding namespace packages (https://raw.githubusercontent.com/pypa/setuptools/main/docs/userguide/package_discovery.rst) — 'On the other hand, ``find_namespace_packages()`` will scan all directories.' (fetched)
- setuptools docs/userguide/package_discovery.rst §Finding simple packages (https://raw.githubusercontent.com/pypa/setuptools/main/docs/userguide/package_discovery.rst) — 'To avoid ``pkg.namespace`` from being added to your package list you can set ``namespaces = false``.' (fetched)
- Ruff setting namespace-packages (astral-sh/ruff crates/ruff_workspace/src/options.rs) — 'Mark the specified directories as namespace packages. For the purpose of … module resolution, Ruff will treat those directories and all their subdirectories … as if they contained an `__init__.py` file.' (fetched)
- Caveat: the discovery consequence is documented for setuptools only; INP001 is off by default in its pedantic group.

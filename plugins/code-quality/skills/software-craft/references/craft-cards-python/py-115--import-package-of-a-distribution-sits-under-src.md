---
title: An import package of a Python project built into a distribution sits under src/ rather than directly in the project root beside pyproject.toml
rule_id: PY-115
domain: tooling
step: [design]
applies_to: [python, build-config, tests]
triggers: ['^\s*\[tool[.]setuptools[.]packages[.]find\]', '^\s*packages\s*=\s*\[', 'signal:added_file']
scope: file
check_kind: semantic
severity_default: minor
---

# An import package of a Python project built into a distribution sits under src/ rather than directly in the project root beside pyproject.toml

## Thesis
In a Python project that is built into a distribution and whose tests and tools, started in the project root, are meant to exercise the installed copy of the code, each import package sits in a `src/` subdirectory, as `src/<package>/`, rather than directly in the project root beside `pyproject.toml`.

## Rationale
The Python interpreter includes the current working directory as the first item on the import path, so if an import package exists in the current working directory with the same name as an installed import package, the variant from the current working directory is used. This can lead to subtle misconfiguration of the project's packaging tooling, which could result in files not being included in a distribution; keeping import packages in a directory separate from the root directory of the project ensures that the installed copy is used. pytest defaults to the `prepend` import mode, and once the tests directory is changed into packages with `__init__.py` files, pytest prepends the root of the repository to `sys.path`, which makes a package in the root importable — a problem when the tests, run for example in a virtual environment, are meant to exercise the installed version of the package, not the local code from the repository. With the flat layout, an editable installation that adds the project directory to the import path through a path configuration file also puts the other project files and the packaging and tooling configuration files on it, which makes certain imports work in editable installations but not in regular installations. With automatic discovery, setuptools refuses to create distribution archives from a flat layout with multiple top-level packages or modules, to prevent accidentally publishing code not meant for distribution, whereas with the src layout other Python files or folders in the project root are not distributed by mistake.

## Example
```python
bad:  # pyproject.toml beside mypkg/__init__.py in the project root
      [tool.setuptools]
      packages = ["mypkg"]
good: # pyproject.toml beside src/mypkg/__init__.py
      [tool.setuptools.packages.find]
      where = ["src"]
```

## Limits
The src layout requires installation of the project to be able to run its code, and the flat layout does not: development gains a step, typically an editable installation for development and a regular installation for testing, so a project that is not built into a distribution is outside the rule. Tests of a src-layout project run against the local copy without an editable install only once the search path for module files is extended, for example with `PYTHONPATH=src`. The sources split on how firm the rule is: one position strongly suggests the src layout generally, and especially under the default `prepend` import mode; another holds the flat layout very practical for using the REPL but in some situations more error-prone, for example during tests or with folders or Python files hanging around the project root. The condition that separates them is whether a process started in the project root is meant to use the installed copy or the in-development one: tests and tools meant to exercise the installed version fall under the rule, because the working directory first on the import path makes the in-development copy shadow the installed one, whereas a REPL session that deliberately plays with the working copy through the implicit current-directory entry of the import path is the case where the flat layout is practical and the src layout needs an editable install first.

## Validator
Grep the hunk for a `[tool.setuptools.packages.find]` table, an explicit `packages = [...]` list and added `__init__.py` files. Open `pyproject.toml` at the project root and confirm the project is built into a distribution: a `[build-system]` table and a `[project]` table with a `name`. Trace each import package the configuration names, or that discovery finds, to its directory: directly beside `pyproject.toml`, or under `src/`. Check that tests or tools run from the project root and are meant to exercise the installed copy, such as a `tests/` directory, a `[tool.pytest.ini_options]` table or a tox or nox configuration that installs the project. Validator question: **Does the change add an import package of a project built into a distribution, whose tests or tools run from the project root, directly in the project root beside `pyproject.toml` rather than under `src/`?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-115`, severity minor, `file`, `symbol`, `code` = the `packages` list or the `[tool.setuptools.packages.find]` table and the package path verbatim from the diff, `fix` = the package moved to `src/<package>/` and found with `where = ["src"]` under `[tool.setuptools.packages.find]`, with an editable installation for development, `rationale` = the current working directory first on the import path, where the in-development copy shadows the installed one and can leave files out of a distribution).

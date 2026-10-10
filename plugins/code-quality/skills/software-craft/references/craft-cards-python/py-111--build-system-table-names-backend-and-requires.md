---
title: The pyproject.toml of a project built into a distribution declares a [build-system] table whose build-backend names the backend and whose requires lists the backend's package
rule_id: PY-111
domain: tooling
step: [implement, review]
applies_to: [python, build-config]
triggers: ['^\s*\[build-system\]', '^\s*build-backend\s*=', '^\s*requires\s*=\s*\[', '^\s*\[project\]', 'signal:added_file']
scope: file
check_kind: semantic
severity_default: major
---

# The pyproject.toml of a project built into a distribution declares a [build-system] table whose build-backend names the backend and whose requires lists the backend's package

## Thesis
The `pyproject.toml` of a Python project that is built into a distribution — one with a `[project]` table, a `setup.py` or a `setup.cfg` — carries a `[build-system]` table whose `build-backend` key names the build backend and whose `requires` key lists the backend's package and any other dependency the build needs.

## Rationale
The `[build-system]` table defines the build tool a project uses and belongs in the file regardless of which build backend it is. Its `build-backend` value is a string naming the Python object that performs the build, in the same `module:object` syntax as a setuptools entry point; its `requires` value is the list of dependencies needed to build the project, typically just the build backend package, possibly with additional dependencies. If `pyproject.toml` is absent or the `build-backend` key is missing, the source tree is not using the PEP 517 interface, and tools should revert to the legacy behaviour of running `setup.py`, directly or by implicitly invoking the `setuptools.build_meta:__legacy__` backend; for a file that lacks the `[build-system]` table the default values should be used, the example table `requires = ["setuptools"]`. A build frontend should, by default, create an isolated environment for each build containing only the standard library and any explicitly requested build dependencies, which are the strings `requires` lists as the dependencies required to execute the build system. A tool that reads a `[build-system]` table that is present but missing a required field should consider it an error.

## Example
```python
bad:  PYPROJECT_TOML = """# pyproject.toml
      [project]
      name = "pkg" """
good: PYPROJECT_TOML = """# pyproject.toml
      [build-system]
      requires = ["hatchling"]
      build-backend = "hatchling.build"
      [project]
      name = "pkg" """
```

## Limits
A `pyproject.toml` that stores only configuration other than build-related data, such as `[tool.ruff]` or `[tool.mypy]`, may legitimately lack a `[build-system]` table; when the project also has no `setup.py`, `setup.cfg` or other build configuration file and no `[project]` table, nothing indicates that it is built, and the rule does not reach it. A backend hosted in the source tree through the `backend-path` key is loaded from the listed directories rather than from a distribution `requires` names, so for such a table `requires` lists only what that backend itself needs to run.

## Validator
Open the `pyproject.toml` the change adds or edits and check for a `[project]` table in it, or a `setup.py` or `setup.cfg` beside it. Read its `[build-system]` table: the `build-backend` string and the `requires` list, and check that the distribution providing the `build-backend` module (for example `hatchling` for `hatchling.build`, `setuptools` for `setuptools.build_meta`) appears in `requires`. Skip that last check when the table carries a `backend-path` key. Validator question: **Does the pyproject.toml of a project with a `[project]` table, a `setup.py` or a `setup.cfg` lack a `[build-system]` table, lack its `build-backend` or `requires` key, or name a backend whose distribution `requires` does not list?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-111`, severity major, `file`, `symbol`, `code` = the `[project]` header or the incomplete `[build-system]` table verbatim, `fix` = a `[build-system]` table with `requires = ["<backend package>"]` and `build-backend = "<module>"` for the backend the project's configuration is written for, `rationale` = without `build-backend` tools fall back to running `setup.py` through setuptools' legacy backend, and the isolated build environment holds only what `requires` lists).

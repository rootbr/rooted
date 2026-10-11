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

## Source
- PyPA guide guides/writing-pyproject-toml, the note before §Declaring the build backend (pypa/packaging.python.org source/guides/writing-pyproject-toml.rst) — 'The ``[build-system]`` table should always be present, regardless of which build backend you use (``[build-system]`` *defines* the build tool you use).' (fetched)
- PyPA guide guides/writing-pyproject-toml §Declaring the build backend (pypa/packaging.python.org source/guides/writing-pyproject-toml.rst) — 'The ``[build-system]`` table contains a ``build-backend`` key, which specifies the build backend to be used. It also contains a ``requires`` key, which is a list of dependencies needed to build the project -- this is typically just the build backend package, but it may also contain additional dependencies.' (fetched)
- PEP 517 §Source trees (python/peps peps/pep-0517.rst) — '``build-backend`` is a string naming a Python object that will be used to perform the build (see below for details). This is formatted following the same ``module:object`` syntax as a ``setuptools`` entry point.' (fetched)
- PEP 517 §Source trees (python/peps peps/pep-0517.rst) — 'If the ``pyproject.toml`` file is absent, or the ``build-backend`` key is missing, the source tree is not using this specification, and tools should revert to the legacy behaviour of running ``setup.py`` (either directly, or by implicitly invoking the ``setuptools.build_meta:__legacy__`` backend).' (fetched)
- PEP 517, the non-normative advice to frontend implementors on build isolation (python/peps peps/pep-0517.rst) — 'A build frontend SHOULD, by default, create an isolated environment for each build, containing only the standard library and any explicitly requested build-dependencies.' (fetched)
- PEP 517 §In-tree build backends (python/peps peps/pep-0517.rst) — 'Projects can specify that their backend code is hosted in-tree by including the ``backend-path`` key in ``pyproject.toml``.' (fetched); the section opens with the case of including the backend source in the tree 'rather than referencing the backend via the ``requires`` key'.
- PyPA pyproject.toml specification §Declaring build system dependencies: the [build-system] table (pypa/packaging.python.org source/specifications/pyproject-toml.rst) — 'This key must have a value of a list of strings representing dependencies required to execute the build system.' (fetched)
- PyPA pyproject.toml specification §Declaring build system dependencies: the [build-system] table (pypa/packaging.python.org source/specifications/pyproject-toml.rst) — 'Build tools are expected to use the example configuration file above as their default semantics when a ``pyproject.toml`` file is not present.' (fetched); the example is `requires = ["setuptools"]`.
- PyPA pyproject.toml specification §Declaring build system dependencies: the [build-system] table (pypa/packaging.python.org source/specifications/pyproject-toml.rst) — 'A ``pyproject.toml`` file may be used to store configuration details other than build-related data and thus lack a ``[build-system]`` table legitimately. If the file exists but is lacking the ``[build-system]`` table then the default values as specified above should be used. If the table is specified but is missing required fields then the tool should consider it an error.' (fetched)
- PyPA pyproject.toml specification §Declaring build system dependencies: the [build-system] table (pypa/packaging.python.org source/specifications/pyproject-toml.rst) — 'Tools may choose to present an error to the user if the file exists, ``[build-system]`` table is missing, and there is no clear indication that the project should be built (e.g., no setup.py/setup.cfg or other build configuration files, and no ``[project]`` table).' (fetched)

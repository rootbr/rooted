---
title: A Python project a change creates states its metadata statically in the [project] table of pyproject.toml and keeps setup.py only for configuration that needs code, such as C extensions
rule_id: PY-114
domain: tooling
step: [design, implement]
applies_to: [python, build-config]
triggers: ['^\s*from\s+setuptools\s+import\s+.*\bsetup\b', '\bsetup\(\s*name\s*=', '^\s*\[metadata\]', 'signal:added_file']
scope: file
check_kind: semantic
severity_default: minor
---

# A Python project a change creates states its metadata statically in the [project] table of pyproject.toml and keeps setup.py only for configuration that needs code, such as C extensions

## Thesis
When a change creates a Python project, the project's metadata — its name, its version or a `dynamic` entry for the version, its dependencies and its scripts — is written statically in the `[project]` table of `pyproject.toml`, and a `setup.py` is kept only if some programmatic configuration is needed, such as building C extensions.

## Rationale
The `[project]` table is the format that most build backends use to specify a project's basic metadata, such as its dependencies and its name, and a command the package installs is declared in its `[project.scripts]` table; the setuptools build backend supports both the `[project]` table and the older format in `setup.cfg` or `setup.py`. Core metadata specified statically serves speed, ease of specification, unambiguity and deterministic consumption by build back-ends, and the table is a tool-agnostic way of specifying metadata, for ease of learning and of transitioning between build back-ends. A field the build backend computes, such as a version read from a `__version__` attribute or a Git tag, is marked as dynamic in the table, and filling it is the build backend's responsibility.

## Example
```python
bad:  # setup.py of a new project without extension modules
      from setuptools import setup
      setup(name="mytool", version="1.0", install_requires=["requests>=2"])
good: # pyproject.toml, beside a [build-system] table naming the build backend
      [project]
      name = "mytool"
      version = "1.0"
      dependencies = ["requests>=2"]
```

## Limits
The rule reaches only a project the change creates: the `setup.cfg` and `setup.py` formats are still valid, so metadata an existing project keeps in them is not a finding. A `setup.py` that a new project keeps for programmatic configuration, such as building C extensions, is correct. The `[project]` table is understood by most build backends, but some build backends use a different format — Poetry before version 2.0 used the `[tool.poetry]` table instead — and a project on such a backend is outside the rule.

## Validator
Grep the hunk for `from setuptools import setup`, a `setup(name=` call and a `[metadata]` section of `setup.cfg`. Confirm the change creates the file, alone or together with the project's first `pyproject.toml`; an existing file the change edits is outside the rule. Open `pyproject.toml` at the project root when the project has one: read its `[build-system]` table for the build backend, and its `[project]` table and `dynamic` list for the fields already declared; a new project without a `pyproject.toml` declares no build backend that uses a different format, so the question's backend clause holds for it. Trace what the `setup()` call configures besides metadata — `ext_modules`, a `cmdclass` or values computed by code are programmatic configuration and stay in `setup.py`. Validator question: **Does a file the change creates write a new project's name, version, dependencies or scripts into `setup()` keyword arguments or a `setup.cfg` `[metadata]` section, while the project declares no build backend that uses a format other than the `[project]` table, and the field is neither in `[project]` nor listed in its `dynamic`?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-114`, severity minor, `file`, `symbol`, `code` = the `setup(...)` call or the `[metadata]` section verbatim from the diff, `fix` = the same fields as `name`, `version`, `dependencies` and `[project.scripts]` entries in the `[project]` table of `pyproject.toml` beside a `[build-system]` table, with `setup.py` reduced to its programmatic configuration or removed, `rationale` = core metadata stated statically in the tool-agnostic `[project]` table that build back-ends consume deterministically, with `setup.py` kept only for configuration that needs code).

## Source
- PyPA guide guides/writing-pyproject-toml §note before Declaring the build backend (https://raw.githubusercontent.com/pypa/packaging.python.org/main/source/guides/writing-pyproject-toml.rst) — 'For new projects, use the ``[project]`` table, and keep ``setup.py`` only if some programmatic configuration is needed (such as building C extensions), but the ``setup.cfg`` and ``setup.py`` formats are still valid.' (fetched)
- PyPA guide guides/writing-pyproject-toml §opening list of tables (https://raw.githubusercontent.com/pypa/packaging.python.org/main/source/guides/writing-pyproject-toml.rst) — 'The ``[project]`` table is the format that most build backends use to specify your project's basic metadata, such as the dependencies, your name, etc.' (fetched)
- PyPA guide guides/writing-pyproject-toml §note before Declaring the build backend (https://raw.githubusercontent.com/pypa/packaging.python.org/main/source/guides/writing-pyproject-toml.rst) — 'the ``[project]`` table is understood by *most* build backends, but some build backends use a different format.' (fetched)
- PyPA guide guides/writing-pyproject-toml §note before Declaring the build backend (https://raw.githubusercontent.com/pypa/packaging.python.org/main/source/guides/writing-pyproject-toml.rst) — 'it used the ``[tool.poetry]`` table instead. With version 2.0, it supports both.' (fetched)
- PyPA guide guides/writing-pyproject-toml §note before Declaring the build backend (https://raw.githubusercontent.com/pypa/packaging.python.org/main/source/guides/writing-pyproject-toml.rst) — 'Also, the setuptools_ build backend supports both the ``[project]`` table, and the older format in ``setup.cfg`` or ``setup.py``.' (fetched)
- PyPA guide guides/writing-pyproject-toml §Static vs. dynamic metadata (https://raw.githubusercontent.com/pypa/packaging.python.org/main/source/guides/writing-pyproject-toml.rst) — 'many build backends can read the version from a ``__version__`` attribute in your code, a Git tag, or similar. In such cases, you should mark the field as dynamic' (fetched)
- PyPA guide guides/writing-pyproject-toml §Static vs. dynamic metadata (https://raw.githubusercontent.com/pypa/packaging.python.org/main/source/guides/writing-pyproject-toml.rst) — 'When a field is dynamic, it is the build backend's responsibility to fill it.' (fetched)
- PyPA guide guides/writing-pyproject-toml §Creating executable scripts (https://raw.githubusercontent.com/pypa/packaging.python.org/main/source/guides/writing-pyproject-toml.rst) — 'To install a command as part of your package, declare it in the ``[project.scripts]`` table.' (fetched)
- PEP 621 §Motivation (https://raw.githubusercontent.com/python/peps/main/peps/pep-0621.rst) — 'Encourage users to specify core metadata statically for speed, ease of specification, unambiguity, and deterministic consumption by build back-ends' (fetched)
- PEP 621 §Motivation (https://raw.githubusercontent.com/python/peps/main/peps/pep-0621.rst) — 'Provide a tool-agnostic way of specifying metadata for ease of learning and transitioning between build back-ends' (fetched)

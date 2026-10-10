---
title: A distributable Python package declares each dependency its code needs at run time in its package metadata, [project].dependencies or install_requires, and not only in a requirements file
rule_id: PY-110
domain: tooling
step: [implement, review]
applies_to: [python, library, build-config]
triggers: ['install_requires\s*=', '^\s*dependencies\s*=\s*\[', '^\s*[A-Za-z][A-Za-z0-9._-]*(\[[^\]]*\])?\s*(==|>=|~=|<=|!=|<|>)\s*[0-9]']
scope: base-compare
check_kind: semantic
severity_default: major
---

# A distributable Python package declares each dependency its code needs at run time in its package metadata, [project].dependencies or install_requires, and not only in a requirements file

## Thesis
A Python package built into a distribution lists what its code minimally needs to run correctly — each third-party distribution its installed modules import unconditionally — in its dependency metadata: the `dependencies` array of the `[project]` table in `pyproject.toml`, or setuptools' `install_requires`. A requirements file that lists the same distribution does not stand in for that entry.

## Rationale
`install_requires` is the setuptools keyword that specifies what a project minimally needs to run correctly, and when the project is installed by pip, it is the specification used to install the project's dependencies. In `pyproject.toml`, a project lists its dependencies in the `dependencies` array of `[project]`, and each string maps directly to a `Requires-Dist` entry of the distribution's metadata. A requirements file is not analyzed by pip during an install: pip uses it only when a user specifically installs it with `python -m pip install -r`. A dependency listed only there is therefore not installed when the distribution is installed. A source-level study of PyPI library releases identifies 15 kinds of configuration issues, finds 183,864 library releases with potential configuration issues, and reports that 68% of these issues can only be detected via the source-level check.

## Example
```python
bad:  import httpx                    # pkg/client.py
      httpx==0.27.0                   # requirements.txt
      dependencies = ["click>=8.1"]   # pyproject.toml [project]
good: import httpx                    # pkg/client.py
      dependencies = ["click>=8.1", "httpx>=0.27"]  # pyproject.toml [project]
```

## Limits
A dependency needed only for a specific feature of the package may be put in `optional-dependencies` rather than in `dependencies`. A requirements file that defines the requirements for a complete Python environment, often an exhaustive listing of pinned versions for repeatable installations of that environment, serves a different purpose from the metadata of a single project; the rule asks that the metadata carry the dependency, not that the requirements file drop it. How tightly the metadata constrains each version is outside the rule, and so is a project that is never built into a distribution.

## Validator
For each third-party import the change adds to the package's installed modules, and each line it adds to a requirements file, open the project's `pyproject.toml` `[project]` table, or `setup.py` and `setup.cfg`, at the base and at the head, and trace whether the distribution providing that module is listed in `dependencies`, `install_requires` or an `optional-dependencies` extra. Skip standard-library modules, the package's own modules, test files and tooling outside the package; treat an import guarded by `try`/`except ImportError` as an optional feature. Validator question: **Does the change make the package's installed code import a third-party distribution that no `dependencies`, `install_requires` or `optional-dependencies` entry of the package's metadata lists, at most in a requirements file?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-110`, severity major, `file`, `symbol`, `code` = the added import and the requirements-file line, if any, verbatim, `fix` = the distribution added to `[project].dependencies` or `install_requires` with its version range, `rationale` = pip installs a distribution's dependencies from its metadata and reads a requirements file only through `python -m pip install -r`).

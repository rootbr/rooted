---
title: The metadata of a Python distribution declares requires-python with the lowest Python version the code supports as its lower bound
rule_id: PY-112
domain: tooling
step: [implement, review]
applies_to: [python, build-config]
triggers: ['^\s*\[project\]', '^\s*requires-python\s*=', 'python_requires\s*=', 'install_requires\s*=']
scope: file
check_kind: semantic
severity_default: minor
---

# The metadata of a Python distribution declares requires-python with the lowest Python version the code supports as its lower bound

## Thesis
The `[project]` table of a Python project built into a distribution declares `requires-python` — `python_requires` in setuptools' `setup.cfg` or `setup()` — with a lower bound at the oldest Python version the code supports, such as `requires-python = ">=3.10"`.

## Rationale
`requires-python` declares the minimum version of Python a project supports, and the field corresponds to the `Requires-Python` core metadata field. Metadata 1.2+ installers such as pip match the current Python runtime against the required version in the package metadata; when they do not match, the installer attempts to install the last package distribution that supported that runtime, looking back through older versions of the package until it finds one with a matching Python version. The same mechanism can be used to drop support for older Python versions, by amending `Requires-Python` in the package metadata. In setuptools the minimum required Python version can be configured as `requires-python` in `[project]`, or as `python_requires` in `setup.cfg` or in `setup()`.

## Example
```python
bad:  # the package's modules use match statements
      setup(name="pkg", version="1.0",
            install_requires=["httpx>=0.27"])
good: setup(name="pkg", version="1.0", python_requires=">=3.10",
            install_requires=["httpx>=0.27"])
```

## Limits
The rule asks for a lower bound; an upper bound such as `requires-python = "<= 3.10"` is one to think twice about before applying, and the rule does not ask for it. Version ranges and exclusion rules that comply with the version specifiers specification, such as `">= 3.7, != 3.7.0, != 3.7.1"`, meet the rule as long as they carry the lower bound. Whether the code stays within the declared bound, and a project never built into a distribution, are outside the rule.

## Validator
Open the `[project]` table of the `pyproject.toml`, or the `setup()` call or the `[options]` section of `setup.cfg`, that the change adds or edits, and read `requires-python` or `python_requires`. When the field is present, check that it carries a lower bound on the Python version (a `>=`, `>` or `~=` clause, or an exact `==` version). Validator question: **Does the metadata of a project built into a distribution lack `requires-python` (or `python_requires`), or declare it with no lower bound on the Python version?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-112`, severity minor, `file`, `symbol`, `code` = the `[project]` header or the `requires-python` line verbatim, `fix` = `requires-python = ">=3.X"` in `[project]`, or `python_requires=">=3.X"` in `setup()`, with the oldest Python version the code supports, `rationale` = installers compare `Requires-Python` with the running interpreter to pick the last release that supports it, and a missing lower bound gives them nothing to compare).

---
title: Python code uses no syntax or standard-library feature introduced after the lowest Python version the project's requires-python admits
rule_id: PY-71
domain: tooling
step: [implement, review]
applies_to: [python]
triggers: [':=', 'except\s*\*', '^\s*(type\s+\w+(\[[^\]]*\])?\s*=|(def|class)\s+\w+\[)', ',\s*/\s*[,)]', '@final\b|\bimport\b.*\bfinal\b|\bExceptionGroup\b', '[\[{(]\s*\*\*?\w+([.]\w+)*\s+for\b']
scope: file
check_kind: mechanical
severity_default: major
---

# Python code uses no syntax or standard-library feature introduced after the lowest Python version the project's requires-python admits

## Thesis
Code a change adds uses no syntax and no standard-library name introduced in a Python version newer than the minimum the project declares in `requires-python`, the same floor the project gives Pylint as `py-version` and Ruff as `target-version`: f-strings need 3.6; the assignment expression operator `:=`, positional-only parameters and the `typing.final` decorator need 3.8; exception groups, `except*` and `ExceptionGroup`, need 3.11; generic type syntax, the `type` alias statement included, needs 3.12; unpacking in comprehensions needs 3.15. Such a line is rewritten in a form the floor supports, or the change raises `requires-python` to the feature's version.

## Rationale
`requires-python` in the `[project]` table declares the minimum version of Python a project supports, and Metadata 1.2+ installers such as pip compare the running interpreter with that required version before they install, so an interpreter at the floor is one the project declares it supports. A feature introduced in a later version is absent there. New syntax is a matter of the parser: a type alias defined with the `type` keyword is only accepted by the Python parser in Python 3.12 and later. A standard-library name exists only from the version that introduced it, as the `final` decorator exists from Python 3.8. Pylint's version-dependent checks take `py-version` as the minimum Python version and default to the version used to run Pylint; Ruff treats `requires-python = ">=3.8"` as identical to `target-version = "py38"`, lets `target-version` take precedence when both are specified, and proposes no change that uses a feature unavailable in that version.

## Example
```python
bad:  # pyproject.toml: requires-python = ">=3.10"
      type Vector = list[float]
good: # pyproject.toml: requires-python = ">=3.10"
      from typing import TypeAlias
      Vector: TypeAlias = list[float]
```

## Limits
A stub file can sometimes use a typing feature before it is available at runtime, as long as the stub uses no new syntax; stub files should be parseable in all Python versions that are supported by the implementation reading them and that are still supported by the CPython project. A standard-library name, unlike syntax, can sit inside a block gated on a `sys.version_info` comparison for the version that introduced it, since code can be conditionally executed based on the active Python version by comparing against the `sys.version_info` tuple; the gate does not make new syntax parse on an older version, because acceptance belongs to the parser, as with the `type` statement that only the 3.12 and later parser accepts. Where `target-version` and `requires-python` differ, Ruff checks against `target-version`, which takes precedence.

## Validator
Read the floor from `requires-python` in the `[project]` table of pyproject.toml, or from Ruff's `target-version` where it is set. Grep the added lines for `:=`, `except*`, `ExceptionGroup`, `final` imported from `typing`, a `/` in a parameter list, a `type X = ...` statement or a `def`/`class` name followed by a `[...]` type-parameter list, and a `*` or `**` unpacking at the head of a comprehension; check f-strings only where the floor is below 3.6. Map each hit to its version (f-string 3.6; `:=`, positional-only `/` and `typing.final` 3.8; `except*` and `ExceptionGroup` 3.11; generic type syntax and the `type` statement 3.12; comprehension unpacking 3.15) and compare it with the floor. Open pyproject.toml in the change to see whether the floor is raised. Skip a `.pyi` stub that uses a typing feature without new syntax, and a standard-library name reached only inside a `sys.version_info` gate for its version; such a gate does not clear syntax. Validator question: **Does an added line use syntax or a standard-library name introduced in a Python version above the floor the project declares, with the change leaving that floor unraised?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-71`, severity major, `file`, `symbol`, `code` = the added line that uses the feature, verbatim, `fix` = the line rewritten in Python the floor supports, such as `Vector: TypeAlias = list[float]` for `type Vector = list[float]`, or `requires-python` raised to the feature's version, `rationale` = the feature, the Python version that introduced it and the declared floor).

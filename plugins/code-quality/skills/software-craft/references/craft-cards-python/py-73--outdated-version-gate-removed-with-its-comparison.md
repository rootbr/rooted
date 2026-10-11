---
title: A sys.version_info branch that runs only on Python versions below the project's requires-python minimum is removed together with its comparison
rule_id: PY-73
domain: tooling
step: [refactor, review]
applies_to: [python]
triggers: ['\bsys[.]version_info\s*(<|<=|>=|>|==|!=)\s*\(', '\bsys[.]version_info\s*\[\s*:\s*\d\s*\]\s*(<|<=|>=|>|==|!=)', '\(\s*\d+\s*(,\s*\d+\s*)*\)\s*(<|<=|>=|>)\s*sys[.]version_info']
scope: file
check_kind: mechanical
severity_default: minor
---

# A sys.version_info branch that runs only on Python versions below the project's requires-python minimum is removed together with its comparison

## Thesis
When a conditional block is gated on a `sys.version_info` comparison that selects only Python versions older than the project's minimum supported version (the floor declared in `requires-python`, or in Ruff's `target-version` where that is set), the comparison and the outdated branch are removed and the code for the supported versions stays, unconditional.

## Rationale
In Python, code can be conditionally executed based on the active Python version by comparing against the `sys.version_info` tuple. `requires-python` declares the minimum version of Python a project supports; Metadata 1.2+ installers such as pip match the running interpreter against it, and Ruff treats `requires-python = ">=3.8"` as identical to `target-version = "py38"`, with `target-version` taking precedence when both are specified. A block executed only for versions older than that minimum is therefore an unreachable version block on every supported interpreter. Removing such a block is an unsafe fix, because the removal takes away all code, comments and annotations within the unreachable block.

## Example
```python
bad:  # pyproject.toml: requires-python = ">=3.9"
      if sys.version_info < (3, 8):
          from typing_extensions import Literal
      else:
          from typing import Literal
good: # pyproject.toml: requires-python = ">=3.9"
      from typing import Literal
```

## Limits
A branch that also runs on a version at or above the minimum is live code and stays; the rule reaches only a block executed for versions older than the minimum supported version. The floor holds where the package is installed with pip or another installer that supports the Metadata 1.2 specification, which the workflow of dropping older Python versions requires.

## Validator
Read the floor: Ruff's `target-version` where the configuration sets it, otherwise `requires-python` in the `[project]` table of pyproject.toml. Grep the file for `sys.version_info` compared with a tuple, a `sys.version_info[:n]` slice compared with a tuple, and a tuple compared with `sys.version_info`. For each gate, work out the versions its branch runs on: the body of `if sys.version_info < (3, 8):` runs only below 3.8, and so does the `else` of `if sys.version_info >= (3, 8):`. Compare that range with the floor; a branch that reaches any version at or above the floor is no finding. Validator question: **Does a branch gated on `sys.version_info` run only on Python versions older than the floor the project declares?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-73`, severity minor, `file`, `symbol`, `code` = the `sys.version_info` comparison line and the outdated branch, verbatim, `fix` = the code for the supported versions alone, unconditional, such as `from typing import Literal`, with any comment from the removed block that still applies kept, `rationale` = the versions the branch runs on and the declared minimum).

## Source
- Ruff UP036 outdated-version-block (astral-sh/ruff crates/ruff_linter/src/rules/pyupgrade/rules/outdated_version_block.rs) — 'Checks for conditional blocks gated on `sys.version_info` comparisons that are outdated for the minimum supported Python version.'; 'code can be conditionally executed based on the active Python version by comparing against the `sys.version_info` tuple'; 'If a code block is only executed for Python versions older than the minimum supported version, it should be removed.'; 'fix is marked as unsafe because it will remove all code, comments, and annotations within unreachable version blocks' (fetched)
- Ruff setting target-version (astral-sh/ruff crates/ruff_workspace/src/options.rs) — '`project.requires-python` instead'; 'treats the following as identical to `target-version = "py38"`'; 'If both are specified, `target-version` takes precedence over' (fetched)
- PyPA guide Writing your pyproject.toml §requires-python (pypa/packaging.python.org source/guides/writing-pyproject-toml.rst) — 'This lets you declare the minimum version of Python that you support' (fetched)
- PyPA guide Dropping support for older Python versions §Dropping support for older Python versions (pypa/packaging.python.org source/guides/dropping-older-python-versions.rst) — 'Metadata 1.2+ installers, such as Pip, will adhere to this specification by matching the current Python runtime and comparing it with the required version in the package metadata.'; 'This workflow requires that the user installing the package uses Pip' (fetched)

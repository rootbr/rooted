---
title: A Python string enumeration on a 3.11 or later minimum version derives from StrEnum, not from both str and Enum
rule_id: PY-139
domain: design
step: [implement, refactor, review]
applies_to: [python]
triggers: ['^\s*class\s+\w+\(\s*str\s*,\s*(?:enum[.])?Enum\s*\)', '^\s*class\s+\w+\(\s*(?:enum[.])?Enum\s*,\s*str\s*\)']
scope: file
check_kind: semantic
severity_default: minor
---

# A Python string enumeration on a 3.11 or later minimum version derives from StrEnum, not from both str and Enum

## Thesis
In a project whose minimum supported Python is 3.11 or later, an enumeration whose members are strings derives from `enum.StrEnum` rather than from both `str` and `enum.Enum`, unless code relies on the enum-and-member-name output that the mixin gives.

## Rationale
Since Python 3.11, `Enum.__format__`, the default for `format()`, `str.format()` and f-strings, always produces the same result as `Enum.__str__`: for enums inheriting from `ReprEnum` it is the member's value, and for all other enums it is the enum and member name, such as `Color.RED`. `ReprEnum` is used by `IntEnum`, `StrEnum` and `IntFlag` to keep the `str()` of the mixed-in type. A member of a class deriving from both `str` and `Enum`, such as `Foo.BAR = 'bar'`, formats as `bar` on Python 3.10 and as `Foo.BAR` on Python 3.11. `StrEnum`, added in Python 3.11, has members that can be used as (and must be) strings, and under it `f'{Foo.BAR}'` gives `bar`.

## Example
```python
bad:  class Color(str, Enum):
          RED = 'red'
      label = f'{Color.RED}'  # 'Color.RED' on 3.11 and later
good: class Color(StrEnum):
          RED = 'red'
      label = f'{Color.RED}'  # 'red'
```

## Limits
Code that relies on the Python 3.11 output of the mixin, the enum and member name, keeps the mixin, since migrating to `StrEnum` introduces a behavior change for it. A project that still supports a Python older than 3.11 has no `StrEnum` to derive from, since `StrEnum` was added in 3.11.

## Validator
For each class in the hunk whose bases are `str` and `Enum` (or `enum.Enum`) in either order, read the project's minimum supported Python — `requires-python` in `pyproject.toml`, or `target-version` in the Ruff configuration. Search the file and its callers for `format()`, `str.format()` or f-string uses of the members and for code that expects their formatted output to read `ClassName.MEMBER`. Validator question: **Does a class in the diff derive from both `str` and `Enum` in a project whose minimum supported Python is 3.11 or later, with no code relying on the enum-and-member-name output?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-139`, severity minor, `file`, `symbol`, `code` = the `class` line with the `str` and `Enum` bases, `fix` = the class deriving from `StrEnum`, such as `class Color(StrEnum):`, with `from enum import StrEnum`, `rationale` = the minimum supported Python and the formatted output a member gives under the mixin against under `StrEnum`).

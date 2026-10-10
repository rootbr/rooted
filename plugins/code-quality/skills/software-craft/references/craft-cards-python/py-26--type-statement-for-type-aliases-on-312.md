---
title: On a project whose minimum Python is 3.12 or later, a type alias is declared with the type statement rather than a TypeAlias annotation or TypeAliasType call, unless the alias is also used as a value at run time
rule_id: PY-26
domain: code
step: [implement, refactor]
applies_to: [python, static-types]
triggers: [':\s*(typing[.])?TypeAlias\s*=', '\bTypeAliasType\(', '^\s*from\s+typing(_extensions)?\s+import\s+.*\bTypeAlias\b']
scope: callers
check_kind: mechanical
severity_default: suggestion
---

# On a project whose minimum Python is 3.12 or later, a type alias is declared with the type statement rather than a TypeAlias annotation or TypeAliasType call, unless the alias is also used as a value at run time

## Thesis
On a project whose minimum supported Python is 3.12 or later, a type alias is declared with the `type` statement (`type Vector = list[float]`, `type Pair[T] = tuple[T, T]`) rather than as an assignment annotated with `TypeAlias` or a `TypeAliasType(...)` call. An alias the code also uses as a value at run time, such as the second argument of `isinstance()`, keeps its assignment form.

## Rationale
The `type` statement was introduced in Python 3.12 by PEP 695 for defining type aliases; it is easier to read and gives cleaner support for generics, since one statement can replace both the `TypeVar` and the `TypeAlias` declarations of a generic alias. The typing documentation deprecates `TypeAlias` in favour of the `type` statement, which creates instances of `TypeAliasType` and natively supports forward references; removal of `TypeAlias` is not currently planned, and users are encouraged to migrate. The value of a `type` alias is evaluated lazily: names used in its definition are not resolved until its `__value__` attribute is accessed. At run time the statement creates a `typing.TypeAliasType` instance, which cannot stand in for the value on its right-hand side, so where a simple old-style alias can serve as the second argument of `isinstance()`, a `type` alias there always raises `TypeError`. The statement infers the variance of its type parameters, while a `TypeVar` declares it with the `covariant` and `contravariant` keywords, so rewriting an alias over such a `TypeVar` may change the variance of its parameters.

## Example
```python
bad:  from typing import TypeAlias, TypeAliasType
      Vector: TypeAlias = list[float]
      Matrix = TypeAliasType("Matrix", list[Vector])
good: type Vector = list[float]
      type Matrix = list[Vector]
      Number = int | float  # also passed to isinstance()
```

## Limits
The separating condition is the project's minimum supported Python. The `type` statement exists from Python 3.12, and the checks that require it are bound to that version: such a check raises an issue only when the analysed project's Python version is set to 3.12 or higher. Below 3.12 the `TypeAlias` annotation is the available form: it is particularly useful on older Python versions for aliases that use forward references, and there an alias is annotated `typing.TypeAlias` to distinguish it from a non-type global variable. An alias passed to `isinstance()` or otherwise used as a value keeps the assignment. The automatic rewrite is unsafe, since it can change runtime behaviour and type-checking semantics, so an alias over a `TypeVar` declared `covariant` or `contravariant` is converted with a check of the inferred variance. Where the project's Python version is not set to 3.12 or higher, the rule does not apply.

## Validator
Establish the project's minimum supported Python from `requires-python` in `pyproject.toml` or the `target-version` or `python_version` setting of Ruff or mypy; when it is below 3.12 or cannot be established, stop. Grep the file for `: TypeAlias =`, `TypeAliasType(` and an import of `TypeAlias`. For each alias so declared, search the file and its importers for a use of the alias as a value: an argument of `isinstance()` or `issubclass()`, a call of the alias, an attribute read on it. Note any `TypeVar` in the alias declared `covariant` or `contravariant`. Validator question: **On a project whose minimum supported Python is 3.12 or later, does the file declare a type alias with a `TypeAlias` annotation or a `TypeAliasType(...)` call that the code never uses as a value at run time?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-26`, severity suggestion, `file`, `symbol`, `code` = the alias declaration quoted verbatim, `fix` = the same alias as a `type` statement, such as `type Vector = list[float]` or `type Pair[T] = tuple[T, T]`, with a variance-declared `TypeVar` named for a hand check, `rationale` = `TypeAlias` is deprecated from Python 3.12 in favour of the `type` statement, whose value is evaluated lazily and which natively supports forward references).

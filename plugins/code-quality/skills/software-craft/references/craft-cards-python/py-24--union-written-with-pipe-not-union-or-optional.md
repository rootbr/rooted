---
title: A union annotation is written X | Y and an optional one X | None rather than Union or Optional wherever the minimum Python is 3.10 or the module defers annotations that nothing evaluates at run time
rule_id: PY-24
domain: code
step: [implement, refactor, review]
applies_to: [python, static-types]
triggers: ['\b(typing[.])?Optional\[', '\b(typing[.])?Union\[', '^\s*from\s+typing\s+import\s+.*\b(Optional|Union)\b']
scope: file
check_kind: mechanical
severity_default: suggestion
---

# A union annotation is written X | Y and an optional one X | None rather than Union or Optional wherever the minimum Python is 3.10 or the module defers annotations that nothing evaluates at run time

## Thesis
On a project whose minimum supported Python is 3.10 or later, a union annotation is written `X | Y` and a type that admits `None` is written `X | None`, in place of `Union[X, Y]` and `Optional[X]`. On an older minimum version the same holds in a module with `from __future__ import annotations`, unless the code relies on annotations evaluated at run time, directly or through a library such as Pydantic.

## Rationale
Starting with Python 3.10 (PEP 604) union types can be spelled with the `|` operator; `Union[X, Y]` is equivalent to `X | Y`, the shorthand is the recommended spelling, and it is more concise and readable than the `typing.Union` and `typing.Optional` syntaxes. `Optional[X]` is equivalent to `X | None`, which is not the same concept as an optional argument, one that has a default: a parameter annotated `Optional` is still a required argument when no default value is set, and annotating it `X | None` makes the intention clear. Before 3.10 an evaluated `int | str` raises `TypeError: unsupported operand type(s) for |: 'type' and 'type'`; with `from __future__ import annotations` the annotations are not evaluated at run time, so the shorthand is usable there.

## Example
```python
bad:  def find(name: str, default: Optional[User]) -> Union[User, None]:
          return registry.get(name, default)
good: def find(name: str, default: User | None) -> User | None:
          return registry.get(name, default)
```

## Limits
`Union` and `Optional` remain valid and equivalent: the `|` expressions are recommended in new Python 3.10+ code and the older `Optional` and `Union` syntaxes are still allowed, so the rule covers the annotations a change writes, not a sweep of the ones it leaves untouched. On a minimum version below 3.10, code that relies on runtime type annotations, directly or through a library such as Pydantic, keeps `Union` and `Optional`. A union outside annotations, such as in a type alias not defined with the `type` statement or in a base class, can still require string literals or result in errors even with the future import, and is outside the rule.

## Validator
Read the project's minimum Python from `requires-python` in `pyproject.toml`, `python_requires` in `setup.cfg` or `setup.py`, or the type checker's or linter's target version. Grep the annotations the hunk adds or changes for `Optional[` and `Union[`. With a minimum of 3.10 or later, each is the finding. With an older minimum, open the module and flag only when it has `from __future__ import annotations`, the use is inside an annotation, and nothing in the project evaluates those annotations at run time, such as a Pydantic model or a call to `typing.get_type_hints()`. Validator question: **Does an annotation the hunk adds or changes write `Union[...]` or `Optional[...]` where the minimum Python is 3.10 or later, or where the module has `from __future__ import annotations` and nothing evaluates its annotations at run time?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-24`, severity suggestion, `file`, `symbol`, `code` = the annotation with `Union` or `Optional`, `fix` = the same annotation written with `|`, `X | None` for `Optional[X]`, in Python, `rationale` = names the construct, its `|` spelling and the project's minimum Python or its future import).

## Source
- CPython Doc/library/typing.rst §Union (python/cpython Doc/library/typing.rst) — "Union type; ``Union[X, Y]`` is equivalent to ``X | Y`` and means either X or Y." (fetched)
- CPython Doc/library/typing.rst §Union (python/cpython Doc/library/typing.rst) — "To define a union, use e.g. ``Union[int, str]`` or the shorthand ``int | str``. Using that shorthand is recommended." (fetched)
- CPython Doc/library/typing.rst §Optional (python/cpython Doc/library/typing.rst) — "``Optional[X]`` is equivalent to ``X | None`` (or ``Union[X, None]``)." (fetched)
- CPython Doc/library/typing.rst §Optional (python/cpython Doc/library/typing.rst) — "Note that this is not the same concept as an optional argument, which is one that has a default." (fetched)
- Ruff UP007 non-pep604-annotation-union (astral-sh/ruff crates/ruff_linter/src/rules/pyupgrade/rules/use_pep604_annotation.rs) — "[PEP 604] introduced a new syntax for union type annotations based on the `|` operator. This syntax is more concise and readable than the previous `typing.Union` and `typing.Optional` syntaxes." (fetched)
- Ruff UP007 non-pep604-annotation-union (astral-sh/ruff crates/ruff_linter/src/rules/pyupgrade/rules/use_pep604_annotation.rs) — "This rule is enabled when targeting Python 3.10 or later (see: [`target-version`]). By default, it's _also_ enabled for earlier Python versions if `from __future__ import annotations` is present, as `__future__` annotations are not evaluated at runtime." (fetched)
- Ruff UP045 non-pep604-annotation-optional (astral-sh/ruff crates/ruff_linter/src/rules/pyupgrade/rules/use_pep604_annotation.rs) — "If your code relies on runtime type annotations (either directly or via a library like Pydantic), you can disable this behavior for Python versions prior to 3.10 by setting [`lint.pyupgrade.keep-runtime-typing`] to `true`." (fetched)
- Pylint consider-alternative-union-syntax (R6003) (pylint-dev/pylint doc/data/messages/c/consider-alternative-union-syntax/details.rst) — "``typing.Optional`` can also cause confusion in annotated function arguments, since an argument annotated as ``Optional`` is still a *required* argument when a default value is not set. Explicitly annotating such arguments with ``type | None`` makes the intention clear." (fetched)
- SonarSource python S6546 (SonarSource/sonar-python python-checks/src/main/resources/org/sonar/l10n/py/rules/python/S6546.html) — "This syntax has the same functionality as typing.Union, but it is more concise and easier to read." (fetched)
- mypy docs §Using X | Y syntax for Unions (python/mypy docs/source/runtime_troubles.rst) — "Starting with Python 3.10 (:pep:`604`), you can spell union types as" (fetched)
- mypy docs §Using X | Y syntax for Unions (python/mypy docs/source/runtime_troubles.rst) — "(if evaluated, ``int | str`` will raise ``TypeError: unsupported operand type(s) for |: 'type' and 'type'``)" (fetched)
- mypy docs §Future annotations import (python/mypy docs/source/runtime_troubles.rst) — "Even with the ``__future__`` import, there are some scenarios that could still require string literals or result in errors, typically involving use of forward references or generics in:" (fetched)
- mypy docs §Future annotations import (python/mypy docs/source/runtime_troubles.rst) — "not defined using the ``type`` statement;" (fetched)
- mypy docs §Future annotations import (python/mypy docs/source/runtime_troubles.rst) — "base classes." (fetched)
- mypy docs §Using X | Y syntax for Unions (python/mypy docs/source/runtime_troubles.rst) — "if you use ``from __future__ import annotations``, mypy will understand this syntax in annotations, string literal types, type comments and stub files." (fetched)
- Google Python Style Guide §3.19.5 NoneType (google/styleguide pyguide.md) — "You can use `|` union type expressions (recommended in new Python 3.10+ code), or the older `Optional` and `Union` syntaxes." (fetched)

---
title: A module whose annotations use builtin generics such as list[int] while its project supports Python 3.8, or X | Y unions while it supports Python 3.9 or earlier, starts with from __future__ import annotations
rule_id: PY-25
domain: code
step: [implement, review]
applies_to: [python, static-types]
triggers: ['\b(list|dict|set|frozenset|tuple|type)\[', ':\s*[\w.\[\], ]+\|\s*[\w.\[\]]+', '->\s*[^:]*\|']
scope: file
check_kind: mechanical
severity_default: major
---

# A module whose annotations use builtin generics such as list[int] while its project supports Python 3.8, or X | Y unions while it supports Python 3.9 or earlier, starts with from __future__ import annotations

## Thesis
A module that writes PEP 585 builtin generics (`list[int]`, `dict[str, int]`) in annotations while the project still supports a Python version before 3.9, or PEP 604 unions (`int | None`) while it supports a version before 3.10, starts with `from __future__ import annotations`, which is available from Python 3.7.

## Rationale
Many runtime typing problems come from Python trying to evaluate annotations. The builtin generics are available only on Python 3.9 and higher and the `|` union only on 3.10 and higher, so without the future import these annotations cause runtime errors on the older versions; an evaluated `int | str` raises `TypeError: unsupported operand type(s) for |: 'type' and 'type'`. With `from __future__ import annotations` the interpreter no longer evaluates annotations, which amounts to turning every function and variable annotation into a string literal, so the module stays compatible with both past and future Python versions while mypy still understands the syntax in annotations.

## Example
```python
bad:  # pyproject.toml: requires-python = ">=3.8"
      def load(path: str | None) -> dict[str, int] | None:
          return parse(path) if path else None
good: from __future__ import annotations
      def load(path: str | None) -> dict[str, int] | None:
          return parse(path) if path else None
```

## Limits
The import defers function and variable annotations only: type aliases not defined with the `type` statement, type narrowing, type definitions such as `TypeVar`, `NewType` or `NamedTuple`, and base classes can still require string literals or result in errors on those versions. Libraries that evaluate annotations dynamically, through `typing.get_type_hints` or `eval`, call for care: an annotation that raises when evaluated, such as PEP 604 syntax on Python 3.9, can still raise through them. Adding the import may change the semantics of the program, which is why a linter marks that fix unsafe. A project whose minimum is 3.10 or later needs no import for this syntax.

## Validator
Read the project's minimum Python from `requires-python` in `pyproject.toml`, `python_requires` in `setup.cfg` or `setup.py`, or the type checker's or linter's target version; stop when it is 3.10 or later. Grep the file's annotations for subscripted builtins (`list[`, `dict[`, `set[`, `frozenset[`, `tuple[`, `type[`) when the minimum is below 3.9, and for `|` between types when it is below 3.10. Open the top of the module for `from __future__ import annotations`. Validator question: **Does the module annotate with a builtin generic while the minimum Python is below 3.9, or with an `X | Y` union while it is below 3.10, without `from __future__ import annotations`?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-25`, severity major, `file`, `symbol`, `code` = the annotation with the newer syntax as the diff writes it, `fix` = `from __future__ import annotations` added at the top of the module, in Python, `rationale` = names the syntax, the Python version it needs and the project's minimum Python).

## Source
- Ruff FA102 future-required-type-annotation (astral-sh/ruff crates/ruff_linter/src/rules/flake8_future_annotations/rules/future_required_type_annotation.rs) — "Using PEP 585 and PEP 604 style annotations without a `from __future__ import annotations` import will cause runtime errors on Python versions prior to 3.9 and 3.10, respectively." (fetched)
- Ruff FA102 future-required-type-annotation (astral-sh/ruff crates/ruff_linter/src/rules/flake8_future_annotations/rules/future_required_type_annotation.rs) — "By adding the `__future__` import, the interpreter will no longer interpret annotations at evaluation time, making the code compatible with both past and future Python versions." (fetched)
- Ruff FA102 future-required-type-annotation (astral-sh/ruff crates/ruff_linter/src/rules/flake8_future_annotations/rules/future_required_type_annotation.rs) — "This rule's fix is marked as unsafe, as adding `from __future__ import annotations` may change the semantics of the program." (fetched)
- Ruff FA102 future-required-type-annotation (astral-sh/ruff crates/ruff_linter/src/rules/flake8_future_annotations/rules/future_required_type_annotation.rs) — "As such, this rule will only flag such usages if your project targets Python 3.9 or below." (fetched)
- Ruff FA100 future-rewritable-type-annotation (astral-sh/ruff crates/ruff_linter/src/rules/flake8_future_annotations/rules/future_rewritable_type_annotation.rs) — "However, these annotations are only available on Python 3.9 and higher, _unless_ the `from __future__ import annotations` import is present." (fetched)
- mypy docs §Using X | Y syntax for Unions (python/mypy docs/source/runtime_troubles.rst) — "(if evaluated, ``int | str`` will raise ``TypeError: unsupported operand type(s) for |: 'type' and 'type'``)" (fetched)
- mypy docs §Using X | Y syntax for Unions (python/mypy docs/source/runtime_troubles.rst) — "if you use ``from __future__ import annotations``, mypy will understand this syntax in annotations, string literal types, type comments and stub files." (fetched)
- mypy docs §Future annotations import (python/mypy docs/source/runtime_troubles.rst) — "Many of the issues described here are caused by Python trying to evaluate annotations." (fetched)
- mypy docs §Future annotations import (python/mypy docs/source/runtime_troubles.rst) — "This behaviour is made available in Python 3.7 and later through the use of ``from __future__ import annotations``." (fetched)
- mypy docs §Future annotations import (python/mypy docs/source/runtime_troubles.rst) — "This can be thought of as automatic string literal-ification of all function and variable annotations." (fetched)
- mypy docs §Future annotations import (python/mypy docs/source/runtime_troubles.rst) — "Even with the ``__future__`` import, there are some scenarios that could still require string literals or result in errors, typically involving use of forward references or generics in:" (fetched)
- mypy docs §Future annotations import (python/mypy docs/source/runtime_troubles.rst) — "not defined using the ``type`` statement;" (fetched)
- mypy docs §Future annotations import (python/mypy docs/source/runtime_troubles.rst) — ":ref:`type narrowing <type-narrowing>`;" (fetched)
- mypy docs §Future annotations import (python/mypy docs/source/runtime_troubles.rst) — "type definitions (see :py:class:`~typing.TypeVar`, :py:class:`~typing.NewType`, :py:class:`~typing.NamedTuple`);" (fetched)
- mypy docs §Future annotations import (python/mypy docs/source/runtime_troubles.rst) — "base classes." (fetched)
- mypy docs §Future annotations import (python/mypy docs/source/runtime_troubles.rst) — "Some libraries may have use cases for dynamic evaluation of annotations, for instance, through use of ``typing.get_type_hints`` or ``eval``. If your annotation would raise an error when evaluated (say by using :pep:`604` syntax with Python 3.9), you may need to be careful when using such libraries." (fetched)

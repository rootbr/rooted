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

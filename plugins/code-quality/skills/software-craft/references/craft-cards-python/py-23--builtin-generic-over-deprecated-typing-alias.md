---
title: An annotation uses the builtin or collections.abc generic rather than the typing alias PEP 585 deprecated, such as List, Dict or Tuple, wherever the minimum Python is 3.9 or the module defers annotations that nothing evaluates at run time
rule_id: PY-23
domain: code
step: [implement, refactor, review]
applies_to: [python, static-types]
triggers: ['(?<![\w.])(typing[.])?(List|Dict|Set|FrozenSet|Tuple|Type|DefaultDict|Deque)\[', '^\s*from\s+typing\s+import\s+.*\b(List|Dict|Set|FrozenSet|Tuple|Type|DefaultDict|Deque)\b', '\btyping[.](Iterable|Iterator|Sequence|Mapping|MutableMapping|Callable|Generator|AsyncIterator|Awaitable|AbstractSet)\[']
scope: file
check_kind: mechanical
severity_default: minor
---

# An annotation uses the builtin or collections.abc generic rather than the typing alias PEP 585 deprecated, such as List, Dict or Tuple, wherever the minimum Python is 3.9 or the module defers annotations that nothing evaluates at run time

## Thesis
On a project whose minimum supported Python is 3.9 or later, an annotation uses the builtin generic (`list[int]`, `dict[str, int]`, `tuple[int, ...]`, `type[T]`) or the `collections.abc` class (`Iterable[str]`, `Mapping[str, int]`, `Sequence[int]`) in place of its `typing` alias (`List`, `Dict`, `Tuple`, `Type`, `typing.Iterable` and the other aliases of standard classes), which are deprecated as of Python 3.9. On an older minimum version the same holds in a module with `from __future__ import annotations`, unless the code relies on annotations evaluated at run time, directly or through a library such as Pydantic.

## Rationale
From Python 3.9 the builtin collections and the `collections.abc` classes accept subscripting, so the `typing` aliases became redundant and importing them from `typing` is deprecated. To minimize the runtime impact of typing, the deprecation generates no `DeprecationWarning`: the interpreter stays silent and only a type checker or linter reports the alias, and type checkers are encouraged to flag the deprecated types when the program targets a minimum Python version of 3.9 or newer. The builtin types have the same functionality as their `typing` counterparts and are more readable; to annotate arguments, an abstract collection type such as `Mapping` is preferred over `dict` or `typing.Dict`. Before 3.9 the builtin form is available only when `from __future__ import annotations` is present, because those annotations are not evaluated at run time.

## Example
```python
bad:  from typing import Dict, List
      def tally(words: List[str]) -> Dict[str, int]:
          return dict(Counter(words))
good: from collections.abc import Iterable
      def tally(words: Iterable[str]) -> dict[str, int]:
          return dict(Counter(words))
```

## Limits
The aliases still work: their removal is not currently planned, and they remain in `typing` without deprecation warnings until at least Python 3.14; the rule covers the annotations a change adds or changes. On a minimum version below 3.9, code that relies on runtime type annotations, directly or through a library such as Pydantic, keeps the `typing` alias, and so does a use outside annotations, such as a type alias or a `cast`, which puts the type in runtime context where the future import does not reach. Special forms that alias no standard class, such as `Any` or `Literal`, are outside the rule; the rule covers the aliases of pre-existing standard library classes.

## Validator
Read the project's minimum Python from `requires-python` in `pyproject.toml`, `python_requires` in `setup.cfg` or `setup.py`, or the type checker's or linter's target version. Grep the hunk for a subscripted `typing` alias (`List[`, `Dict[`, `Set[`, `Tuple[`, `Type[`, `typing.Iterable[` and kin) and for its `from typing import` line. With a minimum of 3.9 or later, an annotation using one is the finding. With an older minimum, open the module and flag only when it has `from __future__ import annotations`, the use is inside an annotation, and nothing in the project evaluates those annotations at run time, such as a Pydantic model or a call to `typing.get_type_hints()`. Validator question: **Does an annotation the hunk adds or changes use a deprecated `typing` alias of a builtin or `collections.abc` class where the minimum Python is 3.9 or later, or where the module has `from __future__ import annotations` and nothing evaluates its annotations at run time?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-23`, severity minor, `file`, `symbol`, `code` = the annotation with the alias and its `from typing import` line, `fix` = the annotation with the builtin or `collections.abc` generic, in Python, `rationale` = names the alias, its replacement and the project's minimum Python or its future import).

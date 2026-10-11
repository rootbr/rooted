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

## Source
- CPython Doc/library/typing.rst §Deprecated aliases (python/cpython Doc/library/typing.rst) — "However, the aliases became redundant in Python 3.9 when the corresponding pre-existing classes were enhanced to support ``[]``" (fetched)
- CPython Doc/library/typing.rst §Deprecated aliases (python/cpython Doc/library/typing.rst) — "The redundant types are deprecated as of Python 3.9. However, while the aliases may be removed at some point, removal of these aliases is not currently planned. As such, no deprecation warnings are currently issued by the interpreter for these aliases." (fetched)
- CPython Doc/library/typing.rst §Deprecated aliases (python/cpython Doc/library/typing.rst) — "without deprecation warnings until at least Python 3.14." (fetched)
- CPython Doc/library/typing.rst §Deprecated aliases (python/cpython Doc/library/typing.rst) — "Type checkers are encouraged to flag uses of the deprecated types if the program they are checking targets a minimum Python version of 3.9 or newer." (fetched)
- CPython Doc/library/typing.rst §Deprecated aliases (python/cpython Doc/library/typing.rst) — "This module defines several deprecated aliases to pre-existing standard library classes." (fetched)
- CPython Doc/library/typing.rst §Aliases to built-in types (python/cpython Doc/library/typing.rst) — "Note that to annotate arguments, it is preferred to use an abstract collection type such as :class:`~collections.abc.Mapping` rather than to use :class:`dict` or :class:`!typing.Dict`." (fetched)
- PEP 585 §Implementation (python/peps peps/pep-0585.rst) — "Importing those from ``typing`` is deprecated." (fetched)
- PEP 585 §Implementation (python/peps peps/pep-0585.rst) — "and the intention to minimize the runtime impact of typing, this deprecation will not generate DeprecationWarnings." (fetched)
- mypy docs §Future annotations import (python/mypy docs/source/runtime_troubles.rst) — "Even with the ``__future__`` import, there are some scenarios that could still require string literals or result in errors, typically involving use of forward references or generics in:" (fetched)
- PEP 585 §Implementation (python/peps peps/pep-0585.rst) — "certain features of typing like type aliases or casting require putting types outside of annotations, in runtime context." (fetched)
- Ruff UP006 non-pep585-annotation (astral-sh/ruff crates/ruff_linter/src/rules/pyupgrade/rules/use_pep585_annotation.rs) — "This rule is enabled when targeting Python 3.9 or later (see: [`target-version`]). By default, it's _also_ enabled for earlier Python versions if `from __future__ import annotations` is present, as `__future__` annotations are not evaluated at runtime." (fetched)
- Ruff UP006 non-pep585-annotation (astral-sh/ruff crates/ruff_linter/src/rules/pyupgrade/rules/use_pep585_annotation.rs) — "If your code relies on runtime type annotations (either directly or via a library like Pydantic), you can disable this behavior for Python versions prior to 3.9 by setting [`lint.pyupgrade.keep-runtime-typing`] to `true`." (fetched)
- Ruff FA100 future-rewritable-type-annotation (astral-sh/ruff crates/ruff_linter/src/rules/flake8_future_annotations/rules/future_rewritable_type_annotation.rs) — "However, these annotations are only available on Python 3.9 and higher, _unless_ the `from __future__ import annotations` import is present." (fetched)
- Pylint deprecated-typing-alias (W6001) (pylint-dev/pylint pylint/extensions/typing.py, message description) — "Emitted when a deprecated typing alias is used." (fetched)
- Pylint consider-using-alias (R6002) (pylint-dev/pylint pylint/extensions/typing.py, message description) — "Only emitted if 'runtime-typing=no' and a deprecated typing alias is used in a type annotation context in Python 3.7 or 3.8." (fetched)
- SonarSource python S6545 (SonarSource/sonar-python python-checks/src/main/resources/org/sonar/l10n/py/rules/python/S6545.html) — "These built-in types have the same functionality as their counterparts in the typing module, but are more readable and idiomatic." (fetched)

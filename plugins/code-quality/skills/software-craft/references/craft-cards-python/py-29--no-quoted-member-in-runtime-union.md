---
title: An X | Y union the interpreter evaluates at run time has no quoted member, and a forward reference in it quotes the whole union or relies on from __future__ import annotations
rule_id: PY-29
domain: code
step: [implement, review]
applies_to: [python, static-types]
triggers: ['[\x27"][A-Za-z_][\w.]*[\x27"]\s*\|', '\|\s*[\x27"][A-Za-z_][\w.]*[\x27"]']
scope: file
check_kind: mechanical
severity_default: major
---

# An X | Y union the interpreter evaluates at run time has no quoted member, and a forward reference in it quotes the whole union or relies on from __future__ import annotations

## Thesis
An `X | Y` union that the interpreter evaluates at run time has no quoted member such as `"Node" | None`. A forward reference in such a union quotes the entire union (`"Node | None"`) or, in an annotation, relies on `from __future__ import annotations`; in a type alias assigned without the `type` statement, in a base class or in a `TypeVar` or `NewType` definition, the future import may still leave string literals required, so the entire union is quoted.

## Rationale
PEP 604 adds the operator `type.__or__()`, so `int | str` is an expression the interpreter evaluates through that operator. Annotations can typically be wrapped in strings to avoid runtime evaluation, but a string member within an `X | Y` union causes a runtime error. `from __future__ import annotations` acts as an automatic string literal-ification of all function and variable annotations and so disables their runtime evaluation entirely. It does not reach every evaluated expression: forward references in type aliases not defined with the `type` statement, in type definitions such as `TypeVar`, `NewType` and `NamedTuple`, and in base classes could still require string literals or result in errors. Before Python 3.14 the annotations on functions, classes and modules are evaluated eagerly unless the future import is used; from Python 3.14 they are evaluated only when necessary.

## Example
```python
bad:  class Node:
          parent: "Node" | None
          def first(self) -> None | "Node":
              ...
good: class Node:
          parent: "Node | None"
          def first(self) -> "Node | None":
              ...
```

## Limits
A union written entirely inside one string is not evaluated and is in range. From Python 3.14 an annotation is evaluated only when necessary, and it remains possible to introspect annotations at run time, so on a project whose minimum is 3.14 the union is evaluated only when something, such as introspection at run time, evaluates the annotations; there forward references no longer need to be enclosed in strings, and the fix removes the quotes. A module with `from __future__ import annotations` is in range for its annotations only, and its aliases, base classes and `TypeVar` or `NewType` definitions could still require string literals.

## Validator
Grep the file for a quoted name beside `|`. Open the module header and note whether it has `from __future__ import annotations`. Classify the place of each union: a function or variable annotation, or an evaluated expression such as the value of a type alias assigned without the `type` statement, a base class, or the arguments of a `TypeVar` or `NewType` definition. Validator question: **Does the file place a quoted name as a member of an `X | Y` union in an annotation of a module without `from __future__ import annotations`, or in a type alias value, base class, `TypeVar` or `NewType` definition the interpreter evaluates?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-29`, severity major, `file`, `symbol`, `code` = the union with its quoted member quoted verbatim, `fix` = the entire union quoted, such as `"Node | None"`, or for an annotation `from __future__ import annotations` with `Node | None`, `rationale` = a string member within an evaluated `X | Y` union causes a runtime error).

## Source
- Ruff TC010 runtime-string-union (astral-sh/ruff crates/ruff_linter/src/rules/flake8_type_checking/rules/runtime_string_union.rs) — 'type annotations can typically be wrapped in strings to avoid runtime evaluation, the use of a string member within an `X | Y`-style union type will cause a runtime error.' (fetched)
- Ruff TC010 runtime-string-union (astral-sh/ruff crates/ruff_linter/src/rules/flake8_type_checking/rules/runtime_string_union.rs) — 'remove the quotes, wrap the _entire_ union in quotes, or use `from __future__ import annotations` to disable runtime evaluation of annotations entirely.' (fetched)
- PEP 604 §Proposal (https://raw.githubusercontent.com/python/peps/main/peps/pep-0604.rst) — 'this proposal adds operator' (fetched)
- PEP 604 §Proposal (https://raw.githubusercontent.com/python/peps/main/peps/pep-0604.rst) — 'With this new operator, it is possible to write ``int | str`` instead of' (fetched)
- mypy docs runtime_troubles.rst §Future annotations import (https://raw.githubusercontent.com/python/mypy/master/docs/source/runtime_troubles.rst) — 'This can be thought of as automatic string literal-ification of all function and variable annotations.' (fetched)
- mypy docs runtime_troubles.rst §Future annotations import (https://raw.githubusercontent.com/python/mypy/master/docs/source/runtime_troubles.rst) — 'Even with the ``__future__`` import, there are some scenarios that could still require string literals or result in errors, typically involving use of forward references or generics in:' (fetched)
- mypy docs runtime_troubles.rst §Future annotations import (https://raw.githubusercontent.com/python/mypy/master/docs/source/runtime_troubles.rst) — ':ref:`type aliases <type-aliases>` not defined using the ``type`` statement;' (fetched)
- CPython Doc/whatsnew/3.14.rst §Deferred evaluation of annotations (https://raw.githubusercontent.com/python/cpython/main/Doc/whatsnew/3.14.rst) — 'on functions, classes, and modules are no longer evaluated eagerly.' (fetched)
- CPython Doc/whatsnew/3.14.rst §Deferred evaluation of annotations (https://raw.githubusercontent.com/python/cpython/main/Doc/whatsnew/3.14.rst) — 'evaluated only when necessary (except if ``from __future__ import annotations`` is used).' (fetched)
- CPython Doc/whatsnew/3.14.rst §Deferred evaluation of annotations (https://raw.githubusercontent.com/python/cpython/main/Doc/whatsnew/3.14.rst) — 'it remains possible to introspect annotations at runtime.' (fetched)
- CPython Doc/whatsnew/3.14.rst §Deferred evaluation of annotations (https://raw.githubusercontent.com/python/cpython/main/Doc/whatsnew/3.14.rst) — 'It is no longer necessary to enclose annotations in strings if they contain forward references.' (fetched)

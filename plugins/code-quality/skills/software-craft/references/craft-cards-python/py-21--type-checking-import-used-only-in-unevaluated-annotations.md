---
title: A name imported only inside an if TYPE_CHECKING block is used only in annotations and quoted type expressions the interpreter does not evaluate, never in code that runs
rule_id: PY-21
domain: code
step: [implement, review]
applies_to: [python, static-types]
triggers: ['\bif\s+(typing[.])?TYPE_CHECKING\b', '^\s+(from\s+[\w.]+\s+)?import\s+\w', ':\s*(typing[.])?TypeAlias\s*=', '\bcast\(\s*[A-Z]\w*\s*,']
scope: file
check_kind: semantic
severity_default: major
---

# A name imported only inside an if TYPE_CHECKING block is used only in annotations and quoted type expressions the interpreter does not evaluate, never in code that runs

## Thesis
A name whose only definition is an import inside an `if TYPE_CHECKING:` block appears only where the interpreter does not evaluate it: in annotations left unevaluated by quoting, by `from __future__ import annotations` or by the deferred annotations of Python 3.14, and in quoted type expressions such as a quoted `TypeAlias` value. Every use of the name in code that runs, such as a call or its argument (`cast(User, x)`, `isinstance(x, User)`), a base class, a decorator, a default value or the unquoted value of a `TypeAlias` assignment, rests on an import that executes at run time.

## Rationale
`typing.TYPE_CHECKING` is assumed `True` by static type checkers and is `False` at run time: a type checker imports the module for its analysis, while the interpreter never executes the block, so a name defined only there is not available at run time. A reference to it in code that runs raises `NameError`, and an explicit `TypeAlias` whose unquoted value names it raises `NameError` as well. Annotations escape this only while nothing evaluates them. Before Python 3.14 the annotations of functions, classes and modules are evaluated eagerly unless the module has `from __future__ import annotations`, which turns every function and variable annotation into a string; from Python 3.14 annotations are evaluated only when necessary, so an undefined name in them is harmless as long as nothing examines them. Resolving such annotations at run time with `typing.get_type_hints()` fails because the name is not defined.

## Example
```python
bad:  if TYPE_CHECKING:
          from app.models import User
      def is_user(obj: object) -> bool:
          return isinstance(obj, User)
good: from app.models import User
      if TYPE_CHECKING:
          from app.billing import Invoice
      def is_user(obj: object, invoice: "Invoice") -> bool:
          return isinstance(obj, User)
```

## Limits
A name that a running statement also binds, an `else:` branch of the same `if TYPE_CHECKING:` or a second import outside it, is outside the rule: the defect needs the type-checking block to hold the only definition. An annotation that the code examines at run time counts as code that runs; `annotationlib.get_annotations` with the `Format.STRING` or `Format.FORWARDREF` format retrieves annotations that may contain undefined symbols without raising `NameError`. Where the reference is an annotation, quoting it lets the import stay in the type-checking block; elsewhere the name needs an import outside the block. Whether a conditional import is warranted at all, which it is only where the imports needed for type checking must be avoided at run time, is outside this rule.

## Validator
Grep the file for `if TYPE_CHECKING:` or `if typing.TYPE_CHECKING:` and list every name its imports bind; drop a name that an `else:` branch or another import outside the block also binds. For each remaining name, find every reference in the file. A string annotation or a quoted type expression passes. An unquoted annotation passes when the module has `from __future__ import annotations` or the project's minimum Python, from `requires-python` in `pyproject.toml`, is 3.14 or later, and nothing in the code resolves it with `typing.get_type_hints()`. Every other reference runs: a call, a call argument such as the first argument of `cast` or the second of `isinstance`, a base class, a decorator, a default value, the unquoted value of a `TypeAlias` assignment. Validator question: **Does a name whose only definition is an import inside an `if TYPE_CHECKING:` block appear in an expression the interpreter evaluates at run time?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-21`, severity major, `file`, `symbol`, `code` = the line that references the name at run time and the import under `if TYPE_CHECKING:` that binds it, `fix` = the import moved out of the type-checking block, or the reference quoted where it is an annotation, in Python, `rationale` = names the imported name, the runtime construct that evaluates it and the `NameError` it raises).

---
title: Code whose Python floor is 3.10 or later reads a class's annotations through annotationlib.get_annotations or inspect.get_annotations, never from the __annotations__ entry of its __dict__
rule_id: PY-160
domain: code
step: [implement, review]
applies_to: [python]
triggers: ['__dict__\[\s*["\x27]__annotations__["\x27]\s*\]', '__dict__[.]get\(\s*["\x27]__annotations__["\x27]']
scope: file
check_kind: mechanical
severity_default: major
---

# Code whose Python floor is 3.10 or later reads a class's annotations through annotationlib.get_annotations or inspect.get_annotations, never from the __annotations__ entry of its __dict__

## Thesis
Where a project's minimum Python is 3.10 or later, or typing_extensions is available on an older floor, code reads a class's annotations with `annotationlib.get_annotations()` on Python 3.14+, `inspect.get_annotations()` on Python 3.10+ or `typing_extensions.get_annotations()` below Python 3.10, and reads them neither as `cls.__dict__["__annotations__"]` nor as `cls.__dict__.get("__annotations__")`.

## Rationale
From Python 3.14 the annotations of functions, classes and modules are no longer evaluated eagerly: they are stored in special-purpose annotate functions and evaluated only when necessary, except where `from __future__ import annotations` is used. A class defined under that import keeps an `__annotations__` entry in its class dictionary, so on Python 3.14 a read through `cls.__dict__.get("__annotations__")` or `cls.__dict__["__annotations__"]` returns annotations only when the class is defined under `from __future__ import annotations`, and misses them for every other class. The data stored in the class dictionary is an implementation detail whose format may change in the future. `annotationlib.get_annotations` (Python 3.14+, superseding `inspect.get_annotations`), `inspect.get_annotations` (Python 3.10+) and `typing_extensions.get_annotations` (below Python 3.10 where typing-extensions is available) are dedicated library functions with a stable public API, where the `__dict__` read relies on implementation details.

## Example
```python
bad:  def field_names(cls):
          ann = cls.__dict__.get("__annotations__", {})
          return list(ann)
good: def field_names(cls):
          ann = inspect.get_annotations(cls)
          return list(ann)
```

## Limits
Code that must run on Python 3.9 or earlier without typing_extensions keeps the class `__dict__` read, including a branch that runs only on those versions: there the documented practice relies on an implementation detail of Python 3.9 and before, that a class's annotations, when defined, are stored in its `__dict__`, and calls `cls.__dict__.get("__annotations__", None)` because the class may or may not have annotations defined. During class construction, where only the class namespace dictionary is available, `annotationlib.get_annotate_from_class_namespace` retrieves the annotate function from it; a metaclass reading that namespace mapping is outside the rule's triggers. A read of the `__annotations__` attribute itself, `obj.__annotations__`, is outside this rule.

## Validator
Grep the hunk for `__dict__["__annotations__"]` and `__dict__.get("__annotations__"`, in either quote style. For each match, read the project's Python floor from `requires-python` in pyproject.toml, Ruff's `target-version`, or `python_requires` in setup.cfg or setup.py; when the floor is below 3.10, check whether typing_extensions is a declared dependency. Open the enclosing function and leave out a read that sits in a branch that runs only on Python 3.9 or earlier, such as one under `sys.version_info < (3, 10)`. Validator question: **Does the hunk read annotations from the `__annotations__` entry of an object's `__dict__` in code whose floor is Python 3.10 or later, or an older floor with typing_extensions available, outside a branch that runs only on Python 3.9 or earlier?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-160`, severity major, `file`, `symbol`, `code` = the `__dict__` subscript or `.get` call that reads `"__annotations__"`, verbatim from the diff, `fix` = the same read as `annotationlib.get_annotations(cls)` on a 3.14 floor, `inspect.get_annotations(cls)` on a 3.10 floor or `typing_extensions.get_annotations(cls)` below 3.10, `rationale` = that from Python 3.14 the class dictionary holds annotations only for a class defined under `from __future__ import annotations`, and that its contents are an implementation detail).

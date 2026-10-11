---
title: A Python test whether an object can be called uses callable(obj), never a hasattr check for __call__
rule_id: PY-154
domain: code
step: [implement]
applies_to: [python, dynamic-types]
triggers: ['\bhasattr\s*\([^)]*[\x22\x27]__call__[\x22\x27]']
scope: hunk
check_kind: mechanical
severity_default: minor
---

# A Python test whether an object can be called uses callable(obj), never a hasattr check for __call__

## Thesis
A Python test whether an object can be called is written `callable(obj)`, never `hasattr(obj, "__call__")`, because an object that implements a custom `__getattr__`, or whose `__call__` is itself not callable, can give a misleading answer to the hasattr test.

## Rationale
A call `x(arg1, arg2, ...)` roughly translates to `type(x).__call__(x, arg1, ...)`: for custom classes, implicit invocations of special methods are only guaranteed to work correctly if defined on the object's type, not in its instance dictionary, and instances are callable if their class has a `__call__()` method. `hasattr` is implemented by calling `getattr` and seeing whether it raises an AttributeError, so it answers for any attribute named `__call__`: a custom `__getattr__` can give a misleading result, and an imported module that has a `__call__` attribute, or an instance with an attribute set by `self.__call__ = None`, passes the hasattr test without being callable. When `callable()` is false, calling the object will never succeed.

## Example
```python
bad:  if hasattr(handler, "__call__"):
          handler(event)
good: if callable(handler):
          handler(event)
```

## Limits
A true answer from `callable(obj)` still leaves it possible that the call fails; only a false answer settles that calling the object will never succeed. Code that reads `obj.__call__` to use the bound method, rather than to test for its presence, is outside the rule.

## Validator
Grep the hunk for `hasattr(` with `"__call__"` or `'__call__'` as the attribute name and read what the result decides. Validator question: **Does the hunk test whether an object can be called through `hasattr(obj, "__call__")` instead of `callable(obj)`?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-154`, severity minor, `file`, `symbol`, `code` = the hasattr call verbatim from the diff, `fix` = `callable(handler)` in place of the hasattr test, `rationale` = names that a call looks up `__call__` on the object's class, while hasattr also answers for a custom `__getattr__`, a module attribute or an instance attribute).

## Source
- flake8-bugbear B004 (PyCQA/flake8-bugbear README.rst) — 'If ``x`` implements custom ``__getattr__`` or its ``__call__`` is itself not callable, you might get misleading results.  Use ``callable(x)`` for consistent results.' (fetched)
- Ruff B004 unreliable-callable-check (astral-sh/ruff crates/ruff_linter/src/rules/flake8_bugbear/rules/unreliable_callable_check.rs) — 'Using `hasattr` is an unreliable mechanism for testing if an object is callable. If `obj` implements a custom `__getattr__`, or if its `__call__` is itself not callable, you may get misleading results.'; 'an imported module may have a `__call__` attribute but is not considered a callable object'; 'self.__call__ = None' (fetched)
- CPython Doc/library/functions.rst §callable (https://docs.python.org/3/library/functions.html) — 'it is still possible that a call fails, but if it is'; 'calling object will never succeed.'; 'and seeing whether it raises an AttributeError or not.'; 'Note that classes are callable (calling a class returns a new instance); instances are callable if their class has a __call__() method.' (fetched)
- CPython Doc/reference/datamodel.rst §Emulating callable objects and §Special method lookup (https://raw.githubusercontent.com/python/cpython/main/Doc/reference/datamodel.rst) — '``x(arg1, arg2, ...)`` roughly translates to ``type(x).__call__(x, arg1, ...)``'; 'For custom classes, implicit invocations of special methods are only guaranteed to work correctly if defined on an object's type, not in the object's instance dictionary.' (fetched)

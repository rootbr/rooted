---
title: A Python method's self or cls parameter takes no default value
rule_id: PY-142
domain: design
step: [implement, review]
applies_to: [python, object-oriented]
triggers: ['def\s+\w+\s*\(\s*(?:self|cls|mcs|metacls)\s*(?::[^=,)]*)?=', '^\s*def\s+\w+\s*\(\s*(?:self|cls)\s*=\s*None\b']
scope: hunk
check_kind: mechanical
severity_default: minor
---

# A Python method's self or cls parameter takes no default value

## Thesis
In a Python method whose first parameter is the receiver, that is a method defined directly in a class body with no decorator, `__new__` included, or with `classmethod` as its sole decorator, the receiver parameter, whether named `self`, `cls` or anything else, carries no default value; the same holds under a decorator that leaves the receiver binding unchanged.

## Rationale
Receiver parameters are usually bound by the method binding protocol: calling a method through an instance inserts the instance in front of the argument list, so `x.f(1)` is equivalent to `C.f(x, 1)`, and for a class method calling either `x.f(1)` or `C.f(1)` is equivalent to calling the underlying function with the class first. `__new__` is a static method, special-cased so it need not be declared as such, that takes the class of which an instance was requested as its first argument. A default value on a receiver parameter is therefore almost certainly a mistake and can lead to confusing behaviour or runtime errors. For an instance method the default is reached only by a caller that invokes the method directly through the class rather than through an instance, such as `A.method()` instead of `A().method()`; for a class method the class is bound on both paths, so the default is never used.

## Example
```python
bad:  class Builder:
          def method(self=None): ...
          @classmethod
          def build(cls=None): ...
good: class Builder:
          def method(self): ...
          @classmethod
          def build(cls): ...
```

## Limits
A function decorated with `staticmethod` has no receiver: a static method object defeats the transformation of function objects to method objects, so a default on its first parameter is an ordinary default. Under another decorator the rule holds where the decorator leaves the receiver binding unchanged, as `property`, a property setter and `typing.override` typically do; an arbitrary decorator could alter that binding, so the first parameter of a method under an unknown decorator is not taken for a receiver. Removing the default changes behaviour for a caller that invokes the method directly through the class rather than through an instance, such as `A.method()` instead of `A().method()`, relying on the receiver's default.

## Validator
Grep the hunk for a `def` whose first parameter carries a default: `self=`, `cls=`, `mcs=`, `metacls=` or any other first name followed by `=`, after an optional annotation. Open the enclosing scope to confirm the `def` sits directly in a class body rather than in a function nested inside a method. Read its decorators: none (`__new__` and `__init_subclass__` included) or `classmethod` alone makes the first positional parameter, positional-only or regular, the receiver; `staticmethod` means there is no receiver; `property`, a property setter or `typing.override` keeps the receiver; leave a method under any other decorator alone. Trace the callers in the hunk that call the method through the class without an instance. Validator question: **Does the receiver parameter of a method defined directly in a class body carry a default value?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-142`, severity minor, `file`, `symbol`, `code` = the `def` line with the defaulted receiver verbatim, `fix` = the same `def` with the default removed, such as `def method(self): ...`, and each call through the class that relied on the default passing an instance, `rationale` = the binding protocol supplies the receiver, so its default is almost certainly a mistake that a call through the class without an instance is the only way to reach).

## Source
- Ruff RUF077 method-receiver-default (astral-sh/ruff crates/ruff_linter/src/rules/ruff/rules/method_receiver_default.rs) — 'Receiver parameters (`self`, `cls`, or any name used as the receiver) should not have default values.'; 'In practice, these parameters are usually bound by the method binding protocol, so a default value on a receiver parameter is almost certainly a mistake and can lead to confusing behavior or runtime errors.'; 'Removing the default changes behavior for a caller that invokes the method directly through the class rather than through an instance (e.g. `A.method()` instead of `A().method()`), relying on the receiver parameter's default value.'; 'this rule only flags an undecorated method, an undecorated `__new__`, or a method whose sole decorator is the one that makes it a `@classmethod`.'; 'even though such decorators typically leave the receiver binding unchanged, because an arbitrary decorator could alter it.' (fetched)
- CPython Doc/reference/datamodel.rst §Instance methods (python/cpython Doc/reference/datamodel.rst) — 'in front of the argument list.'; 'calling ``x.f(1)`` is equivalent to calling ``C.f(x, 1)``.'; 'calling either ``x.f(1)`` or ``C.f(1)`` is equivalent to calling ``f(C,1)`` where ``f`` is the underlying function.' (fetched)
- CPython Doc/reference/datamodel.rst §Static method objects (python/cpython Doc/reference/datamodel.rst) — 'Static method objects provide a way of defeating the transformation of function objects to method objects described above.' (fetched)
- CPython Doc/reference/datamodel.rst §Basic customization (python/cpython Doc/reference/datamodel.rst) — 'is a static method (special-cased so you need not declare it as such) that takes the class of which an instance was requested as its first argument.' (fetched)
- Caveat: RUF077 is a preview rule, off by default, its fix always marked unsafe, and it flags only an undecorated method, an undecorated `__new__` or a method whose sole decorator is `classmethod`.

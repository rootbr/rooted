---
title: Python code uses the operator or builtin a special method implements, never a direct call such as a.__add__(b) or x.__len__() outside a special method body or a super() call
rule_id: PY-150
domain: code
step: [implement, refactor]
applies_to: [python, object-oriented]
triggers: ['(?<!super\(\))[.]__(add|sub|mul|matmul|truediv|floordiv|mod|pow|and|or|xor|lshift|rshift|eq|ne|lt|le|gt|ge|contains|len|str|repr|bool|hash|iter|next|getitem|setitem|delitem|call|format|bytes|int|float)__\s*\(', '(?<!super\(\))[.]__[ri](add|sub|mul|matmul|truediv|floordiv|mod|pow|and|or|xor|lshift|rshift)__\s*\(']
scope: hunk
check_kind: mechanical
severity_default: minor
---

# Python code uses the operator or builtin a special method implements, never a direct call such as a.__add__(b) or x.__len__() outside a special method body or a super() call

## Thesis
Outside the body of a special method definition, Python code applies the operator or builtin that a special method implements, such as `a + b`, `a > b`, `len(x)` or `str(x)`, instead of calling `__add__`, `__gt__`, `__len__`, `__str__` or a similar special method directly on an instance; a call on `super()` is the exception.

## Rationale
Special-method names are not meant to be called explicitly, and in most cases a builtin or an operator replaces the call. The two are not equivalent. A type may implement only some of the related special methods: a direct call of a missing one returns NotImplemented, while the operator raises TypeError, and a NotImplemented that reaches ordinary code gives a misleading error later or flows on as a value. The behaviour differs even for built-in types: `(1).__gt__(1.0)` returns NotImplemented while `1 > 1.0` is False, because the operator tries the reflected operation on the other type when a method returns NotImplemented. Implicit invocations of special methods are only guaranteed to work correctly when the method is defined on the object's type, not in its instance dictionary, so a special method assigned on an instance answers the direct call while operators and builtins ignore it.

## Example
```python
bad:  total = price.__add__(tax)
      size = items.__len__()
good: total = price + tax
      size = len(items)
```

## Limits
A direct call inside a special method definition and a call on `super()` are outside the rule. Some special methods are allowed to be called explicitly, among them `__exit__`, `__aexit__`, `__get__`, `__set__`, `__new__`, `__init_subclass__`, `__reduce__`, `__getstate__`, `__setstate__`, `__index__` and `__missing__`. A lambda that needs `__setitem__`, `__delitem__` or another method whose operator form is a statement keeps the direct call, since a lambda cannot hold a statement. A call on the type rather than on an instance, such as `type(obj).__hash__(obj)`, bypasses the instance on purpose, the way implicit special-method lookup does, and is outside the rule as well.

## Validator
Grep the hunk for a call of a special-method attribute, `.__name__(`. Skip it when the enclosing function is itself a special method (its name begins and ends with two underscores), when the receiver is `super()`, when the receiver is a class or `type(obj)` rather than an instance, when the method is one of those allowed to be called explicitly (`__exit__`, `__aexit__`, `__get__`, `__set__`, `__new__`, `__init_subclass__`, `__reduce__`, `__getstate__`, `__setstate__`, `__index__`, `__missing__`), and when a lambda calls a method whose operator form is a statement, such as `__setitem__` or `__delitem__`. Validator question: **Does code outside a special method definition call, directly on an instance and not through super(), a special method that an operator or builtin implements?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-150`, severity minor, `file`, `symbol`, `code` = the direct special-method call, `fix` = the operator or builtin form, such as `price + tax` or `len(items)`, `rationale` = the direct call returns NotImplemented where the operator tries the reflected method or raises TypeError, and it finds a special method set on the instance that operators and builtins ignore).

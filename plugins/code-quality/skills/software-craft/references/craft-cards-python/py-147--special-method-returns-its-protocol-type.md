---
title: A Python special method returns the type its protocol requires, such as a bool from __bool__, a non-negative int from __len__, a str from __str__ and __repr__ and None from __init__
rule_id: PY-147
domain: code
step: [design, implement]
applies_to: [python, object-oriented]
triggers: ['def\s+__(bool|len|hash|index)__\s*\(', 'def\s+__(str|repr|format|bytes|iter|init)__\s*\(']
scope: hunk
check_kind: semantic
severity_default: major
---

# A Python special method returns the type its protocol requires, such as a bool from __bool__, a non-negative int from __len__, a str from __str__ and __repr__ and None from __init__

## Thesis
A Python special method returns the type the data model gives for it: `__bool__` returns False or True, `__len__` an integer >= 0, `__hash__` and `__index__` an integer, `__str__`, `__repr__` and `__format__` a string, `__bytes__` a bytes object, `__iter__` a new iterator object, and `__init__` returns None.

## Rationale
Python calls these methods to implement truth value testing and bool(), len(), hash(), operator.index(), str(), repr(), format(), bytes(), the request for an iterator over a container, and the initialisation of a new object. Each special method expects a specific return type, and a call to it raises TypeError when its return type is incorrect: a `__bool__` that returns `len(self.items)` makes `bool(obj)` raise, and so every truth test of the object, and an `__init__` that returns a value other than None raises TypeError at run time. When `__bool__` is not defined, truth testing calls `__len__`, if it is defined, and treats the object as true when the result is nonzero, so a class that defines `__len__` needs no `__bool__` that counts its items.

## Example
```python
bad:  class Basket:
          def __bool__(self):
              return len(self.items)
good: class Basket:
          def __bool__(self):
              return len(self.items) > 0
```

## Limits
A special method set to None declares its operation unavailable, and calling the operation then raises TypeError by design: a class that sets `__iter__` to None is not iterable. Such a method is outside the rule. Rich comparison methods such as `__eq__` and `__lt__` can return any value, and a comparison used in a Boolean context calls bool() on it, so they are outside the rule.

## Validator
Grep the hunk for the def of a special method the Thesis lists. Open the method and trace every return statement and the end of its body, where falling off the end returns None: infer the type of each returned expression, such as `len(...)` an int, a comparison a bool, an f-string a str, a list neither an iterator nor a bool. Treat an `__iter__` whose body contains yield as a generator function, which returns a generator, an iterator; treat an `__init__` with a bare return as returning None. Validator question: **Does a listed special method in the hunk return, on some path, a value of a type other than the one the data model gives for it, a negative integer from `__len__`, or a value other than None from `__init__`?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-147`, severity major, `file`, `symbol`, `code` = the def line and the offending return, quoted verbatim from the diff, `fix` = the return converted to the required type, such as `return len(self.items) > 0` or `return str(self.value)`, or the `__bool__` removed in favour of `__len__`, `rationale` = the method, the type or value it returns and the exception the calling builtin raises, TypeError for a result of the wrong type).

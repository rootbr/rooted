---
title: A Python subclass's __slots__ repeats no name that a base class already declares in its __slots__
rule_id: PY-137
domain: design
step: [implement, review]
applies_to: [python, object-oriented]
triggers: ['^\s*__slots__\s*(?::[^=]+)?=', '[\x22\x27]__slots__[\x22\x27]\s*:']
scope: file
check_kind: semantic
severity_default: major
---

# A Python subclass's __slots__ repeats no name that a base class already declares in its __slots__

## Thesis
A Python class whose base class declares `__slots__` lists in its own `__slots__` only the names of additional slots, so no name in it repeats a name that a base class's `__slots__` already holds.

## Rationale
`__slots__` are implemented at the class level by creating descriptors for each variable name, and `__slots__` declared in parents are available in child classes. If a class defines a slot also defined in a base class, the instance variable defined by the base class slot is inaccessible, except by retrieving its descriptor directly from the base class. This renders the meaning of the program undefined; a check to prevent it may be added in the future.

## Example
```python
bad:  class Base:
          __slots__ = ('a', 'b')
      class Subclass(Base):
          __slots__ = ('a', 'd')
good: class Base:
          __slots__ = ('a', 'b')
      class Subclass(Base):
          __slots__ = ('d',)
```

## Limits
A subclass that defines no `__slots__` of its own repeats no slot: its instances get a `__dict__` and `__weakref__`, and the `__slots__` declared in its parents stay available to it. The rule compares names between `__slots__` declarations only; a class attribute named like a slot of its own class is a different conflict, in which the class attribute would overwrite the slot's descriptor.

## Validator
For each `__slots__` assignment the hunk adds or changes in a class body, read the class's bases and open every base class up the inheritance chain — in this file or the module it is imported from — and collect the names in each base's `__slots__`: a single string is one name, and a tuple, list or other iterable gives one name per item. Validator question: **Does a name in the class's `__slots__` also appear in the `__slots__` of one of its base classes?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-137`, severity major, `file`, `symbol`, `code` = the subclass's `__slots__` line, `fix` = the `__slots__` with the repeated name removed, such as `__slots__ = ('d',)`, `rationale` = the repeated name and the base class whose `__slots__` already declares it).

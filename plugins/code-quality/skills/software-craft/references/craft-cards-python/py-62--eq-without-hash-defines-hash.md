---
title: A Python class that defines __eq__ and whose instances must stay hashable also defines __hash__ or sets __hash__ to its parent's implementation explicitly
rule_id: PY-62
domain: design
step: [implement, review]
applies_to: [python, object-oriented]
triggers: ['def __eq__\(', '^\s+__eq__\s*=']
scope: file
check_kind: semantic
severity_default: major
---

# A Python class that defines __eq__ and whose instances must stay hashable also defines __hash__ or sets __hash__ to its parent's implementation explicitly

## Thesis
A Python class that overrides `__eq__` and compares only state that does not change after construction keeps its instances hashable: its own body defines `__hash__` so that objects which compare equal have the same hash value, or sets `__hash__ = <ParentClass>.__hash__` where the parent's hash stays in sync with the new equality. A class whose compared state is mutable leaves `__hash__` unimplemented, and its instances stay unhashable.

## Rationale
When a class body overrides `__eq__` and does not define `__hash__`, Python sets the class's `__hash__` to `None`, regardless of whether a superclass defines `__hash__`. Its instances then raise `TypeError` when a program retrieves their hash value and are identified as unhashable by `isinstance(obj, collections.abc.Hashable)`, which breaks their use as keys in a dictionary or members of a set. The only required property of a hash is that objects which compare equal have the same hash value, so inheriting a parent's `__hash__` while overriding `__eq__` is sound only where the two stay in sync, and the class must say so explicitly with `__hash__ = <ParentClass>.__hash__`. Hashed collections require that a key's hash value is immutable: if an object's hash value changes, it sits in the wrong hash bucket, which is why a class with mutable compared state should not implement `__hash__`.

## Example
```python
bad:  class Money:
          def __init__(self, amount: int, currency: str) -> None:
              self.amount, self.currency = amount, currency
          def __eq__(self, other: object) -> bool:
              return isinstance(other, Money) and (self.amount, self.currency) == (other.amount, other.currency)
good: class Money:
          ...  # __init__ and __eq__ unchanged; amount and currency are never reassigned
          def __hash__(self) -> int:
              return hash((self.amount, self.currency))
```

## Limits
Two positions meet here. One position reports every class that implements `__eq__` but not `__hash__`, because the class becomes unhashable and its instances cannot be keys in a dictionary or members of a set. The other position holds that a class which defines mutable objects and implements `__eq__` should not implement `__hash__`, since hashed collections require a key's hash value to be immutable. The condition that separates them is whether the state `__eq__` compares can change after construction: with unchanging compared state the class defines `__hash__` or sets `__hash__ = <ParentClass>.__hash__`, and with mutable compared state it leaves `__hash__` as `None` and its instances out of hashed collections. A dataclass whose `__eq__` the decorator generates is governed by the decorator's parameters: with `eq` true and `frozen` false it sets `__hash__` to `None`, marking the class unhashable since it is mutable.

## Validator
Grep the hunk for `def __eq__(` or an `__eq__ =` assignment in a class body. Open the class in the file; if its body defines `def __hash__` or assigns `__hash__`, stop. Trace every attribute `__eq__` compares: look for a method, property setter or outside code in the file that assigns or mutates it after `__init__`. If any compared attribute changes after construction, stop: that class stays unhashable. Otherwise look for its instances used as dict keys, set members or `hash()` arguments, and for a base class that defines `__hash__`, to name what the implicit `__hash__ = None` breaks. Validator question: **Does a class whose body defines `__eq__` but neither defines nor assigns `__hash__` compare only state that stays unchanged after construction?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-62`, severity major, `file`, `symbol`, `code` = the class line and the `def __eq__` line quoted verbatim from the diff, `fix` = `def __hash__(self) -> int: return hash((<the compared attributes>))` in the same class body, or `__hash__ = <ParentClass>.__hash__` where the parent's hash agrees with the new `__eq__`, `rationale` = the compared state that stays unchanged and the dict key, set member or base-class hashing that the implicit `__hash__ = None` breaks).

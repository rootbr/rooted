---
title: An __init__ of a Python class whose base class defines __init__ calls the base initializer through super().__init__
rule_id: PY-65
domain: design
step: [implement, review]
applies_to: [python, object-oriented]
triggers: ['def __init__\(self', '^class \w+\(\s*\w']
scope: file
check_kind: semantic
severity_default: major
---

# An __init__ of a Python class whose base class defines __init__ calls the base initializer through super().__init__

## Thesis
In Python, the `__init__` of a class whose base class has an `__init__` method explicitly calls that base initializer, for example as `super().__init__(...)`, so the base class part of the instance is initialized.

## Rationale
Python calls `__init__` after the instance has been created by `__new__`, with the arguments passed to the class constructor expression. If a base class has an `__init__` method, the derived class's `__init__`, if any, must explicitly call it to ensure proper initialization of the base class part of the instance. A derived `__init__` that leaves the call out leaves that part uninitialized, as when a subclass whose `__init__` only prints a message never runs the base `__init__` that sets the instance's name.

## Example
```python
bad:  class Fruit:
          def __init__(self, name: str) -> None: self.name = name
      class Apple(Fruit):
          def __init__(self) -> None: print("Creating an apple")
good: class Apple(Fruit):
          def __init__(self) -> None: super().__init__("apple")
```

## Limits
A derived class that defines no `__init__` needs no call: the requirement holds for the derived class's `__init__`, if any. `super().__init__(...)` is the documented example of the explicit call, and the rule asks for the call itself, so a call that names the base class explicitly also satisfies it.

## Validator
Grep the hunk for `def __init__(self` inside a `class` statement that names a base class. Open the class in the file and find its bases, in the file or through their imports; check whether a base other than `object` defines `__init__`. Read the derived `__init__` and trace every path through it: a `super().__init__(...)` call, a `<Base>.__init__(self, ...)` call, or a helper method that makes one counts as the call. Validator question: **Does an `__init__` of a class whose base class defines `__init__` complete on some path without calling the base initializer?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-65`, severity major, `file`, `symbol`, `code` = the class line and the `def __init__` line quoted verbatim from the diff, `fix` = the derived `__init__` with `super().__init__(<the base arguments>)` added, `rationale` = the base class whose `__init__` is skipped and the attributes it sets that the instance lacks).

## Source
- CPython Doc/reference/datamodel.rst §object.__init__ (https://raw.githubusercontent.com/python/cpython/main/Doc/reference/datamodel.rst) — 'Called after the instance has been created (by :meth:`__new__`), but before it is returned to the caller.  The arguments are those passed to the class constructor expression.' ... "the derived class's :meth:`__init__` method, if any, must explicitly call it to ensure proper initialization of the base class part of the instance; for example: ``super().__init__([args...])``." (fetched)
- Pylint super-init-not-called (W0231) (https://pylint.readthedocs.io/en/stable/user_guide/messages/warning/super-init-not-called.html §Description) — 'Used when an ancestor class method has an __init__ method which is not called by a derived class.' (fetched)

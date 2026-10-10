---
title: A Python class that derives from ABC marks with abstractmethod every method its subclasses must provide, and a class not meant as an interface drops the ABC base
rule_id: PY-68
domain: design
step: [design, implement, review]
applies_to: [python, object-oriented]
triggers: ['^class \w+\(.*\bABC\b', 'metaclass\s*=\s*(abc[.])?ABCMeta', '^\s+def \w+\(self[^)]*\)\s*(->\s*[^:]+)?:\s*([.][.][.]|pass)\s*$']
scope: file
check_kind: mechanical
severity_default: minor
---

# A Python class that derives from ABC marks with abstractmethod every method its subclasses must provide, and a class not meant as an interface drops the ABC base

## Thesis
A Python class that derives from `abc.ABC` or has `abc.ABCMeta` as its metaclass and is meant to be used as an interface marks with `@abstractmethod` each method or property its subclasses must provide, an empty method meant to be abstract included; for a class with such a base that is not meant to be used as an interface, the change to consider is removing the `ABC` base.

## Rationale
A class that has a metaclass derived from `ABCMeta` cannot be instantiated unless all of its abstract methods and properties are overridden, and `@abstractmethod`, the decorator indicating abstract methods, requires that metaclass. With no member marked, nothing is left to override: the class itself instantiates, and so does a subclass that omits a method the interface needs. Abstract base classes are used to define interfaces; one with no abstract methods or properties may mean that an abstract method or property was forgotten or an `@abstractmethod` decorator omitted, and an empty method in it without an abstract decorator may be indicative of a mistake. The decorator combines with `@classmethod`, `@staticmethod` and `@property` when applied as the innermost decorator, so class methods, static methods and properties are marked the same way.

## Example
```python
bad:  class Repository(ABC):
          def save(self, item): ...
          def get(self, key): ...
good: class Repository(ABC):
          @abstractmethod
          def save(self, item): ...
          @abstractmethod
          def get(self, key): ...
```

## Limits
An `ABC` base whose methods are all concrete is not necessarily an error; when the class is not meant to be used as an interface, removing the `ABC` base is the change to consider rather than adding decorators. An empty method takes `@abstractmethod` when it is meant to be abstract; an empty method that subclasses may leave as it is stays undecorated. `@abstractmethod` only affects subclasses derived using regular inheritance; virtual subclasses registered with the ABC's `register()` method are not affected.

## Validator
Grep the hunk for a `class` line whose bases include `ABC`, for `metaclass=ABCMeta`, and for a method whose body is only `...` or `pass`. Open the file at the class: list its methods and properties with the decorators on each, read its docstring, and look at its subclasses in the file to judge whether it is meant as an interface. Validator question: **Does a class with an `ABC` base or `ABCMeta` metaclass carry no `@abstractmethod` member, or leave without `@abstractmethod` an empty-bodied method that its subclasses are meant to provide?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-68`, severity minor, `file`, `symbol`, `code` = the `class` line and the undecorated `def` lines quoted verbatim from the diff, `fix` = `@abstractmethod` above each method subclasses must provide, with `from abc import ABC, abstractmethod`, or the `ABC` base removed from a class not meant as an interface, in Python, `rationale` = the instance of the base or of an incomplete subclass that the missing decorators let through).

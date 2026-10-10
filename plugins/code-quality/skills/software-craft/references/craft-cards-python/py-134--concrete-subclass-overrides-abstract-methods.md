---
title: A concrete Python subclass overrides every method its bases declare abstract
rule_id: PY-134
domain: design
step: [design, implement, review]
applies_to: [python, object-oriented]
triggers: ['^\s*class\s+\w+\(\s*[A-Za-z_][^)]*\)\s*:', 'raise\s+NotImplementedError\b', '^\s*@(?:abc[.])?abstractmethod\b']
scope: file
check_kind: semantic
severity_default: major
---

# A concrete Python subclass overrides every method its bases declare abstract

## Thesis
A concrete Python class defines every method that one of its base classes declares abstract, whether the base marks the method with abc.abstractmethod or gives it a body that raises NotImplementedError.

## Rationale
The abstractmethod decorator only sets the function attribute __isabstractmethod__ to True; ABCMeta.__new__ computes the class's __abstractmethods__ set from those attributes, and when the set is non-empty, an attempt to instantiate the class raises TypeError. The decorator therefore requires that the class's metaclass is ABCMeta or derived from it: under a base whose metaclass is not ABCMeta, such as one that does not derive from abc.ABC, no such set is computed, the incomplete subclass instantiates, and calling the missing method runs the base's placeholder body, which for a pass body returns None. A body that raises NotImplementedError is the convention in user-defined base classes for a method that derived classes must override; no metaclass collects it, so the gap shows only when the method is first called. Even under ABCMeta the check runs when the class is instantiated, not when it is defined.

## Example
```python
bad:  class Shape:
          @abc.abstractmethod
          def area(self): ...
      class Square(Shape):
          pass
good: class Shape(abc.ABC):
          @abc.abstractmethod
          def area(self): ...
      class Square(Shape):
          def area(self): return self.side ** 2
```

## Limits
A subclass that is itself abstract, left for further subclasses to complete, is outside the rule, whose scope is the concrete class; a class that declares an abstract method of its own, derives directly from abc.ABC, declares metaclass=ABCMeta or is a Protocol class counts as abstract.

## Validator
Grep the hunk for class statements with bases, abstractmethod decorators and raise NotImplementedError. For each class with bases that the hunk adds or changes, open its file and the definitions of its bases, and collect the base methods decorated with abstractmethod or whose body raises NotImplementedError, minus those an intermediate base already defines; when the hunk adds an abstract method to a base, take the subclasses in the file as well. Skip a class that declares an abstract method of its own, derives directly from abc.ABC, declares metaclass=ABCMeta or is a Protocol class. Validator question: **Does a concrete class leave undefined a method that one of its base classes declares abstract?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-134`, severity major, `file`, `symbol`, `code` = the class statement of the concrete class and the abstract base method it leaves undefined, `fix` = the concrete class with its own definition of that method, `rationale` = that the incomplete class instantiates, or under ABCMeta fails only at instantiation, and the missing method runs the base's placeholder body).

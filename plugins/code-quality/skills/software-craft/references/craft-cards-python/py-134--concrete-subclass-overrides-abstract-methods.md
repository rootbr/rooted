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

## Source
- Pylint abstract-method (W0223) (pylint-dev/pylint pylint/checkers/classes/class_checker.py) — 'Used when an abstract method (i.e. raise NotImplementedError) is not overridden in concrete class.' (fetched)
- Pylint abstract-method (W0223) (pylint-dev/pylint doc/data/messages/a/abstract-method/bad/abstract_method.py) — 'class Panther(WildAnimal):  # [abstract-method]' (fetched)
- pylint-dev/pylint utils.py, class_is_abstract (https://raw.githubusercontent.com/pylint-dev/pylint/main/pylint/checkers/utils.py) — 'Only check for explicit metaclass=ABCMeta on this specific class' (fetched)
- pylint-dev/pylint utils.py, class_is_abstract (https://raw.githubusercontent.com/pylint-dev/pylint/main/pylint/checkers/utils.py) — 'As well as direct abc.ABC inheritance' (fetched)
- pylint-dev/pylint utils.py, class_is_abstract (https://raw.githubusercontent.com/pylint-dev/pylint/main/pylint/checkers/utils.py) — 'Protocol classes are considered' (fetched)
- pylint-dev/pylint utils.py, class_is_abstract (https://raw.githubusercontent.com/pylint-dev/pylint/main/pylint/checkers/utils.py) — 'if method.is_abstract(pass_is_abstract=False):' (fetched)
- PEP 3119 §The abc Module, Implementation (https://raw.githubusercontent.com/python/peps/main/peps/pep-3119.rst) — 'The ``@abstractmethod`` decorator sets the function attribute ``__isabstractmethod__`` to the value ``True``.' (fetched)
- PEP 3119 §The abc Module, Implementation (https://raw.githubusercontent.com/python/peps/main/peps/pep-3119.rst) — 'The ``ABCMeta.__new__`` method computes the type attribute ``__abstractmethods__`` as the set of all method names that have an ``__isabstractmethod__`` attribute whose value is true.' (fetched)
- PEP 3119 §The abc Module, Implementation (https://raw.githubusercontent.com/python/peps/main/peps/pep-3119.rst) — 'If the resulting ``__abstractmethods__`` set is non-empty, the class is considered abstract, and attempts to instantiate it will raise ``TypeError``.' (fetched)
- CPython Doc/library/abc.rst §abc.abstractmethod (https://raw.githubusercontent.com/python/cpython/main/Doc/library/abc.rst) — 'Using this decorator requires that the class's metaclass is :class:`ABCMeta` or is derived from it.' (fetched)
- CPython Doc/library/abc.rst §abc.abstractmethod (https://raw.githubusercontent.com/python/cpython/main/Doc/library/abc.rst) — 'A class that has a metaclass derived from :class:`!ABCMeta` cannot be instantiated unless all of its abstract methods and properties are overridden.' (fetched)
- Python documentation, Built-in Exceptions §NotImplementedError (https://docs.python.org/3/library/exceptions.html) — 'In user defined base classes, abstract methods should raise this exception when they require derived classes to override the method' (fetched)
- CPython Doc/tutorial/controlflow.rst §Defining Functions (https://raw.githubusercontent.com/python/cpython/main/Doc/tutorial/controlflow.rst) — 'even functions without a :keyword:`return` statement do return a value, albeit a rather boring one.' (fetched)

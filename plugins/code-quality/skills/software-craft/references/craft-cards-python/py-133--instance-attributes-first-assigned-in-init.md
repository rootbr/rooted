---
title: Every instance attribute of a Python class is first assigned in __init__ or another attribute-defining method
rule_id: PY-133
domain: design
step: [design, implement, review]
applies_to: [python, object-oriented, dynamic-types]
triggers: ['^\s+self[.][A-Za-z_]\w*\s*(?::[^=]+)?=[^=]', '^\s+setattr\(\s*self\s*,']
scope: file
check_kind: semantic
severity_default: minor
---

# Every instance attribute of a Python class is first assigned in __init__ or another attribute-defining method

## Thesis
Every attribute that a method of a Python class assigns on self is first assigned, if only to a placeholder such as False, in __init__ or in another attribute-defining method: by default __new__, setUp, asyncSetUp and __post_init__, a list the project's linter configuration can extend.

## Rationale
A Python data attribute needs no declaration: like a local variable, it springs into existence when it is first assigned. An attribute first assigned in an ordinary method, such as self.is_registered = True inside register(), therefore does not exist until that method has run, and a read before then fails, because attribute lookup raises AttributeError when the attribute is not available. Assigning the attribute in __init__ first, as self.is_registered = False, makes it exist from the moment the object is built, and the later method only reassigns it.

## Example
```python
bad:  class Student:
          def register(self):
              self.is_registered = True
good: class Student:
          def __init__(self):
              self.is_registered = False
          def register(self):
              self.is_registered = True
```

## Limits
An attribute also counts as first assigned when it is assigned in a property setter, defined as a class attribute, assigned in an attribute-defining method of a base class, or set by a method that an attribute-defining method calls. In a class that defines __getattr__, a read before the first assignment calls that method as a fallback instead of failing with AttributeError.

## Validator
Grep the hunk for assignments to self.<name> and for setattr(self, ...) inside method bodies. Read the project's Pylint defining-attr-methods option, whose default is __init__, __new__, setUp, asyncSetUp and __post_init__. Open the class in the file and, for each attribute the hunk assigns outside those methods, look for an assignment in one of them, in a method they call, in a property setter, in the class body, or in a defining method of a base class. Skip a class that matches the project's mixin-class-rgx when its ignored-checks-for-mixins lists attribute-defined-outside-init. Validator question: **Is an attribute that a method assigns on self assigned nowhere in __init__, the other attribute-defining methods, the methods they call, a property setter, the class body or a base class's defining method?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-133`, severity minor, `file`, `symbol`, `code` = the assignment of the attribute outside the attribute-defining methods, `fix` = an assignment of the attribute to a placeholder in `__init__`, such as `self.is_registered = False`, with the later method keeping its reassignment, `rationale` = that the attribute does not exist, and a read raises AttributeError, until the assigning method has run).

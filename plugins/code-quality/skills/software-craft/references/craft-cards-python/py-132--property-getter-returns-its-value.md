---
title: A Python property getter returns its value with a return statement
rule_id: PY-132
domain: design
step: [implement, review]
applies_to: [python, object-oriented]
triggers: ['^\s*@property\b', '^\s*@\w+[.]getter\b']
scope: hunk
check_kind: mechanical
severity_default: major
---

# A Python property getter returns its value with a return statement

## Thesis
A Python method decorated with @property contains a return statement that gives the attribute's value, unless the getter raises an exception, yields, or is decorated with abstractmethod or overload.

## Rationale
The @property decorator transforms a method into a getter for a computed attribute, so reading the attribute is expected to yield a value, just as reading a regular attribute does. A Python function without a return statement still returns a value, None. A getter whose body only evaluates the expression, such as f"{self.first_name} {self.last_name}" with no return in front, therefore provides None on every read instead of a meaningful value. This is almost always unintentional; code that depends on the property then behaves incorrectly, and the implicit None is not obvious from looking at the property access, which makes the bug harder to trace.

## Example
```python
bad:  class User:
          @property
          def full_name(self):
              f"{self.first_name} {self.last_name}"
good: class User:
          @property
          def full_name(self):
              return f"{self.first_name} {self.last_name}"
```

## Limits
A getter that raises an exception, or one decorated with abstractmethod, is an intentional pattern where no return value is expected. A getter declared in a Protocol class or in a .pyi stub file is outside the rule as well. A getter whose body yields is a generator function and returns a generator object on every read, not None, and a getter decorated with overload is a declaration; both are outside the rule. The rule is met by a return statement anywhere in the getter's own body, since the defect is a property method that contains no return statement at all; a return inside a nested function does not count for the getter.

## Validator
Grep the hunk for @property and @<name>.getter decorator lines, and for any decorator the project lists in Ruff's lint.pydocstyle.property-decorators option. Open the decorated function and scan its own body, without descending into nested function definitions, for a return statement. Skip the getter when its body raises an exception or yields, when it is decorated with abstractmethod or overload, when its class is a Protocol, or when the file is a .pyi stub. Validator question: **Does a method decorated as a property getter contain no return statement in its own body while it neither raises nor yields, and is not abstract, an overload, a Protocol member or a stub-file declaration?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-132`, severity major, `file`, `symbol`, `code` = the decorator line, the `def` line and the body statement that computes the value without returning it, `fix` = the same getter with `return` in front of the computed expression, `rationale` = that every read of the attribute yields None).

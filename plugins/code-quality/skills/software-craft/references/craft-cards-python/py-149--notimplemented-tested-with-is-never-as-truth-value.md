---
title: Python code tests for NotImplemented with is or is not and never uses it as a truth value, which raises TypeError from Python 3.14
rule_id: PY-149
domain: code
step: [implement, handle-errors]
applies_to: [python, object-oriented]
triggers: ['\bNotImplemented\b', '\bnot\s+[\w.]+[.]__(eq|ne|lt|le|gt|ge)__\s*\(', '\bif\s+[^#]*[.]__(eq|ne|lt|le|gt|ge)__\s*\(']
scope: hunk
check_kind: semantic
severity_default: major
---

# Python code tests for NotImplemented with is or is not and never uses it as a truth value, which raises TypeError from Python 3.14

## Thesis
Python code tests the NotImplemented that a binary or rich-comparison special method returns with `is NotImplemented` or `is not NotImplemented`, and never evaluates it in a boolean context: not in `if result:`, `not result`, `bool(result)`, `and` or `or`, and not through `not self.__eq__(other)` or another unchecked direct call of a special method that can return it. From Python 3.14 evaluating NotImplemented in a boolean context raises TypeError.

## Rationale
NotImplemented is the special value that binary special methods such as `__eq__`, `__lt__` and `__add__` return to indicate that the operation is not implemented with respect to the other type, and it should not be evaluated in a boolean context. Before Python 3.14 it evaluated to True, with a DeprecationWarning since Python 3.9, which could lead to unexpected behaviour in code meant to check whether an operation was implemented: `not self.__eq__(other)` gave False, "not unequal", for two objects that `__eq__` cannot compare. From Python 3.14 the same expression raises TypeError. When a binary method returns NotImplemented, the interpreter tries the reflected operation on the other type, or another fallback depending on the operator, and raises an appropriate exception only if all attempts return NotImplemented; a method that returns a bool made from the sentinel never triggers that fallback. The default `__ne__` delegates to `__eq__` and inverts the result unless it is NotImplemented, so a `__ne__` that only inverts `__eq__` is unnecessary.

## Example
```python
bad:  def __ne__(self, other):
          return not self.__eq__(other)
good: def __ne__(self, other):
          result = self.__eq__(other)
          return result if result is NotImplemented else not result
```

## Limits
Returning NotImplemented from a binary special method and comparing a result with `is` or `is not` are the intended uses. A comparison written with the operator, `a == b` or `a < b`, applies the reflected attempt and the fallback itself, so its result in a condition is outside the rule. A direct call into an `__eq__` that the same class defines to return only True or False on every path yields no sentinel; the default `object.__eq__` returns NotImplemented whenever the two objects are not identical, so a direct call that can reach it falls under the rule. NotImplementedError, the exception, is not interchangeable with NotImplemented and is outside the rule.

## Validator
Grep the hunk for `NotImplemented` and for direct calls of `__eq__`, `__ne__`, `__lt__`, `__le__`, `__gt__`, `__ge__` or another binary special method. For each, find where the value goes: an `if` or `while` test, `not`, `and`, `or`, `bool()`, a conditional expression or an `assert`; trace a name assigned from such a call to the place it is tested. For a direct call, open the class and its bases to see whether the called method can return NotImplemented; the default `object.__eq__` can. Validator question: **Does code evaluate NotImplemented, or the unchecked result of a special-method call that can return NotImplemented, in a boolean context instead of testing it with is or is not?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-149`, severity major, `file`, `symbol`, `code` = the expression that tests the sentinel or the direct special-method call, `fix` = a `result is NotImplemented` or `result is not NotImplemented` test before the value is used, or the `__ne__` deleted so the default applies, `rationale` = NotImplemented evaluated as true, deprecated in a boolean context since Python 3.9, and raises TypeError there from Python 3.14).

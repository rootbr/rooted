---
title: A Python binary-operator or rich-comparison method that does not support the other operand returns NotImplemented and does not raise NotImplementedError, and no code raises NotImplemented
rule_id: PY-10
domain: code
step: [implement, handle-errors, review]
applies_to: [python, object-oriented]
triggers: ['raise\s+NotImplemented\b(?!Error)', 'raise\s+NotImplementedError\b', 'def\s+__(eq|ne|lt|le|gt|ge|add|sub|mul|matmul|truediv|floordiv|mod|divmod|pow|lshift|rshift|and|xor|or|r(add|sub|mul|matmul|truediv|floordiv|mod|divmod|pow|lshift|rshift|and|xor|or))__\(']
scope: file
check_kind: mechanical
severity_default: major
---

# A Python binary-operator or rich-comparison method that does not support the other operand returns NotImplemented and does not raise NotImplementedError, and no code raises NotImplemented

## Thesis
A Python rich-comparison or binary numeric special method, such as `__eq__`, `__lt__`, `__add__` or `__radd__`, that does not implement the operation for the operand it receives returns `NotImplemented` and does not raise `NotImplementedError`; code that marks a method as abstract or not implemented raises `NotImplementedError`, never `NotImplemented`.

## Rationale
Numeric methods and rich comparison methods should return the `NotImplemented` singleton when they do not implement the operation for the operands provided; the interpreter then tries the reflected operation, such as `__radd__` of the other operand for `+`, or some other fallback, depending on the operator. If such a method raises `NotImplementedError` instead, the callers would not catch the exception and the reverse operation would not be called, so the other operand never gets its turn. The converse slip fails as well: `NotImplemented` is not an exception, so it cannot be raised; `NotImplementedError` is the exception that indicates a method is abstract or not implemented in the derived class.

## Example
```python
bad:  def __eq__(self, other):
          if not isinstance(other, Money):
              raise NotImplementedError
      def convert(self, rate):
          raise NotImplemented
good: def __eq__(self, other):
          if not isinstance(other, Money):
              return NotImplemented
      def convert(self, rate):
          raise NotImplementedError
```

## Limits
The rule reaches the rich-comparison methods `__lt__`, `__le__`, `__eq__`, `__ne__`, `__gt__` and `__ge__` and the binary numeric methods with their reflected forms: `__add__`, `__sub__`, `__mul__`, `__matmul__`, `__truediv__`, `__floordiv__`, `__mod__`, `__divmod__`, `__pow__`, `__lshift__`, `__rshift__`, `__and__`, `__xor__`, `__or__` and `__radd__` through `__ror__`. Raising `NotImplementedError` stays correct in an ordinary method meant to be abstract or not implemented in a derived class.

## Validator
Grep the hunk for `raise NotImplemented` not followed by `Error`, and for `raise NotImplementedError`. For the second, open the file and find the enclosing def: it counts only when that def is a rich-comparison or binary numeric special method or a reflected form of one, and the raise answers an operand the method does not support. Validator question: **Does code raise `NotImplemented`, or does a rich-comparison or binary numeric special method raise `NotImplementedError` for an operand it does not support?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-10`, severity major, `file`, `symbol`, `code` = the raise statement with its enclosing def line, verbatim, `fix` = `return NotImplemented` in the special method, or `raise NotImplementedError` where `raise NotImplemented` was written, `rationale` = that a returned NotImplemented lets Python try the other operand's reflected method, which a raised NotImplementedError prevents, or that NotImplemented is not an exception and cannot be raised).

## Source
- CPython Doc/reference/datamodel.rst §NotImplemented (https://raw.githubusercontent.com/python/cpython/main/Doc/reference/datamodel.rst) — 'Numeric methods and rich comparison methods should return this value if they do not implement the operation for the operands provided.  (The interpreter will then try the reflected operation, or some other fallback, depending on the operator.)' (fetched)
- CPython Doc/reference/datamodel.rst §Emulating numeric types (https://raw.githubusercontent.com/python/cpython/main/Doc/reference/datamodel.rst) — 'If one of those methods does not support the operation with the supplied arguments, it should return :data:`NotImplemented`.' (fetched)
- SonarSource python S5712 (SonarSource/sonar-python python-checks/src/main/resources/org/sonar/l10n/py/rules/python/S5712.html) — 'the callers would not catch the exception and the reverse operation would not be called.' (fetched)
- SonarSource python S5712 (SonarSource/sonar-python python-checks/src/main/resources/org/sonar/l10n/py/rules/python/S5712.html) — 'The interpreter will then try the reverse operation, i.e.' (fetched)
- SonarSource python S5712 (SonarSource/sonar-python python-checks/src/main/resources/org/sonar/l10n/py/rules/python/S5712.html) — 'Below is the list of special methods this rule applies to:' (fetched)
- Ruff F901 raise-not-implemented (astral-sh/ruff crates/ruff_linter/src/rules/pyflakes/rules/raise_not_implemented.rs) — 'Because `NotImplemented` is not an exception, it cannot be raised. Raise `NotImplementedError` instead, which is used to indicate that a method is abstract or not implemented in the derived class.' (fetched)

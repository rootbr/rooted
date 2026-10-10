---
title: A Python exception class that defines its own __init__ passes every argument it receives to super().__init__() and takes no keyword-only parameter, unless it defines both __str__ and __reduce__
rule_id: PY-170
domain: errors
step: [design, implement, review]
applies_to: [python, exceptions, object-oriented]
triggers: ['^\s*class\s+\w+\(.*(Error|Exception|Warning)\b.*\)\s*:', 'super\(\)[.]__init__\(', '^\s*def __init__\(self\b']
scope: file
check_kind: semantic
severity_default: major
---

# A Python exception class that defines its own __init__ passes every argument it receives to super().__init__() and takes no keyword-only parameter, unless it defines both __str__ and __reduce__

## Thesis
A Python exception class with a custom `__init__` passes all the arguments that `__init__` receives to `super().__init__()` and declares no keyword-only parameter; a class that defines both `__str__` and `__reduce__` is exempt.

## Rationale
`BaseException.__reduce__` and `BaseException.__str__` rely on the exception's `args` attribute, the tuple of arguments given to the exception constructor, which `BaseException.__new__` and `BaseException.__init__` set. An exception class works correctly with `copy.copy()` and `pickle` when its custom `__init__` passes all of its arguments to `super().__init__()`; an `__init__` that passes fewer or other arguments makes it very easy to break pickling. Keyword arguments are the sharpest case, since `BaseException.__new__` and `BaseException.__init__` ignore them, and an `__init__` that accepts keyword-only parameters is part of the defect as well. Passing every argument keeps `args` correct for `__reduce__` and `__str__`; defining both `__str__` and `__reduce__` bypasses the need for correct handling of `args`.

## Example
```python
bad:  class LookupFailed(Exception):
          def __init__(self, key, source):
              super().__init__(f"{key} not found in {source}")
good: class LookupFailed(Exception):
          def __init__(self, key, source):
              super().__init__(key, source)
              self.key, self.source = key, source
          def __str__(self):
              return f"{self.key} not found in {self.source}"
```

## Limits
A class that defines both `__str__` and `__reduce__` bypasses the need for correct handling of `args` and is outside the rule. The exemption also holds when a superclass defines the two methods; a check confined to the class body cannot detect methods defined in a superclass, so open the bases before reporting.

## Validator
In the hunk, find each class whose bases name an exception type (a name ending in `Error`, `Exception` or `Warning`, or a project class derived from one) and that defines `__init__`. Open the file: list the parameters of `__init__`, including any declared after a bare `*` or `*args`, and the arguments of its `super().__init__(...)` or `Base.__init__(self, ...)` call. Check whether the class or one of its bases in the project defines both `__str__` and `__reduce__`. Validator question: **Does this exception class's `__init__` pass `super().__init__()` fewer or other arguments than it receives, or declare a keyword-only parameter, while neither the class nor its bases define both `__str__` and `__reduce__`?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-170`, severity major, `file`, `symbol`, `code` = the `__init__` signature and its `super().__init__(...)` call, `fix` = the `__init__` passing every parameter, as in `super().__init__(key, source)`, with the message built in `__str__` from stored attributes, `rationale` = `args` no longer matches what `__init__` takes, so `copy.copy()` and pickling of the exception break).

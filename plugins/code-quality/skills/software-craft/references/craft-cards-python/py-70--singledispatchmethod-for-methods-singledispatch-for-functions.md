---
title: A Python method that dispatches on an argument's type uses functools.singledispatchmethod, and a module-level function uses functools.singledispatch
rule_id: PY-70
domain: design
step: [implement, review]
applies_to: [python, object-oriented]
triggers: ['@(functools[.])?singledispatch\s*$', '@(functools[.])?singledispatchmethod\b', '^from functools import .*\bsingledispatch(method)?\b']
scope: hunk
check_kind: mechanical
severity_default: major
---

# A Python method that dispatches on an argument's type uses functools.singledispatchmethod, and a module-level function uses functools.singledispatch

## Thesis
A Python function defined in a class body that dispatches on the type of an argument is decorated with `functools.singledispatchmethod`, and a module-level function that does so is decorated with `functools.singledispatch`.

## Rationale
`functools.singledispatch` dispatches on the type of the first argument, and `singledispatchmethod` on the type of the first non-`self` or non-`cls` argument. Applied to an instance method, `singledispatch` receives `self` as the first argument, so dispatch is performed on the type of the instance, not on the data argument: in the typical case every call falls through to the base implementation because the receiver class is not registered as a dispatch type, and where the receiver class or one of its ancestors matches a registered type, the same call site can produce different results in different parts of a class hierarchy. Applied to a method decorated with `@classmethod`, `singledispatch` attempts to operate on a classmethod object rather than a plain function, and the call fails at runtime. `singledispatchmethod` returns a non-callable descriptor that relies on the descriptor protocol to bind to an instance or class; applied to a standalone function, the resulting object cannot be invoked at all, and calling it raises `TypeError`. In none of these cases is an error or warning raised at decoration time, and some failure modes only surface on the first call.

## Example
```python
bad:  class Board:
          @singledispatch
          def convert_position(self, position): ...
good: class Board:
          @singledispatchmethod
          def convert_position(self, position): ...
```

## Limits
`@staticmethod` placed above `@singledispatch` dispatches correctly: `@singledispatch` then applies to a regular function and `@staticmethod` prevents Python from binding `self`, so dispatch happens on the data argument; that order is uncommon and easy to misuse, and a refactor that swaps it reintroduces the defect. `@singledispatch` placed above `@staticmethod` wraps the staticmethod descriptor object, which makes registration of overloads and dispatch on instances unreliable. `@singledispatchmethod` supports nesting with `@classmethod`, and it must be the outermost decorator to allow `dispatcher.register`.

## Validator
Grep the hunk for `@singledispatch` and `@singledispatchmethod`, with or without `functools.`, and for their import. Open the file at each decorated `def`: note whether it sits in a class body or at module level, and where any `@staticmethod` or `@classmethod` stands relative to the dispatch decorator. Validator question: **Is `@singledispatch` applied to a function in a class body without `@staticmethod` above it, or `@singledispatchmethod` applied to a module-level function?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-70`, severity major, `file`, `symbol`, `code` = the dispatch decorator line and the `def` line under it quoted verbatim from the diff, `fix` = `@singledispatchmethod` on the method with its `.register` implementations, or the generic function moved to module level under `@singledispatch`, or `@singledispatch` in place of `@singledispatchmethod` on a module-level function, in Python, `rationale` = the argument whose type the misplaced decorator dispatches on, or the call that raises `TypeError`).

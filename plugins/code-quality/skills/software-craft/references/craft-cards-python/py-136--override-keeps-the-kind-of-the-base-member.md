---
title: A Python override keeps the kind of the member it replaces, so an async method stays async and a property stays a property
rule_id: PY-136
domain: design
step: [design, implement, review]
applies_to: [python, object-oriented]
triggers: ['^\s*async\s+def\s+\w+\s*\(\s*self\b', '^\s*def\s+\w+\s*\(\s*self\b', '^\s*@property\b', '^\s*@(?:typing[.])?override\b']
scope: file
check_kind: semantic
severity_default: major
---

# A Python override keeps the kind of the member it replaces, so an async method stays async and a property stays a property

## Thesis
A Python member that overrides a base-class member of the same name is of the same kind as the member it replaces: an `async def` overrides an `async def`, a non-async method overrides a non-async method, and a property — its getter, setter or deleter — overrides a property.

## Rationale
An override that does not match its base class in kind — an async method replaced by a non-async one or the reverse, a property replaced by a method or the reverse — could result in potential bugs at runtime. A function defined with `async def` is always a coroutine function, which returns a coroutine object, and `await` suspends the caller on an awaitable object, so a caller written against an async base method awaits whatever an override returns. Nothing at runtime enforces that an override returns a value compatible with the original return type, since annotations have no effect at runtime. mypy checks that an override of a statically typed method has a compatible signature, and it also accepts a dynamically typed override of a statically typed method, which can be unsafe.

## Example
```python
bad:  class Fruit:
          async def bore(self, insect): ...
      class Apple(Fruit):
          def bore(self, insect): ...  # await apple.bore(x) raises TypeError
good: class Fruit:
          async def bore(self, insect): ...
      class Apple(Fruit):
          async def bore(self, insect): ...
```

## Limits
The rule compares an override with the member of the same name on a base class; a member that no base class defines is not an override and is outside it. A property's setter or deleter counts as a property on either side of the comparison, so a subclass that redefines a base property through its setter keeps the kind. An override that keeps the kind can still break the base through its signature or its return type, which the rule does not reach.

## Validator
For each `def`, `async def`, `@property` or `@override` line the hunk adds or changes inside a class body, read the class's bases and open each base class — in this file or the module it is imported from — for a member of the same name. Classify both members twice: `async def` or plain `def`, and property (a `@property` getter, a `@<name>.setter` or a `@<name>.deleter`) or method. Validator question: **Does a member in the diff override a base-class member of the same name while being of a different kind — async against non-async, or property against method?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-136`, severity major, `file`, `symbol`, `code` = the overriding `def` or `async def` line with its decorators, `fix` = the override rewritten in the base member's kind, such as `async def bore(self, insect):`, `rationale` = the base member's kind against the override's kind and the use written against the base — an `await`, a call or an attribute read — that the mismatch breaks).

## Source
- Pylint invalid-overridden-method (W0236) (pylint-dev/pylint pylint/checkers/classes/class_checker.py) — 'Used when we detect that a method was overridden in a way that does not match its base class which could result in potential bugs at runtime.' (fetched)
- Source of pylint/checkers/classes/class_checker.py §_check_invalid_overridden_method (pylint-dev/pylint pylint/checkers/classes/class_checker.py) — 'if parent_is_property and not current_is_property:' ; 'elif not parent_is_property and current_is_property:' ; 'or is_property_setter_or_deleter(parent_function_node)' ; 'or is_property_setter_or_deleter(function_node)' ; 'if parent_is_async and not current_is_async:' ; 'elif not parent_is_async and current_is_async:' (fetched)
- Pylint invalid-overridden-method (W0236) (pylint-dev/pylint doc/data/messages/i/invalid-overridden-method/bad.py) — 'def bore(self, insect):  # [invalid-overridden-method]' (fetched)
- mypy docs/source/class_basics.rst §Overriding statically typed methods (python/mypy docs/source/class_basics.rst) — 'When overriding a statically typed method, mypy checks that the override has a compatible signature' ; 'You can also override a statically typed method with a dynamically typed one.' ; 'As always, relying on dynamically typed code can be unsafe.' ; 'There is no runtime enforcement that the method override returns a value that is compatible with the original return type, since annotations have no effect at runtime' (fetched)
- CPython Doc/reference/compound_stmts.rst §Coroutine function definition (python/cpython Doc/reference/compound_stmts.rst) — 'Functions defined with ``async def`` syntax are always coroutine functions' (fetched)
- CPython Doc/glossary.rst §coroutine function (python/cpython Doc/glossary.rst) — 'A function which returns a :term:`coroutine` object.' (fetched)
- CPython Doc/reference/expressions.rst §Await expression (python/cpython Doc/reference/expressions.rst) — 'Suspend the execution of :term:`coroutine` on an :term:`awaitable` object.' (fetched)
- Caveat: the TypeError in the Example's comment is what awaiting a non-awaitable result raises; the cited texts state the mismatch and its runtime risk, not that exception.

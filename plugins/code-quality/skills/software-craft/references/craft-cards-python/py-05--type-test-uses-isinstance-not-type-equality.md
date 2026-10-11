---
title: A Python type test uses isinstance() and never compares type(obj) with == or !=
rule_id: PY-05
domain: code
step: [implement, review]
applies_to: [python, object-oriented]
triggers: ['(?<![.\w])type\([^)]*\)\s*[=!]=', '[=!]=\s*type\(']
scope: hunk
check_kind: mechanical
severity_default: minor
---

# A Python type test uses isinstance() and never compares type(obj) with == or !=

## Thesis
A Python type test is written `isinstance(obj, T)`, which accepts instances of T and of its subclasses, and does not compare `type(obj)` with `==` or `!=`.

## Rationale
isinstance() checks whether an object is an instance of a class or of a subclass of it, while a direct type comparison does not consider the inheritance hierarchy, so `type(obj) == T` rejects instances of subclasses of T that isinstance() accepts. Object type comparisons should always use isinstance() instead of comparing types directly.

## Example
```python
bad:  if type(value) == int:
          total += value
good: if isinstance(value, int):
          total += value
```

## Limits
Sources differ on an exact type match. One position holds that object type comparisons should always use isinstance() instead of comparing types directly, with no exception for an exact match; a second position checks object type comparisons using `==` and other comparison operators, and holds that for an exact type match `is` or `is not` is the form to use; a third position holds that isinstance() is generally preferred over direct type comparison because it considers the inheritance hierarchy. Whether the code means an exact type match separates the positions, and both the first and the second position reject `type(obj) == T`, so the finding is the `==` or `!=` form and `type(obj) is T` is outside it. A check of type comparisons made with `==` may produce false positives with libraries that override the `==` (`__eq__`) operator, such as NumPy, Pandas and SQLAlchemy, where converting `==` to `is` or `is not` changes the behaviour of the code; the finding needs an operand that is a type() call.

## Validator
Grep the hunk for a `type(...)` call followed by `==` or `!=`, and for `== type(` and `!= type(`. Confirm the call is the builtin type() with one argument, not a shadowed name, a method such as `x.type(...)` or a three-argument class creation. Validator question: **Does the hunk compare the result of a one-argument builtin type() call with `==` or `!=`?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-05`, severity minor, `file`, `symbol`, `code` = the type comparison as written, `fix` = `isinstance(value, int)`, with a tuple of classes for several, or `type(value) is int` where the code means an exact type match, `rationale` = a direct type comparison ignores the inheritance hierarchy, so instances of subclasses fail the test).

## Source
- PEP 8 §Programming Recommendations (python/peps peps/pep-0008.rst) — 'Object type comparisons should always use isinstance() instead of comparing types directly:' (fetched)
- Ruff E721 type-comparison (astral-sh/ruff crates/ruff_linter/src/rules/pycodestyle/rules/type_comparison.rs) — 'Unlike a direct type comparison, `isinstance` will also check if an object is an instance of a class or a subclass thereof. If you want to check for an exact type match, use `is` or `is not`.' (fetched)
- Ruff E721 type-comparison (astral-sh/ruff crates/ruff_linter/src/rules/pycodestyle/rules/type_comparison.rs) — 'Checks for object type comparisons using `==` and other comparison operators.' (fetched)
- Ruff E721 type-comparison (astral-sh/ruff crates/ruff_linter/src/rules/pycodestyle/rules/type_comparison.rs) — 'When using libraries that override the `==` (`__eq__`) operator (such as NumPy, Pandas, and SQLAlchemy), this rule may produce false positives, as converting from `==` to `is` or `is not` will change the behavior of the code.' (fetched)
- SonarSource python S6660 (SonarSource/sonar-python python-checks/src/main/resources/org/sonar/l10n/py/rules/python/S6660.html) — 'In Python, using the isinstance() function is generally preferred over direct type comparison for several reasons' (fetched)
- SonarSource python S6660 (SonarSource/sonar-python python-checks/src/main/resources/org/sonar/l10n/py/rules/python/S6660.html) — 'Compatibility with inheritance: isinstance() considers inheritance hierarchy, whereas direct type comparison does not.' (fetched)

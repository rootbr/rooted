---
title: A Python class assigns __slots__ a tuple or another container of attribute names, never a bare string
rule_id: PY-141
domain: design
step: [implement, review]
applies_to: [python, object-oriented]
triggers: ['^\s*__slots__\s*(?::[^=]+)?=\s*[rRbBuU]?["'']', '^\s*__slots__\s*(?::[^=]+)?=\s*\(\s*[rRbBuU]?["''][^"'']*["'']\s*\)']
scope: hunk
check_kind: mechanical
severity_default: suggestion
---

# A Python class assigns __slots__ a tuple or another container of attribute names, never a bare string

## Thesis
A Python class body assigns `__slots__` a non-string iterable of attribute names, most commonly a tuple such as `('name',)`, and never a single `str`; a single string in parentheses without a trailing comma, `('name')`, is the same `str`.

## Rationale
The class variable `__slots__` can be assigned a string, an iterable or a sequence of strings with the variable names used by instances, and a string assigned to it is interpreted as a single attribute name rather than as an iterable of attribute names. Code that iterates over the `__slots__` value may expect a sequence of attributes but iterates over the characters of the string instead, so `__slots__ = 'name'` hands that code `'n'`, `'a'`, `'m'`, `'e'`, which can cause confusion. Parentheses alone do not make a tuple: a tuple display with exactly one element requires a trailing comma, and without it `('name')` is a parenthesized group whose value is the single string. To use a single string attribute in `__slots__`, the string is wrapped in an iterable container type such as a tuple.

## Example
```python
bad:  class Record:
          __slots__ = 'name'
      class Entry:
          __slots__ = ('name')
good: class Record:
          __slots__ = ('name',)
      class Entry:
          __slots__ = ('name',)
```

## Limits
Any non-string iterable is a valid `__slots__` value: a tuple, a list, or a dict, whose keys are used as the slot names and whose values can provide per-attribute docstrings recognised by `inspect.getdoc` and shown by `help`. A bare string is legal and still declares its one slot, so the defect lies in the `__slots__` value that iterating code misreads, not in the instances. An iterator assigned to `__slots__` is a separate trap outside this rule: a descriptor is created for each of its values, but the `__slots__` attribute is then an empty iterator.

## Validator
Grep the hunk for an assignment to `__slots__`, with or without an annotation, whose right-hand side opens with a string literal or is one string literal in parentheses with no comma. Open the enclosing class to confirm the assignment sits directly in the class body, and when the right-hand side is a name, a call or a conditional expression, trace it to the value it evaluates to. Pass a tuple, a list, a set, a dict or any other non-string iterable, and a one-element tuple written with its trailing comma. Validator question: **Does a class body assign `__slots__` a value that evaluates to a single `str` instead of a container of names?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-141`, severity suggestion, `file`, `symbol`, `code` = the `__slots__` assignment line verbatim, `fix` = the same names in a tuple, such as `__slots__ = ('name',)`, `rationale` = a `str` assigned to `__slots__` is one slot name, so code that iterates the class's `__slots__` gets its characters instead of attribute names).

## Source
- Ruff PLC0205 single-string-slots (astral-sh/ruff crates/ruff_linter/src/rules/pylint/rules/single_string_slots.rs) — 'Any string iterable may be assigned to `__slots__` (most commonly, a `tuple` of strings).'; 'If a string is assigned to `__slots__`, it is interpreted as a single attribute name, rather than an iterable of attribute names. This can cause confusion, as users that iterate over the `__slots__` value may expect to iterate over a sequence of attributes, but would instead iterate over the characters of the string.'; 'To use a single string attribute in `__slots__`, wrap the string in an iterable container type, like a `tuple`.' (fetched)
- Pylint single-string-used-for-slots (C0205) (pylint-dev/pylint pylint/checkers/classes/class_checker.py) — 'Used when a class __slots__ is a simple string, rather than an iterable.' (fetched)
- CPython Doc/reference/datamodel.rst §__slots__ (python/cpython Doc/reference/datamodel.rst) — 'This class variable can be assigned a string, iterable, or sequence of strings with variable names used by instances.'; 'Any non-string :term:`iterable` may be assigned to *__slots__*.'; 'the dictionary keys will be used as the slot names'; 'The values of the dictionary can be used to provide per-attribute docstrings'; 'created for each of the iterator's values'; 'However, the *__slots__* attribute will be an empty iterator.' (fetched)
- CPython Doc/reference/expressions.rst §Tuple displays (python/cpython Doc/reference/expressions.rst) — 'To avoid ambiguity, if a tuple display has exactly one element, it requires a trailing comma.'; '# no comma: single string' (fetched)
- Caveat: the data model accepts a single string as a `__slots__` value that declares one slot; the rule rests on what iterating code reads from that value, not on a declaration error.

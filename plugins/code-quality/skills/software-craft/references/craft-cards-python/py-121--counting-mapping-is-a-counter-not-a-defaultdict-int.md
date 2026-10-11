---
title: A Python mapping that counts occurrences is a collections.Counter rather than a defaultdict(int), which records every missing key it is asked for
rule_id: PY-121
domain: performance
step: [implement, review]
applies_to: [python]
triggers: ['\bdefaultdict\(\s*(int|lambda\s*:\s*0)\s*[,)]']
scope: file
check_kind: semantic
severity_default: minor
---

# A Python mapping that counts occurrences is a collections.Counter rather than a defaultdict(int), which records every missing key it is asked for

## Thesis
A Python mapping that counts occurrences of hashable items is a `collections.Counter` rather than a `defaultdict(int)` wherever the mapping is read by subscript with a key that may never have been counted, in its own file or in the code it is returned to or stored for, because a defaultdict records every missing key it is accessed with under the default value, which costs excessive memory, while a Counter returns a zero count for a missing item instead of raising `KeyError`.

## Rationale
`collections.defaultdict` is a dict subclass that overrides one method, `__missing__`, which dict's `__getitem__` calls when the requested key is not found. When `default_factory` is not None, `__missing__` calls it without arguments to provide a default value for the key, inserts that value in the dictionary for the key and returns it. With `int` as the factory, or a lambda returning 0, a subscript read of a key that was never counted therefore adds a zero entry: the mapping records missing keys with the default value when accessed and grows by one entry for each distinct uncounted key it is read with, beside the items it counts. `collections.Counter` is the dict subclass for counting hashable objects; its constructor counts the elements of an iterable, and it returns a zero count for a missing item instead of raising `KeyError`, so a read of an uncounted item yields the same 0 without the memory the recorded keys cost.

## Example
```python
bad:  counts = defaultdict(int)
      for item in items:
          counts[item] += 1
      found = [counts[key] for key in keys]
good: counts = Counter(items)
      found = [counts[key] for key in keys]
```

## Limits
A `defaultdict(int)` whose subscripts are all increments of the items being counted, and whose counts are read back through `items()`, `keys()`, `get()` or the `in` operator, holds only counted keys: for a first-seen item the factory supplies the zero count and the increment builds the count, and `__missing__` is not called for any operation besides `__getitem__`, so `get()` returns its default like a plain dict rather than using `default_factory`. A subscript read with a key taken from the mapping's own `keys()` or `items()` finds the key present and inserts nothing. The rule reaches mappings of counts built with `defaultdict(int)` or a zero-returning factory; a defaultdict with another factory, such as `list` for grouping pairs into a dictionary of lists, is outside it.

## Validator
Grep the hunk for `defaultdict(int` and `defaultdict(lambda: 0`. Open the file and take the name the mapping is bound to. List every subscript of that name: an augmented assignment or assignment target (`counts[key] += 1`, `counts[key] = n`) counts an item; every other subscript, in an expression, a condition, a call argument, a comprehension or a format string, is a read. For each read, trace its key: a key drawn from the mapping's own `keys()` or `items()` is present; a key from another iterable, a parameter, a lookup table or input may be missing. Then trace whether the mapping leaves the code that counts as a defaultdict: returned to callers, or stored on an attribute or a module-level name. Validator question: **Is a counting `defaultdict(int)` or `defaultdict(lambda: 0)` read by subscript with a key that may never have been counted, or returned or stored where other code can read it so?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-121`, severity minor, `file`, `symbol`, `code` = the `defaultdict(int)` construction and the subscript read or the return that exposes it, verbatim from the diff, `fix` = the mapping built as `collections.Counter(items)`, or as `Counter()` incremented in the same loop, and read the same way, `rationale` = names that a subscript read of a missing key inserts a zero entry into a defaultdict while a Counter returns a zero count for a missing item).

## Source
- flake8-bugbear B910 (https://raw.githubusercontent.com/PyCQA/flake8-bugbear/main/README.rst) — 'Use Counter() instead of defaultdict(int) to avoid excessive memory use as the default dict will record missing keys with the default value when accessed.' (fetched); B910 is listed among the README's opinionated warnings, which are disabled by default.
- CPython Doc/library/collections.rst §defaultdict objects (https://raw.githubusercontent.com/python/cpython/main/Doc/library/collections.rst) — ':class:`defaultdict` is a subclass of the built-in :class:`dict` class.'; 'It overrides one method and adds one writable instance variable.'; 'If :attr:`default_factory` is not ``None``, it is called without arguments to provide a default value for the given *key*, this value is inserted in the dictionary for the *key*, and returned.'; 'This method is called by the :meth:`~object.__getitem__` method of the :class:`dict` class when the requested key is not found'; 'Note that :meth:`__missing__` is *not* called for any operations besides :meth:`~object.__getitem__`.'; 'This means that :meth:`~dict.get` will, like normal dictionaries, return ``None`` as a default rather than using :attr:`default_factory`.' (fetched)
- CPython Doc/library/collections.rst §defaultdict Examples (https://raw.githubusercontent.com/python/cpython/main/Doc/library/collections.rst) — 'Using :class:`list` as the :attr:`~defaultdict.default_factory`, it is easy to group a sequence of key-value pairs into a dictionary of lists'; 'When a letter is first encountered, it is missing from the mapping, so the :attr:`~defaultdict.default_factory` function calls :func:`int` to supply a default count of zero.'; 'The increment operation then builds up the count for each letter.' (fetched)
- CPython Doc/library/collections.rst §Counter objects (https://raw.githubusercontent.com/python/cpython/main/Doc/library/collections.rst) — 'A :class:`Counter` is a :class:`dict` subclass for counting :term:`hashable` objects.'; 'Elements are counted from an *iterable* or initialized from another *mapping* (or counter)'; 'Counter objects have a dictionary interface except that they return a zero count for missing items instead of raising a :exc:`KeyError`' (fetched)

---
title: Python dict.fromkeys is not given a mutable value, because every key then shares the one object, and per-key containers are built with a dict comprehension
rule_id: PY-54
domain: performance
step: [implement, review]
applies_to: [python]
triggers: ['[.]fromkeys\(.*,\s*(\[|\{|set\(|list\(|dict\(|defaultdict\(|bytearray\()', '[.]fromkeys\([^,()]+(\([^()]*\))?\s*,']
scope: hunk
check_kind: mechanical
severity_default: major
---

# Python dict.fromkeys is not given a mutable value, because every key then shares the one object, and per-key containers are built with a dict comprehension

## Thesis
Where each key of a new Python dict needs its own mutable value, such as an empty list, dict or set, the dict is built with a dict comprehension such as `{key: [] for key in keys}`, and `dict.fromkeys()` is given no mutable value, because `fromkeys` stores the one value object it is passed under every key, so a change made through one key shows under all of them.

## Rationale
`dict.fromkeys(iterable, value)` creates a new dictionary with keys from the iterable and values set to `value`. All of the values refer to just a single instance, so it generally doesn't make sense for `value` to be a mutable object such as an empty list. If that object is modified, all values are modified: with an empty list as the value, appending to any one entry appends to all entries. A dict comprehension generates a dictionary with distinct instances of the default value, which restores separate per-key state.

## Example
```python
bad:  buckets = dict.fromkeys(keys, [])
      buckets[first].append(item)
good: buckets = {key: [] for key in keys}
      buckets[first].append(item)
```

## Limits
`dict.fromkeys()` with its default value `None`, or with a value that is never modified, is outside the rule. A program that relies on one shared mutable instance under every key is correct with `fromkeys`; a comprehension would change its behavior by using a distinct object for every value.

## Validator
Grep the hunk for each `fromkeys(` call with a second argument. Decide whether that argument evaluates to a mutable object: a list, dict or set display, `list()`, `dict()`, `set()`, `defaultdict()`, `bytearray()`, or a name bound to one of them. Trace how the resulting dict's values are used: a value mutated through one key (`append`, `add`, `update`, item assignment) where each key should hold its own state is the defect; code that deliberately shares one object across the keys is not. Validator question: **Is `dict.fromkeys()` given a mutable value object while the keys are meant to hold separate values?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-54`, severity major, `file`, `symbol`, `code` = the `fromkeys(...)` call, `fix` = a dict comprehension such as `{key: [] for key in keys}`, `rationale` = every key of the `fromkeys` result refers to the one mutable value object, so a change through one key shows under all of them).

## Source
- CPython Doc/builtins/stdtypes.rst §Mapping Types, dict.fromkeys (https://raw.githubusercontent.com/python/cpython/main/Doc/builtins/stdtypes.rst) — 'Create a new dictionary with keys from *iterable* and values set to *value*.' (fetched)
- CPython Doc/builtins/stdtypes.rst §Mapping Types, dict.fromkeys (https://raw.githubusercontent.com/python/cpython/main/Doc/builtins/stdtypes.rst) — 'All of the values refer to just a single instance, so it generally doesn't make sense for *value* to be a mutable object such as an empty list.  To get distinct values, use a :ref:`dict comprehension <dict>` instead.' (fetched)
- CPython Doc/builtins/stdtypes.rst §Mapping Types, dict.fromkeys (https://raw.githubusercontent.com/python/cpython/main/Doc/builtins/stdtypes.rst) — '*value* defaults to ``None``.' (fetched)
- Ruff RUF024 mutable-fromkeys-value (astral-sh/ruff crates/ruff_linter/src/rules/ruff/rules/mutable_fromkeys_value.rs) — 'All values in the dictionary created by the `dict.fromkeys` method refer to the same instance of the provided object. If that object is modified, all values are modified, which can lead to unexpected behavior.' (fetched)
- Ruff RUF024 mutable-fromkeys-value (astral-sh/ruff crates/ruff_linter/src/rules/ruff/rules/mutable_fromkeys_value.rs) — 'For example, if the empty list (`[]`) is provided as the default value, all values in the dictionary will use the same list; as such, appending to any one entry will append to all entries.' (fetched)
- Ruff RUF024 mutable-fromkeys-value (astral-sh/ruff crates/ruff_linter/src/rules/ruff/rules/mutable_fromkeys_value.rs) — 'Instead, use a comprehension to generate a dictionary with distinct instances of the default value.' (fetched)
- Ruff RUF024 mutable-fromkeys-value (astral-sh/ruff crates/ruff_linter/src/rules/ruff/rules/mutable_fromkeys_value.rs) — 'the edit will change the behavior of the program by using a distinct object for every value in the dictionary, rather than a shared mutable instance. In some cases, programs may rely on the previous behavior.' (fetched)
- flake8-bugbear B046 (PyCQA/flake8-bugbear README.rst) — 'Mutable value passed to ``dict.fromkeys()``. The same object is shared by every key, so changing it for one key changes it for all of them. Use a dict comprehension instead, e.g. ``{key: [] for key in keys}``.' (fetched)

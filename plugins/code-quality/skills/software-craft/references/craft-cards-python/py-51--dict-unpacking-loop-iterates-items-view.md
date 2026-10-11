---
title: A loop or comprehension that unpacks key and value pairs from a Python dict iterates its items() view, because iterating the dict itself yields only the keys
rule_id: PY-51
domain: performance
step: [implement, review]
applies_to: [python]
triggers: ['^\s*(async\s+)?for\s+\(?\w+\s*,\s*\w+\)?\s+in\s+[\w.]+(\[[^\]]*\])?\s*:', '\bfor\s+\(?\w+\s*,\s*\w+\)?\s+in\s+[\w.]+\s*(\bif\b|[\]})])']
scope: hunk
check_kind: mechanical
severity_default: major
---

# A loop or comprehension that unpacks key and value pairs from a Python dict iterates its items() view, because iterating the dict itself yields only the keys

## Thesis
A Python `for` loop or comprehension that unpacks a key and its value from a dict iterates the dict's `items()` view, as in `for key, value in mapping.items()`, because iterating the dict itself yields only its keys.

## Rationale
Iterating a dict returns an iterator over its keys: `iter(d)` is a shortcut for `iter(d.keys())`. In `for k, v in d`, and in a comprehension such as `{k: v for k, v in d}`, the two targets therefore unpack each key itself instead of receiving a key and its value. When the keys are not tuples of two elements, this can fail with a runtime error. When a key is an iterable such as a string, it can lead to errors or subtle bugs: a key `"hi"` gives `k` the value `'h'` and `v` the value `'i'`. The `items()` method retrieves the key and its corresponding value at the same time, which is the pairing the two targets mean.

## Example
```python
bad:  for name, total in totals:
          print(name, total)
      scaled = {name: total * rate for name, total in totals}
good: for name, total in totals.items():
          print(name, total)
      scaled = {name: total * rate for name, total in totals.items()}
```

## Limits
A dict whose keys are tuples of two elements, iterated so that each key is unpacked into the two targets, is correct without `items()`; adding `items()` there changes the runtime behavior. One analyzer that checks this pattern cannot consistently infer the type of a dict's keys, so the key type, read from the code, decides each case. The rule reaches only an iterated object that is a dict; a two-target loop over a list of pairs, a `zip()` or an `enumerate()` is outside it.

## Validator
Grep the hunk for a `for` clause with two targets, in a statement or a comprehension, whose iterable is a bare name, an attribute or a subscript with no call. Trace that iterable within the hunk to its assignment, parameter annotation or construction: a dict display, `dict()`, a dict comprehension, `defaultdict`, `Counter`, `OrderedDict`, or a `dict[...]` or `Mapping[...]` annotation makes it a dict. For a dict, read its key type from the same place; keys that are tuples of two elements which the loop means to unpack are not a finding. Validator question: **Does a two-target `for` loop or comprehension iterate a dict directly, without `items()`, where the dict's keys are not pairs the loop means to unpack?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-51`, severity major, `file`, `symbol`, `code` = the `for` clause that iterates the dict, `fix` = the same clause iterating `mapping.items()`, `rationale` = iterating a dict yields only its keys, so each key is unpacked into the two targets).

## Source
- Ruff PLE1141 dict-iter-missing-items (astral-sh/ruff crates/ruff_linter/src/rules/pylint/rules/dict_iter_missing_items.rs) — 'When iterating over a dictionary in a for loop, if a dictionary is unpacked without calling `.items()`, it could lead to a runtime error if the keys are not a tuple of two elements.' (fetched)
- Ruff PLE1141 dict-iter-missing-items (astral-sh/ruff crates/ruff_linter/src/rules/pylint/rules/dict_iter_missing_items.rs) — 'The tuple key is unpacked into `x` and `y` instead of the key and values. This means that the suggested fix of using `d.items()` would result in different runtime behavior.' (fetched)
- Ruff PLE1141 dict-iter-missing-items (astral-sh/ruff crates/ruff_linter/src/rules/pylint/rules/dict_iter_missing_items.rs) — 'Ruff cannot consistently infer the type of a dictionary's keys.' (fetched); the rule is in Ruff's preview set.
- SonarSource python S7517 (SonarSource/sonar-python python-checks/src/main/resources/org/sonar/l10n/py/rules/python/S7517.html) — 'Python iterates over the dictionary’s keys by default. If the intention is to access both the key and the value, omitting .items() leads to unexpected behavior. In such cases, the k variable would receive the key, and the v variable would attempt to unpack the key itself, which can lead to errors or subtle bugs if the key is iterable, like a string.' (fetched)
- SonarSource python S7517 (SonarSource/sonar-python python-checks/src/main/resources/org/sonar/l10n/py/rules/python/S7517.html) — 'For example, if a key is a string like "hi", k would be 'h' and v would be 'i'.' (fetched)
- SonarSource python S7517 (SonarSource/sonar-python python-checks/src/main/resources/org/sonar/l10n/py/rules/python/S7517.html) — 'When iterating directly over a dictionary e.g., for k, v in some_dict: or {k: v for k, v in some_dict}, Python iterates over the dictionary’s keys by default.' (fetched)
- SonarSource python S7517 (SonarSource/sonar-python python-checks/src/main/resources/org/sonar/l10n/py/rules/python/S7517.html) — 'This rule raises an issue when a dictionary is iterated over without explicitly calling the .items() method.' (fetched)
- Pylint dict-iter-missing-items (E1141) (pylint-dev/pylint doc/data/messages/d/dict-iter-missing-items/bad.py) — 'for city, population in data:  # [dict-iter-missing-items]' (fetched)
- CPython Doc/builtins/stdtypes.rst §Mapping Types, iter(d) (https://raw.githubusercontent.com/python/cpython/main/Doc/builtins/stdtypes.rst) — 'Return an iterator over the keys of the dictionary.  This is a shortcut for ``iter(d.keys())``.' (fetched)
- CPython Doc/tutorial/datastructures.rst §Looping Techniques (https://raw.githubusercontent.com/python/cpython/main/Doc/tutorial/datastructures.rst) — 'When looping through dictionaries, the key and corresponding value can be retrieved at the same time using the :meth:`~dict.items` method.' (fetched)

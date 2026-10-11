---
title: A Python loop that reads both the keys and the values of a dict iterates items() and reads each value from its loop target, never again by key
rule_id: PY-119
domain: performance
step: [implement, refactor, review]
applies_to: [python]
triggers: ['^\s*for\s+\w+\s+in\s+[A-Za-z_][\w.]*[.]keys\(\)\s*:', '^\s*for\s+\w+\s*,\s*\w+\s+in\s+[A-Za-z_][\w.]*[.]items\(\)\s*:', '^\s*for\s+\w+\s+in\s+[A-Za-z_][\w.]*\s*:']
scope: hunk
check_kind: semantic
severity_default: minor
---

# A Python loop that reads both the keys and the values of a dict iterates items() and reads each value from its loop target, never again by key

## Thesis
A Python for loop over a dict whose body reads each key's value iterates d.items() and unpacks the key and the value, rather than iterating the keys, as `for k in d` or `for k in d.keys()`, and reading d[k]; a loop already over d.items() reads the value from its unpacked target, not again as d[k].

## Rationale
When looping through a dict, its items() method retrieves the key and the corresponding value at the same time. Iterating over a dict with items() is semantically clearer and more efficient than extracting the value with the key. Inside a loop over items() the current value is already available alongside its key, so using the key to look up the value is unnecessary.

## Example
```python
bad:  def report(scores):
          for name in scores:
              print(name, scores[name])
good: def report(scores):
          for name, score in scores.items():
              print(name, score)
```

## Limits
A loop whose body reads only the keys has no value to unpack and is out of reach. The rule concerns the value of the dict being iterated, extracted by explicit indexing with the loop's own key: a lookup in a different mapping, or under another key, is out of reach.

## Validator
Grep the hunk for `for <k> in <d>:`, `for <k> in <d>.keys():` and `for <k>, <v> in <d>.items():`. Confirm at hunk scope that `<d>` is a dict, from a dict display, a dict() call, or a name or attribute annotated or assigned as a dict, then read the loop body for a load of `<d>[<k>]` with the loop's own key variable on the iterated dict. Validator question: **Does a loop over a dict's keys, or over its items(), read the iterated dict's value as d[k] with the loop's key variable?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-119`, severity minor, `file`, `symbol`, `code` = the `for` line and the `d[k]` read, verbatim from the diff, `fix` = `for k, v in d.items():` with the body using `v`, in Python, `rationale` = items() yields each key together with its value, so extracting the value again by key is unnecessary and less efficient).

## Source
- CPython Doc/tutorial/datastructures.rst §Looping Techniques (https://raw.githubusercontent.com/python/cpython/main/Doc/tutorial/datastructures.rst) — 'When looping through dictionaries, the key and corresponding value can be retrieved at the same time using the :meth:`~dict.items` method.' (fetched)
- Ruff PLC0206 dict-index-missing-items (astral-sh/ruff crates/ruff_linter/src/rules/pylint/rules/dict_index_missing_items.rs) — 'Iterating over a dictionary with `.items()` is semantically clearer and more efficient than extracting the value with the key.' (fetched)
- Ruff PLC0206 dict-index-missing-items (astral-sh/ruff crates/ruff_linter/src/rules/pylint/rules/dict_index_missing_items.rs) — 'Checks for dictionary iterations that extract the dictionary value via explicit indexing, instead of using `.items()`.' (fetched)
- Pylint consider-using-dict-items (C0206) (pylint-dev/pylint doc/user_guide/checkers/features.rst) — 'Emitted when iterating over the keys of a dictionary and accessing the value by index lookup. Both the key and value can be accessed by iterating using the .items() method of the dictionary instead.' (fetched)
- Ruff PLR1733 unnecessary-dict-index-lookup (astral-sh/ruff crates/ruff_linter/src/rules/pylint/rules/unnecessary_dict_index_lookup.rs) — 'When iterating over a dict via `.items()`, the current value is already available alongside its key. Using the key to look up the value is unnecessary.' (fetched)
- Pylint unnecessary-dict-index-lookup (R1733) (pylint-dev/pylint doc/user_guide/checkers/features.rst) — 'Emitted when iterating over the dictionary items (key-item pairs) and accessing the value by index lookup. The value can be accessed directly instead.' (fetched)

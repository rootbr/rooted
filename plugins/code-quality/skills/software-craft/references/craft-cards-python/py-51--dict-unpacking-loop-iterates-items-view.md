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

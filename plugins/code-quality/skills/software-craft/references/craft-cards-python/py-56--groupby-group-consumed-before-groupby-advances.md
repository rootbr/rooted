---
title: Each Python itertools.groupby group is consumed or copied into a list before groupby advances, because a group iterator kept past that point yields nothing
rule_id: PY-56
domain: performance
step: [implement, review]
applies_to: [python]
triggers: ['\bgroupby\(', '\b(dict|list|tuple|sorted)\(\s*(itertools[.])?groupby\(']
scope: hunk
check_kind: semantic
severity_default: major
---

# Each Python itertools.groupby group is consumed or copied into a list before groupby advances, because a group iterator kept past that point yields nothing

## Thesis
Each group iterator that `itertools.groupby()` yields is consumed, or copied into a list, before the groupby object advances to the next group. A container that outlives that step holds `list(group)`, not the raw group, so `dict(groupby(...))` and `list(groupby(...))` become a comprehension that copies each group while it is current.

## Rationale
The group that `groupby()` returns is itself an iterator that shares the underlying iterable with the groupby object, so when the groupby object is advanced, the previous group is no longer visible. Every advance to the next group invalidates the previous group iterator, whether it has been iterated or not, and a raw group consumed after the loop has moved on always yields an empty sequence. `dict(groupby(...))`, `list(groupby(...))` and a loop that stores `group` itself all advance groupby before the stored groups are read, so the code processes empty sequences instead of the grouped data. Nothing raises: the result is simply wrong output, which makes the loss hard to debug. Copying the group into a list while it is current keeps its data for later reads.

## Example
```python
bad:  groups = dict(groupby(rows, key=itemgetter(0)))
      for key, group in groupby(rows, key=itemgetter(0)):
          index[key] = group
good: groups = {key: list(group) for key, group in groupby(rows, key=itemgetter(0))}
      for key, group in groupby(rows, key=itemgetter(0)):
          index[key] = list(group)
```

## Limits
A group consumed inside the loop body that received it — iterated, summed, joined or passed to a call that reads it at once — needs no copy; consuming it immediately and never storing the raw iterator is the simplest correct pattern. A tuple, set or other concrete collection serves as well as a list when it is built before the loop advances. Code that uses only the keys, such as `[key for key, _ in groupby(items)]`, needs no copy, because the copy is required only if the group's data is needed later.

## Validator
Grep the hunk for `groupby(`. For each call, open the enclosing function and follow every group iterator the groupby object yields, the second element of each pair. Trace where the raw group goes: into a dict, list or attribute, onto a name read in a later iteration or after the loop, or, through `dict()`, `list()`, `tuple()` or `sorted()` applied to the groupby object itself, into a container built by consuming the whole groupby. Pass a group that is consumed within its own iteration or wrapped in `list()`, `tuple()`, `set()` or a similar constructor before it is stored, and a groupby whose groups are never read.
Validator question: **Is a group iterator from `itertools.groupby()` stored raw and read after the groupby object has advanced past it?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-56`, severity major, `file`, `symbol`, `code` = the groupby call and the statement that stores the raw group, `fix` = the group copied while current, as `{key: list(group) for key, group in groupby(rows, key=itemgetter(0))}` or `index[key] = list(group)`, `rationale` = groupby invalidates the previous group when it advances, so the stored group yields nothing later and no exception signals the loss).

## Source
- Python documentation, library/itertools §groupby (https://docs.python.org/3/library/itertools.html) — 'The returned group is itself an iterator that shares the underlying iterable with groupby(). Because the source is shared, when the groupby() object is advanced, the previous group is no longer visible. So, if that data is needed later, it should be stored as a list' (fetched)
- SonarSource python S8516 (SonarSource/sonar-python python-checks/src/main/resources/org/sonar/l10n/py/rules/python/S8516.html) — 'Every time the outer loop advances to the next group, the previous group iterator is immediately invalidated — regardless of whether it has been iterated or not. Storing a raw group iterator and consuming it after the loop has moved on will always yield an empty sequence.' (fetched)
- SonarSource python S8516 (SonarSource/sonar-python python-checks/src/main/resources/org/sonar/l10n/py/rules/python/S8516.html) — 'Your code will process empty sequences instead of the actual grouped data' (fetched)
- SonarSource python S8516 (SonarSource/sonar-python python-checks/src/main/resources/org/sonar/l10n/py/rules/python/S8516.html) — 'These issues can be difficult to debug because the code does not raise exceptions but simply produces wrong output.' (fetched)
- SonarSource python S8516 (SonarSource/sonar-python python-checks/src/main/resources/org/sonar/l10n/py/rules/python/S8516.html) — 'Consume the group iterator immediately inside the loop body, never storing the raw iterator at all. This is the simplest pattern and avoids any risk of reuse.' (fetched)
- SonarSource python S8516 (SonarSource/sonar-python python-checks/src/main/resources/org/sonar/l10n/py/rules/python/S8516.html) — 'Materialize the group iterator into a concrete collection (list, tuple, set, etc.) before the loop advances.' (fetched)

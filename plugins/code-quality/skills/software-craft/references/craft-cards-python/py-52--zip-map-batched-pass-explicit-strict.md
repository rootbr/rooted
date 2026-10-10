---
title: A Python zip over several iterables, and a multi-iterable map or itertools.batched where the running version has the parameter, passes strict explicitly so unequal lengths are not silently truncated
rule_id: PY-52
domain: performance
step: [implement, review]
applies_to: [python]
triggers: ['\bzip\((?!.*\bstrict\s*=)', '\bmap\(\s*[\w.]+\s*,[^,]+,(?!.*\bstrict\s*=)', '\bbatched\((?!.*\bstrict\s*=)']
scope: hunk
check_kind: mechanical
severity_default: major
---

# A Python zip over several iterables, and a multi-iterable map or itertools.batched where the running version has the parameter, passes strict explicitly so unequal lengths are not silently truncated

## Thesis
A Python `zip()` call over two or more iterables or with a starred argument passes `strict=` explicitly on Python 3.10 and later, and so do such a `map()` call on Python 3.14 and later and every `itertools.batched()` call on Python 3.13 and later: `strict=True` where the iterables must be of equal length or every batch must hold `n` items, `strict=False` where stopping at the shortest iterable or a shorter last batch is intended.

## Rationale
By default `zip()` stops when the shortest iterable is exhausted and ignores the remaining items of the longer iterables, and `map()` over several iterables stops when the shortest iterable is exhausted; the resulting iterator is silently truncated to the length of the shortest iterable. For `zip()` without `strict=True`, any bug that results in iterables of different lengths is silenced, possibly manifesting as a hard-to-find bug in another part of the program: faulty refactoring or logic errors could easily result in silently losing data, and these bugs are difficult to diagnose and difficult even to detect. The standard library's own use of `zip` in the `ast` module created such a bug in `literal_eval`, which silently dropped parts of malformed nodes. `itertools.batched(iterable, n)` yields a last batch shorter than the rest when the length of the iterable is not divisible by `n`. `strict=True` raises `ValueError` when the iterables are exhausted at differing lengths, or when the final batch is shorter than `n`. `strict=False` keeps the default and makes the intention explicit; added as an automatic fix, it preserves the runtime behavior but can obscure situations where the iterables are of unequal length, so the author chooses the intended behavior. The parameter exists from Python 3.10 for `zip()`, 3.13 for `itertools.batched()` and 3.14 for `map()`.

## Example
```python
bad:  for name, score in zip(names, scores):
          ...
      totals = list(map(add, prices, taxes))
      groups = list(batched(rows, size))
good: for name, score in zip(names, scores, strict=True):
          ...
      totals = list(map(add, prices, taxes, strict=True))
      groups = list(batched(rows, size, strict=False))
```

## Limits
A `zip()` that has `itertools.count`, `itertools.cycle`, or `itertools.repeat` without `times` among its arguments is exempt, since these are infinite iterators; one of the two analyzers that check `itertools.batched()` likewise does not report it over an infinite iterator such as `itertools.cycle(...)`. Code that must still run on a Python version older than the one that added the parameter — before 3.10 for `zip()`, before 3.13 for `itertools.batched()`, before 3.14 for `map()` — cannot pass `strict=` and is outside the rule. A `zip()` or `map()` over a single iterable is outside the rule.

## Validator
Grep the hunk for each `zip(`, `map(` and `batched(` call that passes no `strict` keyword. Count the iterables: a `zip()` or `map()` qualifies with two or more iterables (for `map()`, after the function) or a starred argument; every `batched()` call qualifies. Skip a `zip()` with `itertools.count`, `itertools.cycle`, or `itertools.repeat` without `times` among its arguments. Read the project's minimum Python version where the repository declares it (`requires-python`, a classifier, or the linter's target version) and skip a call whose `strict` parameter that version lacks. Decide from the surrounding code whether the inputs must line up: the fix is `strict=True` where they must, `strict=False` where truncation or a short last batch is wanted. Validator question: **Does a qualifying `zip()`, `map()` or `itertools.batched()` call omit `strict=` on a Python version that has the parameter?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-52`, severity major, `file`, `symbol`, `code` = the call without `strict=`, `fix` = the same call with `strict=True`, or with `strict=False` where truncation or a shorter last batch is intended, `rationale` = by default the call silently truncates to the shortest iterable or yields a shorter last batch, so a length mismatch loses data without an error).

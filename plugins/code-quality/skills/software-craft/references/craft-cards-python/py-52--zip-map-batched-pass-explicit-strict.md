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

## Source
- Ruff B905 zip-without-explicit-strict (astral-sh/ruff crates/ruff_linter/src/rules/flake8_bugbear/rules/zip_without_explicit_strict.rs) — 'Checks for `zip` calls without an explicit `strict` parameter when called with two or more iterables, or any starred argument.' (fetched)
- Ruff B905 zip-without-explicit-strict (astral-sh/ruff crates/ruff_linter/src/rules/flake8_bugbear/rules/zip_without_explicit_strict.rs) — 'By default, if the iterables passed to `zip` are of different lengths, the resulting iterator will be silently truncated to the length of the shortest iterable. This can lead to subtle bugs. Pass `strict=True` to raise a `ValueError` if the iterables are of non-uniform length. Alternatively, if the iterables are deliberately of different lengths, pass `strict=False` to make the intention explicit.' (fetched)
- Ruff B905 zip-without-explicit-strict (astral-sh/ruff crates/ruff_linter/src/rules/flake8_bugbear/rules/zip_without_explicit_strict.rs) — 'While adding `strict=False` preserves the runtime behavior, it can obscure situations where the iterables are of unequal length. Ruff prefers to alert users so they can choose the intended behavior themselves.' (fetched)
- Ruff B912 map-without-explicit-strict (astral-sh/ruff crates/ruff_linter/src/rules/flake8_bugbear/rules/map_without_explicit_strict.rs) — 'Checks for `map` calls without an explicit `strict` parameter when called with two or more iterables, or any starred argument.' (fetched)
- Ruff B912 map-without-explicit-strict (astral-sh/ruff crates/ruff_linter/src/rules/flake8_bugbear/rules/map_without_explicit_strict.rs) — 'This rule applies to Python 3.14 and later, where `map` accepts a `strict` keyword argument.' (fetched)
- Ruff B911 batched-without-explicit-strict (astral-sh/ruff crates/ruff_linter/src/rules/flake8_bugbear/rules/batched_without_explicit_strict.rs) — 'By default, if the length of the iterable is not divisible by the second argument to `itertools.batched`, the last batch will be shorter than the rest.' (fetched)
- Ruff B911 batched-without-explicit-strict (astral-sh/ruff crates/ruff_linter/src/rules/flake8_bugbear/rules/batched_without_explicit_strict.rs) — 'In Python 3.13, a `strict` parameter was added which allows controlling if the batches must be of uniform length.' (fetched)
- Ruff B911 batched-without-explicit-strict (astral-sh/ruff crates/ruff_linter/src/rules/flake8_bugbear/rules/batched_without_explicit_strict.rs) — 'Unlike the upstream `B911`, this rule will not report infinite iterators (e.g., `itertools.cycle(...)`).' (fetched)
- flake8-bugbear B905 (PyCQA/flake8-bugbear README.rst) — 'The ``strict=`` argument was added in Python 3.10, so don't enable this flag for code that should work on <3.10.' (fetched)
- flake8-bugbear B905 (PyCQA/flake8-bugbear README.rst) — '(with times=None) since they are infinite iterators.' (fetched); the exclusion list names `itertools.count`, `itertools.cycle` and `itertools.repeat`.
- flake8-bugbear B911 (PyCQA/flake8-bugbear README.rst) — '``strict=True`` causes the resulting iterator to raise a ``ValueError`` if the final batch is shorter than ``n``.' (fetched)
- flake8-bugbear B911 (PyCQA/flake8-bugbear README.rst) — 'The ``strict=`` argument was added in Python 3.13, so don't enable this flag for code that should work on <3.13.' (fetched)
- flake8-bugbear B912 (PyCQA/flake8-bugbear README.rst) — '``strict=True`` causes the resulting iterator to raise a ``ValueError`` if the arguments are exhausted at differing lengths.' (fetched)
- CPython Doc/builtins/functions.rst §zip (https://raw.githubusercontent.com/python/cpython/main/Doc/builtins/functions.rst) — 'By default, :func:`zip` stops when the shortest iterable is :term:`exhausted`. It will ignore the remaining items in the longer iterables, cutting off the result to the length of the shortest iterable' (fetched)
- CPython Doc/builtins/functions.rst §zip (https://raw.githubusercontent.com/python/cpython/main/Doc/builtins/functions.rst) — 'Without the ``strict=True`` argument, any bug that results in iterables of different lengths will be silenced, possibly manifesting as a hard-to-find bug in another part of the program.' (fetched)
- CPython Doc/builtins/functions.rst §map (https://raw.githubusercontent.com/python/cpython/main/Doc/builtins/functions.rst) — 'With multiple iterables, the iterator stops when the shortest iterable is :term:`exhausted`.' (fetched)
- CPython Doc/library/itertools.rst §batched (https://raw.githubusercontent.com/python/cpython/main/Doc/library/itertools.rst) — 'If *strict* is true, will raise a :exc:`ValueError` if the final batch is shorter than *n*.' (fetched)
- PEP 618 §Motivation (raw.githubusercontent.com/python/peps/main/peps/pep-0618.rst) — 'default behavior of ``zip`` means that faulty refactoring or logic errors could easily result in silently losing data.  These bugs are not only difficult to diagnose, but difficult to even detect at all.' (fetched)
- PEP 618 §Motivation (raw.githubusercontent.com/python/peps/main/peps/pep-0618.rst) — 'the use of ``zip`` in the standard-library ``ast`` module created a bug in ``literal_eval`` which `silently dropped parts of malformed nodes' (fetched)

---
title: A Python generator ends with return and never raises StopIteration or lets one escape from next, because since Python 3.7 that exception becomes a RuntimeError
rule_id: PY-55
domain: performance
step: [implement, handle-errors, review]
applies_to: [python, exceptions]
triggers: ['\braise\s+StopIteration\b', '\bnext\(\s*[\w.]+(\([^()]*\))?\s*\)']
scope: file
check_kind: mechanical
severity_default: major
---

# A Python generator ends with return and never raises StopIteration or lets one escape from next, because since Python 3.7 that exception becomes a RuntimeError

## Thesis
A Python generator function ends with `return`, not by raising `StopIteration`, and each `next()` call in its body passes a default or sits in a `try` that handles `StopIteration`, because since Python 3.7 a `StopIteration` that directly or indirectly leaves generator code is converted into `RuntimeError` instead of ending the iteration.

## Rationale
`next(iterator)` returns the default when one is given and the iterator is exhausted; otherwise it raises `StopIteration`. If a `StopIteration` is about to bubble out of a generator frame, it is replaced with `RuntimeError`, which causes the `next()` call that invoked the generator to fail, passing that exception out; the `RuntimeError` retains the `StopIteration` as its cause. Python 3.7 enables these semantics everywhere. Raising `StopIteration` in a generator function therefore causes a `RuntimeError` when the generator is iterated over, and so does an unguarded `next()` on an exhausted iterator inside it: a `StopIteration` cannot be propagated from a generator. The alternatives are to give `next()` a default value, to catch the `StopIteration`, or to return directly.

## Example
```python
bad:  def skip_header(rows):
          next(rows)
          yield from rows
          raise StopIteration
good: def skip_header(rows):
          if next(rows, None) is None:
              return
          yield from rows
```

## Limits
The conversion applies to generator code only. An iterator's `__next__()` method raises `StopIteration` to signal that there are no further items, and a `next()` call or `raise StopIteration` in an ordinary function or in a class's `__next__()` method is outside the rule; a `StopIteration` raised there becomes a `RuntimeError` only when it propagates out through a generator that called it.

## Validator
Grep the file for `raise StopIteration` and for `next(` calls with a single argument. For each hit, find the enclosing function and check whether it is a generator function: its own body contains `yield` or `yield from`. For a `next()` call in a generator, check whether it sits inside a `try` whose `except` clause catches `StopIteration` or a parent class of it, and trace whether the iterator can be exhausted at that point. Validator question: **Does a generator function raise `StopIteration`, or call `next()` without a default outside a `try` that handles `StopIteration`?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-55`, severity major, `file`, `symbol`, `code` = the `raise StopIteration` statement or the `next()` call, `fix` = `return` in place of the raise, or `next(iterator, None)` followed by a `return` when the result is the default, `rationale` = since Python 3.7 a `StopIteration` that leaves a generator becomes `RuntimeError` instead of ending the iteration).

## Source
- PEP 479 §Proposal (raw.githubusercontent.com/python/peps/main/peps/pep-0479.rst) — 'If a ``StopIteration`` is about to bubble out of a generator frame, it is replaced with ``RuntimeError``, which causes the ``next()`` call (which invoked the generator) to fail, passing that exception out.' (fetched)
- PEP 479 §Transition plan (raw.githubusercontent.com/python/peps/main/peps/pep-0479.rst) — 'Python 3.7: Enable new semantics everywhere.' (fetched)
- CPython Doc/builtins/exceptions.rst §StopIteration (https://raw.githubusercontent.com/python/cpython/main/Doc/builtins/exceptions.rst) — 'If a generator code directly or indirectly raises :exc:`StopIteration`, it is converted into a :exc:`RuntimeError` (retaining the :exc:`StopIteration` as the new exception's cause).' (fetched)
- CPython Doc/builtins/exceptions.rst §StopIteration (https://raw.githubusercontent.com/python/cpython/main/Doc/builtins/exceptions.rst) — ':meth:`~iterator.__next__` method to signal that there are no further items produced by the iterator.' (fetched)
- CPython Doc/builtins/functions.rst §next (https://raw.githubusercontent.com/python/cpython/main/Doc/builtins/functions.rst) — 'If *default* is given, it is returned if the iterator is :term:`exhausted`, otherwise :exc:`StopIteration` is raised.' (fetched)
- Ruff PLR1708 stop-iteration-return (astral-sh/ruff crates/ruff_linter/src/rules/pylint/rules/stop_iteration_return.rs) — 'Raising `StopIteration` in a generator function causes a `RuntimeError` when the generator is iterated over. Instead of `raise StopIteration`, use `return` in generator functions.' (fetched)
- Pylint stop-iteration-return (R1708) (pylint-dev/pylint doc/data/messages/s/stop-iteration-return/details.rst) — 'It's possible to give a default value to ``next`` or catch the ``StopIteration``, or return directly. A ``StopIteration`` cannot be propagated from a generator.' (fetched)

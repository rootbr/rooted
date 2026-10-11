---
title: The first element of a Python iterable is taken with next over an iterator, not by building a list or tuple of the whole iterable and indexing or popping position 0
rule_id: PY-120
domain: performance
step: [implement, review]
applies_to: [python]
triggers: ['\b(list|tuple)\(.*\)\s*\[\s*0\s*\]', '\b(list|tuple)\(.*\)[.]pop\(\s*0\s*\)', '\bfor\b.*\]\s*\[\s*0\s*\]']
scope: hunk
check_kind: mechanical
severity_default: minor
---

# The first element of a Python iterable is taken with next over an iterator, not by building a list or tuple of the whole iterable and indexing or popping position 0

## Thesis
Python code that needs only the first element of an iterable takes it with next(iter(x)), or with next() directly on a generator or other iterator, rather than with list(x)[0], tuple(x)[0], list(i for i in x)[0], [i for i in x][0] or list(x).pop(0), and accounts for an empty x, where next raises StopIteration unless it is given a default.

## Rationale
Calling list() creates a new list of the entire collection, and the same is true of tuple() and of a list comprehension, which can be very expensive for large collections when only the first element is needed. next() retrieves the next item from an iterator by calling its __next__() method, so it fetches the first element lazily. The rewrite changes behaviour in two ways. The eager forms evaluate the entire collection while next(iter(x)) evaluates only the first element, so any side effects that occur during iteration are delayed. Indexing with [0] or calling pop() raises IndexError if the collection is empty, while next(iter(x)) raises StopIteration; if a default is given as next's second argument, it is returned when the iterator is exhausted.

## Example
```python
bad:  first = list(mapping.values())[0]
good: first = next(iter(mapping.values()), None)
```

## Limits
Code that relies on IndexError for an empty collection changes behaviour under the rewrite, so the fix passes next a default, tests for emptiness first, or moves the handler to StopIteration. Code that needs the side effects of iterating the whole collection builds the collection deliberately, since next(iter(x)) delays them. The rule reaches the five constructs above with the index or pop() position 0; a later position or a slice is out of reach.

## Validator
Grep the hunk for `list(...)[0]`, `tuple(...)[0]`, `[... for ... in ...][0]` and `list(...).pop(0)`. Check that the built list or tuple is used only for that one element and not kept elsewhere in the hunk. Read how the surrounding code meets an empty iterable — an IndexError handler, an emptiness check, or a guarantee that it is non-empty — and name it in the fix. Validator question: **Does the hunk build a list or tuple of a whole iterable only to read or pop its element at position 0?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-120`, severity minor, `file`, `symbol`, `code` = the expression ending in `[0]` or `.pop(0)`, verbatim from the diff, `fix` = `next(iter(x))`, or `next(<generator expression>)`, with a default such as `next(iter(x), None)` where x may be empty, in Python, `rationale` = the list or tuple copies the entire collection to read one element, while next fetches it lazily).

## Source
- Ruff RUF015 unnecessary-iterable-allocation-for-first-element (astral-sh/ruff crates/ruff_linter/src/rules/ruff/rules/unnecessary_iterable_allocation_for_first_element.rs) — 'Calling e.g. `list(...)` will create a new list of the entire collection, which can be very expensive for large collections. If you only need the first element of the collection, you can use `next(...)` or `next(iter(...)` to lazily fetch the first element. The same is true for the other constructs.' (fetched)
- Ruff RUF015 unnecessary-iterable-allocation-for-first-element (astral-sh/ruff crates/ruff_linter/src/rules/ruff/rules/unnecessary_iterable_allocation_for_first_element.rs) — 'all above-mentioned constructs will eagerly evaluate the entire collection, while `next(iter(...))` will only evaluate the first element. As such, any side effects that occur during iteration will be delayed.' (fetched)
- Ruff RUF015 unnecessary-iterable-allocation-for-first-element (astral-sh/ruff crates/ruff_linter/src/rules/ruff/rules/unnecessary_iterable_allocation_for_first_element.rs) — 'accessing members of a collection via square bracket notation `[0]` or the `pop()` function will raise `IndexError` if the collection is empty, while `next(iter(...))` will raise `StopIteration`.' (fetched)
- Python documentation library/functions.html §next (https://docs.python.org/3/library/functions.html#next) — 'Retrieve the next item from the iterator by calling its __next__() method. If default is given, it is returned if the iterator is exhausted, otherwise StopIteration is raised.' (fetched)
- Caveat: the ruff rule marks its fix unsafe for the two behaviour changes above.

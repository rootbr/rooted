---
title: A Python loop that needs both the position and the element of a sequence iterates enumerate and takes the element from its loop target
rule_id: PY-118
domain: performance
step: [implement, refactor, review]
applies_to: [python]
triggers: ['\bin\s+range\(\s*len\(', '^\s*for\s+\w+\s*,\s*\w+\s+in\s+enumerate\(', '^\s*\w+\s*\+=\s*1\s*(#.*)?$']
scope: hunk
check_kind: semantic
severity_default: minor
---

# A Python loop that needs both the position and the element of a sequence iterates enumerate and takes the element from its loop target

## Thesis
A Python for loop that uses each element of a sequence together with its position iterates enumerate(seq), with start= when the count begins at a number other than 0, and unpacks the position and the element, rather than iterating range(len(seq)) and reading seq[i], incrementing a counter variable by hand within the loop, or reading the element again as seq[i] inside an enumerate loop over seq.

## Rationale
The iterator that enumerate() returns yields, on each step, a tuple of a count, starting from start, which defaults to 0, and the value obtained from iterating the sequence, so the position index and the corresponding value are retrieved at the same time. A loop that iterates with range and len can be simplified by using the enumerate builtin. Against a counter variable incremented by hand within the loop, enumerate is more concise and idiomatic. Inside an enumerate loop the current item is already available alongside its index, so using the index to look up the item is unnecessary.

## Example
```python
bad:  for i in range(len(rows)):
          print(i, rows[i])
good: for i, row in enumerate(rows):
          print(i, row)
```

## Limits
With a start other than 0 the count no longer equals the element's index in seq, so a lookup of seq by the count reads another element and is out of reach. A counter that the body increments only on some iterations, behind an if or skipped by a continue, counts something other than the position and stays a counter. A loop that uses only the index and never the element has nothing to unpack and is out of reach.

## Validator
Grep the hunk for `in range(len(`, for `for <a>, <b> in enumerate(`, and for `<name> += 1` inside a for body. For range(len(seq)), check that the body reads seq[i] with the loop variable. For a counter, check that it is initialised to an integer before the loop, incremented once at the top level of the loop body, and that the loop has no continue. For an enumerate loop without start=, check whether the body reads the iterated sequence by the count. Validator question: **Does a for loop read each element of a sequence by its position — through range(len(seq)) and seq[i], a counter incremented once per iteration, or seq[i] inside an enumerate loop over seq with no start — where enumerate's unpacked target would supply the element?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-118`, severity minor, `file`, `symbol`, `code` = the `for` line and the `seq[i]` read or the `+= 1` line, verbatim from the diff, `fix` = `for i, item in enumerate(seq):`, with `start=` where the count begins elsewhere, and the body using `item`, in Python, `rationale` = enumerate yields the count and the element together, so indexing by range(len()) or a hand-kept counter re-implements the builtin).

## Source
- CPython Doc/tutorial/datastructures.rst §Looping Techniques (https://raw.githubusercontent.com/python/cpython/main/Doc/tutorial/datastructures.rst) — 'When looping through a sequence, the position index and corresponding value can be retrieved at the same time using the :func:`enumerate` function.' (fetched)
- Python documentation library/functions.html §enumerate (https://docs.python.org/3/library/functions.html#enumerate) — 'returns a tuple containing a count (from start which defaults to 0) and the values obtained from iterating over iterable.' (fetched)
- Pylint consider-using-enumerate (C0200) (pylint-dev/pylint doc/user_guide/checkers/features.rst) — 'Emitted when code that iterates with range and len is encountered. Such code can be simplified by using the enumerate builtin.' (fetched)
- Ruff SIM113 enumerate-for-loop (astral-sh/ruff crates/ruff_linter/src/rules/flake8_simplify/rules/enumerate_for_loop.rs) — 'Prefer the `enumerate` builtin over manually incrementing a counter variable within the loop, as `enumerate` is more concise and idiomatic.' (fetched)
- Ruff SIM113 enumerate-for-loop (astral-sh/ruff crates/ruff_linter/src/rules/flake8_simplify/rules/enumerate_for_loop.rs) — 'Checks for `for` loops with explicit loop-index variables that can be replaced with `enumerate()`.' (fetched)
- Ruff PLR1736 unnecessary-list-index-lookup (astral-sh/ruff crates/ruff_linter/src/rules/pylint/rules/unnecessary_list_index_lookup.rs) — 'When iterating over a list with `enumerate`, the current item is already available alongside its index. Using the index to look up the item is unnecessary.' (fetched)
- Pylint unnecessary-list-index-lookup (R1736) (pylint-dev/pylint doc/user_guide/checkers/features.rst) — 'Emitted when iterating over an enumeration and accessing the value by index lookup. The value can be accessed directly instead.' (fetched)

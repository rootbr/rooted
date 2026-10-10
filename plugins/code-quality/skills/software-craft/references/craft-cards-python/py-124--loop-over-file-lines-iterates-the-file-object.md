---
title: A loop over the lines of a Python file iterates the file object itself, not the list of every line that readlines() returns
rule_id: PY-124
domain: code
step: [implement, review]
applies_to: [python]
triggers: ['\bfor\b.*\bin\s+.*[.]readlines\(\s*\)', '[.]readlines\(\s*\)\s*:\s*$']
scope: hunk
check_kind: mechanical
severity_default: minor
---

# A loop over the lines of a Python file iterates the file object itself, not the list of every line that readlines() returns

## Thesis
A Python `for` loop or comprehension that walks an open file line by line iterates the file object, `for line in f`, not the list that a `f.readlines()` call without a hint returns.

## Rationale
`io.IOBase` and its subclasses support the iterator protocol: iterating a file object yields the lines of the stream, bytes for a binary stream and character strings for a text stream. `readlines()` reads and returns a list of lines from the stream, so the loop begins only after every line of the file is held in that list. Iterating the file object reaches the lines without calling `readlines()`, and looping over the file object is memory efficient, fast and leads to simple code.

## Example
```python
bad:  with open(path, encoding="utf-8") as fp:
          for line in fp.readlines():
              handle(line)
good: with open(path, encoding="utf-8") as fp:
          for line in fp:
              handle(line)
```

## Limits
Code that needs all the lines of a file in a list, for indexing or `len`, builds that list on purpose, with `list(f)` or `f.readlines()`. A call with a hint, `f.readlines(hint)`, reads no more lines once the total size of the lines read so far exceeds `hint`, and is outside the rule; a hint of `0` or less, or `None`, counts as no hint. The rule reaches file objects iterated line by line, and a `readlines` method of another class is outside it.

## Validator
Grep the hunk for `.readlines()` as the iterable of a `for` statement or a comprehension. Trace the receiver within the hunk to `open(...)`, `Path.open(...)` or another file object, and check that the loop iterates the list directly or through a call that takes any iterable, such as `enumerate`, rather than one that needs a sequence, such as `reversed`. Validator question: **Does a `for` loop or comprehension iterate the result of `readlines()`, called with no hint, on a file object whose lines it only walks once?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-124`, severity minor, `file`, `symbol`, `code` = the loop header with `.readlines()`, verbatim, `fix` = the same header over the file object, such as `for line in fp:`, `rationale` = `readlines()` reads every line into a list before the loop starts, while the file object yields the lines itself).

---
title: A Python with statement never follows an item bound with as by a further item that is not a call and has no as of its own
rule_id: PY-173
domain: errors
step: [implement, review]
applies_to: [python]
triggers: ['^\s*(async\s+)?with\s.*\bas\s+\w+\s*,\s*[A-Za-z_][\w.]*\s*[:,)]', '^\s*(async\s+)?with\s*\(\s*$']
scope: hunk
check_kind: mechanical
severity_default: minor
---

# A Python with statement never follows an item bound with as by a further item that is not a call and has no as of its own

## Thesis
In a Python `with` statement, every item that follows an item bound with `as` to a name is a call or carries its own `as`; a further context manager written as a bare name, attribute or other non-call expression goes into a nested `with` statement.

## Rationale
Each item of a `with` statement is an expression with an optional `as` target, and with more than one item the context managers are processed as if multiple `with` statements were nested; the return value of `__enter__` is assigned only when a target is included. So `with ctx() as a, b:` enters `b` as a second context manager and binds its `__enter__` result to nothing, while the line also reads as `ctx()` returning a tuple bound to `a` and `b`: a reader cannot tell whether the context manager returns a tuple or the item without a name binding is another context manager. A nested `with` statement for the second manager states which reading is meant.

## Example
```python
bad:  with open(src) as fh1, fh2:
          copy(fh1, fh2)
good: with open(src) as fh1:
          with open(dst, "w") as fh2:
              copy(fh1, fh2)
```

## Limits
A further item that is a call is outside the rule, because a call has no way to be mistaken for a name assignment: `with ctx() as a, lock_for(a):` conforms. An item without `as` that comes before every bound item, as in `with lock, open(path) as fh:`, follows no `as` binding and is outside the rule as well. A parenthesized multi-line `with` statement follows the same rule item by item.

## Validator
Grep the hunk for a `with` or `async with` statement, including a parenthesized item list spread over several lines, in which `as name,` is followed by an item that has no `as` of its own and no call parentheses. Open the statement and resolve that item: is it a context manager entered on purpose, or a name meant to receive part of the first manager's value? Validator question: **Does an item bound with `as` to a name precede, in the same `with` statement, an item that is not a call and has no `as` of its own?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-173`, severity minor, `file`, `symbol`, `code` = the `with` line, `fix` = the second manager in a nested `with` statement with its own `as`, `rationale` = the bare item is entered as a second context manager whose `__enter__` result is not bound, while the line reads as a tuple bound to two names).

## Source
- Pylint confusing-with-statement (W0124) (pylint-dev/pylint pylint/checkers/base/basic_checker.py) — 'Following "as" with another context manager looks like a tuple.' (fetched)
- Pylint confusing-with-statement (W0124) (pylint-dev/pylint pylint/checkers/base/basic_checker.py) — 'Emitted when a `with` statement component returns multiple values and uses name binding with `as` only for a part of those values, as in with ctx() as a, b. This can be misleading' (fetched)
- Pylint confusing-with-statement (W0124) (pylint-dev/pylint pylint/checkers/base/basic_checker.py) — 'clear if the context manager returns a tuple or if the node without a name binding is another context manager.' (fetched)
- Pylint confusing-with-statement (W0124) (pylint-dev/pylint doc/data/messages/c/confusing-with-statement/bad.py) — 'with open("file.txt", "w") as fh1, fh2:  # [confusing-with-statement]' (fetched)
- Pylint confusing-with-statement (W0124) (pylint-dev/pylint doc/data/messages/c/confusing-with-statement/good.py) — '    with open("file.txt", "w", encoding="utf8") as fh2:' (fetched)
- CPython Doc/reference/compound_stmts.rst §The with statement (https://raw.githubusercontent.com/python/cpython/main/Doc/reference/compound_stmts.rst) — 'with_item: `expression` ["as" `target`]' (fetched)
- CPython Doc/reference/compound_stmts.rst §The with statement (https://raw.githubusercontent.com/python/cpython/main/Doc/reference/compound_stmts.rst) — 'If a target was included in the :keyword:`with` statement, the return value from :meth:`~object.__enter__` is assigned to it.' (fetched)
- CPython Doc/reference/compound_stmts.rst §The with statement (https://raw.githubusercontent.com/python/cpython/main/Doc/reference/compound_stmts.rst) — 'With more than one item, the context managers are processed as if multiple :keyword:`with` statements were nested' (fetched)
- CPython Doc/reference/compound_stmts.rst §The with statement (https://raw.githubusercontent.com/python/cpython/main/Doc/reference/compound_stmts.rst) — 'You can also write multi-item context managers in multiple lines if the items are surrounded by parentheses.' (fetched)
- Caveat: the checker (`BasicChecker.visit_with` in pylint/checkers/base/basic_checker.py) reports a pair of items only when the earlier one is bound with `as` to a plain name and the later one has no `as` and is not a call, with the code comment that a function call has no way to be mistaken for a name assignment.

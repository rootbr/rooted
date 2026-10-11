---
title: The expression after the comma of a Python assert is a message string, never a number or other non-string literal meant as the expected value
rule_id: PY-151
domain: code
step: [test, review]
applies_to: [python, tests]
triggers: ['^\s*assert\b[^#]*,\s*(-?\d|True\b|False\b|None\b|[.][.][.]|[bB][rR]?[\x22\x27])']
scope: hunk
check_kind: mechanical
severity_default: major
---

# The expression after the comma of a Python assert is a message string, never a number or other non-string literal meant as the expected value

## Thesis
In a Python `assert expression1, expression2` statement the expression after the comma is a string message, and a non-string literal there, a number, a bytes literal, `True`, `False`, `None` or `...`, is written instead as the comparison it was likely meant to be, `assert len(rows) == 3`, with a string after the comma where a message is wanted.

## Rationale
The extended form `assert expression1, expression2` is equivalent to `if __debug__: if not expression1: raise AssertionError(expression2)`, so only the first expression is tested and the second is the argument of the AssertionError raised when that test fails. `assert len(rows), 3` is therefore true unless `rows` is empty, and it passes whatever the length of a non-empty `rows` is. A literal constant can be a string, bytes, an int, a float, a complex number, a bool, `None` or `Ellipsis`, and a non-string one in the message position was likely intended to be used in a comparison assertion rather than as a message; written as `assert len(rows) == 3`, the assertion tests the value it names.

## Example
```python
bad:  rows = load_rows(path)
      assert len(rows), 3
good: rows = load_rows(path)
      assert len(rows) == 3, "expected three rows"
```

## Limits
The rule reaches the second expression only when it is a non-string literal: a string or f-string message, a name, an attribute access or a call there is outside it, whatever value it yields at run time.

## Validator
Grep the hunk for `assert` statements and find the comma that separates the tested expression from the message, skipping commas inside parentheses, brackets, braces and calls of the tested expression. Read the expression after that comma and tell whether it is a number literal, a bytes literal (`b"..."`), `True`, `False`, `None` or `...`; a string, an f-string, a name or a call is not. Validator question: **Is the expression after the separating comma of an assert statement in the hunk a non-string literal, that is a number, a bytes literal, `True`, `False`, `None` or `...`?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-151`, severity major, `file`, `symbol`, `code` = the assert statement verbatim from the diff, `fix` = the literal moved into a comparison before the comma with a string message after it, `assert len(rows) == 3, "expected three rows"`, or only a string message where the comparison already stands before the comma, `rationale` = names that the expression after the comma is only the AssertionError argument, so the assert tests just the truth of the first expression).

## Source
- CPython Doc/reference/simple_stmts.rst §The assert statement (https://raw.githubusercontent.com/python/cpython/main/Doc/reference/simple_stmts.rst) — 'The extended form, ``assert expression1, expression2``, is equivalent to :: if __debug__: if not expression1: raise AssertionError(expression2)' (fetched)
- Ruff RUF040 invalid-assert-message-literal-argument (astral-sh/ruff crates/ruff_linter/src/rules/ruff/rules/invalid_assert_message_literal_argument.rs) — 'An assert message which is a non-string literal was likely intended to be used in a comparison assertion, rather than as a message.'; 'assert len(fruits), 2  # True unless the list is empty' (fetched)
- CPython Doc/library/ast.rst §Literals (https://raw.githubusercontent.com/python/cpython/main/Doc/library/ast.rst) — 'The values represented can be instances of :class:`str`, :class:`bytes`, :class:`int`, :class:`float`, :class:`complex`, and :class:`bool`, and the constants :data:`None` and :data:`Ellipsis`.' (fetched)

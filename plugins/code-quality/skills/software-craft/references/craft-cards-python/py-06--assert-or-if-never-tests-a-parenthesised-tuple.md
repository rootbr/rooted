---
title: A Python assert or if never tests a parenthesised non-empty tuple, so an assert writes its condition and message without enclosing parentheses
rule_id: PY-06
domain: code
step: [implement, test, review]
applies_to: [python]
triggers: ['^\s*assert\s*\(.*,.*\)\s*(#.*)?$', '^\s*(el)?if\s*\(.*,.*\)\s*:', '^\s*while\s*\(.*,.*\)\s*:']
scope: hunk
check_kind: mechanical
severity_default: major
---

# A Python assert or if never tests a parenthesised non-empty tuple, so an assert writes its condition and message without enclosing parentheses

## Thesis
The test of a Python assert, if, elif or while statement is never a parenthesised tuple with one or more elements: an assert writes its condition and its message as `assert condition, message`, with no parentheses enclosing both, and a check of several values tests each value separately, joined with `and` or in separate asserts.

## Rationale
assert is a statement that takes no parentheses around its parameters: its extended form `assert expression1, expression2` is equivalent to `if __debug__: if not expression1: raise AssertionError(expression2)`, so the comma separates the condition from the message. Parentheses around both parts build one tuple instead, and when expressions are used by control flow statements Python interprets as false only the constants `None` and `False`, numeric zero of all types and empty strings and containers, tuples included; all other values are interpreted as true. A non-empty tuple is therefore always true: `assert (x, y)` tests whether the tuple `(x, y)` is true, which is always the case, so the assert always passes, and an if whose test is a non-empty tuple always passes too, so its branch always runs. Removing the parentheses restores a condition that can fail and a message that is raised only when it does.

## Example
```python
bad:  assert (user.is_active, "user must be active")
      if (count > 0, limit > 0):
          process(items)
good: assert user.is_active, "user must be active"
      if count > 0 and limit > 0:
          process(items)
```

## Limits
The rule reaches only a test that is itself a tuple, with a comma at the top level of the parentheses, such as `assert (x, y)`, `assert (x,)` or `if (a, b):`. A test that holds a tuple inside a larger expression, such as `assert (x, y) == expected` or `if (row, col) in seen:`, is a comparison or a membership test and is outside the rule. Parentheses around the condition alone or around the message alone, as in `assert (a > b), ("message")`, keep the comma outside any parentheses and are correct.

## Validator
Grep the hunk for `assert (`, `if (`, `elif (` and `while (` lines. For each hit, take the parenthesised group that opens right after the keyword and check that it is the whole test — for an assert it closes at the end of the statement or right before the comma that starts the message, for if, elif or while it closes right before the colon — and that it holds a comma at its own top level, not inside a call, a subscript, nested parentheses or a string. Validator question: **Is the whole test of an assert, if, elif or while statement a parenthesised tuple with at least one element?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-06`, severity major, `file`, `symbol`, `code` = the assert, if, elif or while line with its parenthesised tuple, verbatim, `fix` = the statement with the enclosing parentheses removed, such as `assert user.is_active, "user must be active"`, or the values joined with `and`, such as `if count > 0 and limit > 0:`, `rationale` = that a non-empty tuple is always true, so the assert can never fail or the branch always runs).

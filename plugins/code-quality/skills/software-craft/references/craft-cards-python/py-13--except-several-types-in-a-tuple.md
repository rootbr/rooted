---
title: A Python except clause that catches several exception types names them in a tuple and never joins them with or or and
rule_id: PY-13
domain: errors
step: [handle-errors, review]
applies_to: [python, exceptions]
triggers: ['^\s*except\*?\s*\(?\s*[\w.]+\s+(or|and)\s+[\w.]+', '^\s*except\*?\b[^:]*\s(or|and)\s']
scope: hunk
check_kind: mechanical
severity_default: major
---

# A Python except clause that catches several exception types names them in a tuple and never joins them with or or and

## Thesis
An `except` clause that handles several exception types lists them in a tuple, `except (ValueError, TypeError):`, and does not join the classes with `or` or `and`.

## Rationale
Python evaluates the expression of an `except` clause first, and that expression must evaluate to an exception type or a tuple of exception types. A boolean expression of exception classes evaluates to a single exception class, for `or` typically the first one in the list, so the handler catches only one kind of exception; an exception of another named type finds no matching clause there, and the search for a handler continues in the surrounding code and on the invocation stack. That outcome is almost never the desired behavior.

## Example
```python
bad:  try:
          count = int(raw)
      except ValueError or TypeError:
          count = 0
good: try:
          count = int(raw)
      except (ValueError, TypeError):
          count = 0
```

## Limits
The rule reaches the expression of an `except` or `except*` clause. A name bound to a tuple of exception classes is the tuple form and is correct. From Python 3.14 the grouping parentheses can be dropped when several exception types are listed and the clause has no `as` target; `except ValueError, TypeError:` is then a list of types, not a boolean expression.

## Validator
Grep the hunk for an `except` or `except*` header whose expression contains `or` or `and`. Open the header and confirm that the operands are exception classes or names bound to them. Validator question: **Does an except clause join exception classes with `or` or `and` instead of listing them in a tuple?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-13`, severity major, `file`, `symbol`, `code` = the `except` header quoted verbatim from the diff, `fix` = the same classes listed in a tuple, such as `except (ValueError, TypeError):`, `rationale` = the boolean expression evaluates to a single class, typically the first for `or`, so the handler catches only one of the types it names).

---
title: Python string or bytes literals never stand adjacent on one line, and an element of a list, tuple or set literal built from adjacent literals is wrapped in its own parentheses
rule_id: PY-31
domain: code
step: [implement, review]
applies_to: [python]
triggers: ['["\x27]\s+[rRbBfFuU]{0,2}["\x27]', '^\s+[rRbBfFuU]{0,2}["\x27][^"\x27]*["\x27]\s*$']
scope: hunk
check_kind: mechanical
severity_default: major
---

# Python string or bytes literals never stand adjacent on one line, and an element of a list, tuple or set literal built from adjacent literals is wrapped in its own parentheses

## Thesis
In Python code no two string or bytes literals stand next to each other on one line, and an implicit concatenation meant as one element of a list, tuple or set literal is wrapped in its own parentheses.

## Rationale
Python gives multiple adjacent string or bytes literals, possibly using different quoting conventions, the meaning of their concatenation; the feature is defined at the syntactical level and the literals are joined at compile time. A comma missing between two literal elements is therefore no error: in a list, tuple or set literal, implicit concatenation is often the result of a missing comma between elements, which can silently merge items together. Two literals on the same line might also indicate a forgotten comma, as in a `return` meant to build a tuple, where parentheses are not mandatory and only the comma makes the tuple. A single-line concatenation may also be unintentional, because code formatters are capable of introducing one when they collapse long lines. Wrapping an intentional concatenation inside a collection literal in its own parentheses makes it explicit.

## Example
```python
bad:  def pair():
          return "item1" "item2"
      names = ["alpha", "beta" "gamma"]
good: def pair():
          return "item1", "item2"
      names = ["alpha", "beta", "gamma"]
      notes = ["short", ("a long note split "
                         "over two lines")]
```

## Limits
Outside a collection literal, a long string split into literals on consecutive lines inside parentheses stays allowed: strings visibly split to avoid long lines of code are exempt when the first string ends with a space, punctuation or a newline escape, and detection of concatenation over line jumps is left disabled by default, since enabling it gives false positives for string parameters passed on multiple lines in function calls. A pair whose quotes differ, used to avoid escaping quotes, and a pair whose prefixes differ (f, r, u or none) are outside the rule: each gives a visible reason for the concatenation.

## Validator
Grep the hunk for a string or bytes literal followed, after whitespace only, by another literal on the same line, and for a line inside a list, tuple or set display that holds a lone literal with no trailing comma. Open the enclosing statement: for a same-line pair, confirm both operands are literals with the same quotes and prefix and no comma or operator between them; for a collection element, confirm the adjacent literals form one element and are not wrapped in parentheses of their own. Validator question: **Does the hunk place two string or bytes literals adjacent on one line, or build a list, tuple or set element from adjacent literals without parentheses of its own?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-31`, severity major, `file`, `symbol`, `code` = the adjacent literals as written in the diff, `fix` = the missing comma restored, or the intended concatenation merged into one literal or wrapped in its own parentheses across lines, in Python, `rationale` = Python joins adjacent string or bytes literals at compile time, so a missing comma silently merges two items into one).

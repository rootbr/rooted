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

## Source
- CPython Doc/reference/expressions.rst §String literal concatenation (python/cpython Doc/reference/expressions.rst) — "Multiple adjacent string or bytes literals, possibly using different quoting conventions, are allowed, and their meaning is the same as their concatenation"; "This feature is defined at the syntactical level, so it only works with literals." (fetched)
- Ruff ISC004 implicit-string-concatenation-in-collection-literal (astral-sh/ruff crates/ruff_linter/src/rules/flake8_implicit_str_concat/rules/collection_literal.rs) — "In collection literals, implicit string concatenation is often the result of a missing comma between elements, which can silently merge items together."; "If the concatenation is intentional, wrap it in parentheses to make it explicit" (fetched)
- Ruff ISC001 single-line-implicit-string-concatenation (astral-sh/ruff crates/ruff_linter/src/rules/flake8_implicit_str_concat/rules/implicit.rs) — "the implicit concatenation may also be unintentional, as code formatters are capable of introducing single-line implicit concatenations when collapsing long lines." (fetched)
- SonarSource python S5799 (SonarSource/sonar-python python-checks/src/main/resources/org/sonar/l10n/py/rules/python/S5799.html) — "Python concatenates adjacent string or byte literals at compile time."; "In the following contexts it might indicate that a comma was forgotten"; "when the two strings are on the same line."; "parentheses are not mandatory to create a tuple, only the comma is"; "when the strings are in a list, a set or a tuple."; "when the quotes used for both strings are different. This can be used to avoid escaping quotes."; "when the strings or bytes have different prefixes"; "when strings are visibly split to avoid long lines of code, i.e. when the first string ends with a space, punctuation or" (fetched)
- Pylint implicit-str-concat (W1404) (pylint-dev/pylint doc/data/messages/i/implicit-str-concat/details.rst) — "By default, detection of implicit string concatenation of line jumps is disabled."; "it will trigger false positive for string parameters passed on multiple lines in function calls" (fetched)

---
title: A Python assignment or return meant to hold one value ends without a trailing comma, and a tuple that is meant is written in parentheses
rule_id: PY-146
domain: code
step: [implement, review]
applies_to: [python]
triggers: ['^\s*[\w.\[\]\x27\x22]+ = [^=].*[)\]}\w\x27\x22],\s*(#.*)?$', '^\s*return\b.*[)\]}\w\x27\x22],\s*(#.*)?$']
scope: hunk
check_kind: mechanical
severity_default: major
---

# A Python assignment or return meant to hold one value ends without a trailing comma, and a tuple that is meant is written in parentheses

## Thesis
A Python assignment or return whose right-hand side is meant as one value ends without a comma outside brackets, because a trailing comma after a single expression makes the value a one-element tuple. Where a one-element tuple is meant, it is written with explicit parentheses, `(value,)`.

## Rationale
In Python it is the comma, not the parentheses, that makes a tuple: except as part of a list or set display, an expression list containing at least one comma yields a tuple, and a trailing comma is required only to create a one-item tuple such as `1,`, while a single expression without a trailing comma yields the value of that expression. A stray comma at the end of a line, as in `timeout = settings.get("timeout"),`, therefore binds a one-element tuple holding the value, not the value itself, and a misplaced trailing comma of this kind can lead to bugs wherever the tuple is then used as the value. Writing every tuple with explicit parentheses keeps an intended one-element tuple apart from a stray comma.

## Example
```python
bad:  timeout = settings.get("timeout"),
good: timeout = settings.get("timeout")
      names = (user.name,)
```

## Limits
A comma inside brackets is outside the rule: within a list or set display the comma does not make the display a tuple, and in a tuple of two or more items a trailing comma is optional. An expression list of several comma-separated expressions, such as `a, b = b, a`, yields a tuple whose length is the number of expressions, on purpose; the rule concerns the comma after a single expression.

## Validator
Grep the added lines for an assignment, an augmented assignment or a return whose line ends in a comma before any comment. Open the statement and count brackets from its start: the comma counts only at bracket depth zero, after a single expression, with the statement not continued on the next line. Check how the bound name or the returned value is used afterwards, to tell a stray comma, whose fix removes it, from an intended tuple, whose fix adds parentheses. Validator question: **Does an assignment or return in the hunk end in a comma at bracket depth zero after a single expression?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-146`, severity major, `file`, `symbol`, `code` = the statement with its trailing comma, quoted verbatim from the diff, `fix` = the statement without the comma, such as `timeout = settings.get("timeout")`, or with explicit parentheses, `(value,)`, where a tuple is meant, `rationale` = the one-element tuple the comma creates and the place where the code uses it as one value).

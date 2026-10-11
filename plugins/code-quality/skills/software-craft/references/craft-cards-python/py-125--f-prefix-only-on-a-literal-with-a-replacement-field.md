---
title: A Python string literal carries the f prefix only when it holds at least one replacement field
rule_id: PY-125
domain: code
step: [implement, review]
applies_to: [python]
triggers: ['(?<![\w])[fF][rR]?(?:"""[^{}]*?"""|"(?!"")[^"{}]*")', '(?<![\w])[fF][rR]?(?:\x27\x27\x27[^{}]*?\x27\x27\x27|\x27(?!\x27\x27)[^\x27{}]*\x27)', '(?<![\w])[rR][fF]["\x27][^"\x27{}]*["\x27]']
scope: hunk
check_kind: mechanical
severity_default: minor
---

# A Python string literal carries the f prefix only when it holds at least one replacement field

## Thesis
A Python string literal carries the `f` prefix only when it holds at least one `{expression}` replacement field; an implicit concatenation in which at least one f-string segment holds a field meets the rule as a whole.

## Rationale
Replacement fields are delimited by curly braces and contain expressions evaluated at run time; a literal without one has no placeholder expression to format, so the f-string is not necessary and a regular string serves instead. Doubled curly braces `{{` and `}}` outside a replacement field are replaced with a single brace, so they are no field. An f-string without any placeholder can confuse readers, who may expect a placeholder to be present, and it can also indicate that the author forgot to add one, as in `f"x + y = x + y"` where `f"{x} + {y} = {x + y}"` was meant. The finding therefore asks whether a field is missing before the prefix is dropped.

## Example
```python
bad:  banner = f"Connection established"
      print(f"x + y = x + y")
good: banner = "Connection established"
      print(f"{x} + {y} = {x + y}")
```

## Limits
In an implicit concatenation, an f-string segment without a field beside an f-string segment that holds one is outside the rule.

## Validator
Grep the hunk for a string literal with an `f` or `F` prefix, alone or combined with `r` or `R`, whose text holds no single `{`. When it is one segment of an implicit concatenation, check the other f-string segments for a field. Read the literal's text against the names bound nearby: words that spell out names or expressions in scope, such as `x + y = x + y` beside bound `x` and `y`, mark forgotten fields, and the fix writes them. Validator question: **Does an f-prefixed literal hold no replacement field, with no f-string segment of its implicit concatenation holding one either?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-125`, severity minor, `file`, `symbol`, `code` = the f-prefixed literal, verbatim, `fix` = the literal without the `f` prefix, or, where its text names values in scope, the literal with those replacement fields written, `rationale` = an f-string with no field formats nothing and may mark a placeholder the author forgot).

## Source
- Ruff F541 f-string-missing-placeholders (astral-sh/ruff crates/ruff_linter/src/rules/pyflakes/rules/f_string_missing_placeholders.rs) — 'they are not necessary if there are no placeholder expressions to format.' and 'an f-string without placeholders can be confusing for readers, who may expect such a placeholder to be present.' and 'An f-string without any placeholders could also indicate that the author forgot to add a placeholder expression.' and 'this rule only flags f-strings that are part of an implicit concatenation if _none_ of the f-string segments contain placeholder expressions.' (fetched)
- Pylint f-string-without-interpolation (W1309) (pylint-dev/pylint doc/data/messages/f/f-string-without-interpolation/bad.py) — 'print(f"x + y = x + y")  # [f-string-without-interpolation]' (fetched)
- Pylint f-string-without-interpolation (W1309) (pylint-dev/pylint doc/data/messages/f/f-string-without-interpolation/good.py) — 'print(f"{x} + {y} = {x + y}")' (fetched)
- CPython Doc/reference/lexical_analysis.rst §f-strings (https://raw.githubusercontent.com/python/cpython/main/Doc/reference/lexical_analysis.rst) — 'They may contain *replacement fields* delimited by curly braces ``{}``.' and 'Replacement fields contain expressions which are evaluated at run time.' and 'Any doubled curly braces (``{{`` or ``}}``) outside replacement fields' (fetched)

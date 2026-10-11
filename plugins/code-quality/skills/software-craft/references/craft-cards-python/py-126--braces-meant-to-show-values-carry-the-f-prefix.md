---
title: A Python string literal whose braces name values in scope and are meant to show them carries the f prefix, since a plain literal keeps the braces as text without any error
rule_id: PY-126
domain: code
step: [implement, review]
applies_to: [python]
triggers: ['(?<![\w])"[^"]*\{[A-Za-z_][\w.]*(?:\[[^\]]*\])?(?:![rsa])?(?::[^{}"]*)?\}[^"]*"', '(?<![\w])\x27[^\x27]*\{[A-Za-z_][\w.]*(?:\[[^\]]*\])?(?:![rsa])?(?::[^{}\x27]*)?\}[^\x27]*\x27']
scope: file
check_kind: semantic
severity_default: major
---

# A Python string literal whose braces name values in scope and are meant to show them carries the f prefix, since a plain literal keeps the braces as text without any error

## Thesis
A Python string literal that holds `{name}` fields naming variables or expressions in scope, and is meant to show their values, carries the `f` prefix. A literal that is a template by design stays plain: a standalone string expression such as a docstring, a string with a direct method call on it such as `"{value}".format(...)`, a string in a call with argument names that match at least one of its names, and a string in a call known to expect a template, such as a `logging` or `gettext` call.

## Rationale
Replacement fields contain expressions evaluated at run time, and expressions inside curly braces are evaluated only when the string has the `f` prefix. A plain literal holding `{name}` is an ordinary, valid string — many string literals contain f-string-like syntax without being meant as f-strings — so the braces and the name between them reach the output as text. Adding the prefix always changes the behaviour of the program, so the finding rests on intent: the literal is meant to show the values of names in scope, not to serve as a template.

## Example
```python
bad:  name, order = customer.name, customer.order
      print("Hello {name}! Your order {order.id} ships today")
good: name, order = customer.name, customer.order
      print(f"Hello {name}! Your order {order.id} ships today")
```

## Limits
A call known to expect a template string rather than an evaluated f-string receives the braces as its template, so an `f` prefix there changes what it receives. A literal with no `{...}` section, with invalid f-string syntax, with names that are not in scope or no captured variable at all, or with an invalid format specifier is outside the rule.

## Validator
Grep the hunk for a string literal without an `f` prefix that holds a `{name}`, `{obj.attr}` or `{name[key]}` section. Open the file and, at the literal's position, check that each name in the braces is bound in scope. Check the literal's role: a standalone expression, the receiver of a direct method call such as `.format`, an argument of a call whose argument names match a name in its braces, or an argument of a `logging` call, of a project logger object (Ruff's `lint.logger-objects` key lists them where configured) or of a `gettext` call is a template; trace a literal stored under a name to its uses, and treat it as a template when a later `.format`, logging or `gettext` call fills it. Validator question: **Does a plain literal hold brace sections that name values in scope, outside every template use, where the code means to show those values?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-126`, severity major, `file`, `symbol`, `code` = the literal with the call or assignment that holds it, verbatim, `fix` = the same literal with the `f` prefix, `rationale` = the braces name values in scope that the code means to show, and without the prefix they reach the output as text).

## Source
- Ruff RUF027 missing-f-string-syntax (astral-sh/ruff crates/ruff_linter/src/rules/ruff/rules/missing_fstring_syntax.rs) — 'Expressions inside curly braces are only evaluated if the string has an `f` prefix.' and 'There are many possible string literals which are not meant to be f-strings' and 'The string is a standalone expression. For example, the rule ignores all docstrings.' and 'has a direct method call on it' and 'The string is part of a function call with argument names that match at least one variable' and 'The string has no `{...}` expression sections, or uses invalid f-string syntax.' and "The string references variables that are not in scope, or it doesn't capture variables at all." and 'Any format specifiers in the potential f-string are invalid.' and 'known to expect a template string rather than an' and 'This fix will always change the behavior of the program' (fetched); the rule is in preview.
- CPython Doc/reference/lexical_analysis.rst §f-strings (https://raw.githubusercontent.com/python/cpython/main/Doc/reference/lexical_analysis.rst) — 'Replacement fields contain expressions which are evaluated at run time.' (fetched)

---
title: The % operator is never applied to a Python f-string, because % then treats the already interpolated text as a printf-style template
rule_id: PY-129
domain: code
step: [implement, review]
applies_to: [python]
triggers: ['(?<![\w])[rR]?[fF][rR]?"[^"]*"\s*%(?!=)', '(?<![\w])[rR]?[fF][rR]?''[^'']*''\s*%(?!=)', '(?<![\w])[rR]?[fF][rR]?("""|'''''').*\1\s*%(?!=)']
scope: hunk
check_kind: mechanical
severity_default: major
---

# The % operator is never applied to a Python f-string, because % then treats the already interpolated text as a printf-style template

## Thesis
An f-string carries its values in its own replacement fields and is never the left operand of the `%` operator; a value meant for a `%` conversion goes into a replacement field of the same f-string, or the whole string is written as one `%` template.

## Rationale
An f-string has no constant value: its replacement fields are expressions evaluated at run time, and the `%` operator then receives the finished text, interpolated values included, as its format. `%` replaces every `%` conversion specification in that format with elements of the right operand, so a `%` that an interpolated value carries into the text is read as the start of a conversion specification. Unless the format requires a single argument, the right operand must be a tuple with exactly the number of items the format specifies, or a single mapping, so the operand that matched the author's template no longer matches a text whose interpolated values add specifications. F-strings already interpolate through `{...}` expressions and serve the same purpose as `%`-formatting, so applying `%` to an f-string is almost certainly a mistake, and it typically indicates that the author intended either an f-string or `%`-formatting, not both.

## Example
```python
bad:  message = f"{user} has %d items" % count
good: message = f"{user} has {count} items"
```

## Limits
A `%` inside a replacement field, as in `f"{total % size}"`, is the modulo operator on the field's values, and a plain string literal used as the template, as in `"%s has %d items" % (user, count)`, uses one mechanism; both are outside the rule. An f-string bound to a name and later used as the left operand of `%` is the same combination, in reach when the hunk shows both the binding and the `%`.

## Validator
Grep the hunk for an f-string literal, with an `f`, `F`, `rf` or `fr` prefix in any quote style, followed by the `%` operator rather than `%=`, and for a name bound to an f-string that later stands left of `%`. Confirm that the f-string itself is the left operand, not an expression inside one of its replacement fields. Validator question: **Is an f-string, written in place or bound to a name in the hunk, the left operand of the `%` operator?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-129`, severity major, `file`, `symbol`, `code` = the f-string and the `%` expression it starts, `fix` = one f-string with each `%` operand moved into a replacement field, such as `f"{user} has {count} items"`, `rationale` = `%` reads the interpolated text as its format, so a `%` in an interpolated value starts a conversion specification and the right operand must match the specifications the text then holds).

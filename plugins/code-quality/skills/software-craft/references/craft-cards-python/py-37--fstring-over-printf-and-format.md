---
title: A Python string literal formatted in place with values is an f-string rather than % formatting or str.format, except the template of a logging call
rule_id: PY-37
domain: code
step: [implement, refactor, review]
applies_to: [python]
triggers: ['[\x22\x27]\s*%\s*[\w(]', '[\x22\x27][.]format\(']
scope: hunk
check_kind: mechanical
severity_default: minor
---

# A Python string literal formatted in place with values is an f-string rather than % formatting or str.format, except the template of a logging call

## Thesis
A str literal formatted with values where it is written carries those values in an f-string, where an f-string can replace the % operator or the str.format call; the template of a logging call keeps its %-placeholders and receives the values as the call's further arguments.

## Rationale
Python offers printf-style % formatting, str.format and f-strings for putting values into a string. printf-style formatting has a number of quirks and leads to less readable code than str.format calls or f-strings, and f-strings are more readable and generally preferred over str.format calls; their concise, consistent syntax can replace most use cases of the % operator, str.format() and string.Template. One quirk: with a single generic specifier such as %s, a value and the one-element tuple holding it resolve to the same string under % formatting, but differently under str.format and f-strings. A logging call is the exception: passing the arguments to the logger, as logging.debug("msg %s", arg) does, lets the logger skip formatting entirely when the record is filtered out by level, which matters when the arguments have an expensive __str__ or __repr__.

## Example
```python
bad:  greeting = "Hello, %s! You have %d new messages" % (name, count)
      notice = "Sent {} messages".format(count)
good: greeting = f"Hello, {name}! You have {count} new messages"
      notice = f"Sent {count} messages"
      logger.info("Sent %d messages", count)
```

## Limits
f-strings replace most uses of the other two forms, and the rule covers the str.format calls and % expressions that an f-string can replace: a template stored or passed apart from its values, such as a module constant formatted elsewhere, is not a literal formatted in place and stays outside the rule, and so does a bytes literal formatted with %. With a single generic specifier such as %s and a right-hand side that may be a tuple, a mechanical rewrite is not safe, because "%s" % val gives the same string for 1 and for (1,) while "{}".format(val) gives "1" and "(1,)"; the rewrite is made only once the operand's form is known. Inside a logging call an f-string trades one lint message for another, logging-fstring-interpolation, so the template stays.

## Validator
Grep the hunk for a str literal followed by the % operator or by .format(, and open the enclosing statement. Skip a bytes literal, a template held in a name and formatted elsewhere, and the first argument of a logging call (debug, info, warning, error, exception, critical, log) whose values are passed as further arguments; a literal formatted with % or .format inside a logging call's arguments is a finding whose fix passes the values to the logger. For a single %s whose right operand is not a literal tuple, trace whether the operand can be a tuple before proposing the f-string. Validator question: **Is a str literal formatted in place with the % operator or a .format call, outside a logging call's template, where an f-string can carry the values?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-37`, severity minor, `file`, `symbol`, `code` = the literal with its % operand or .format call, quoted verbatim from the diff, `fix` = the same text as an f-string, e.g. `f"Sent {count} messages"`, or inside a logging call the %-template with the values as the call's arguments, `rationale` = printf-style formatting has quirks and reads worse than f-strings, which are generally preferred over str.format, while a logger formats its template only for a record it emits).

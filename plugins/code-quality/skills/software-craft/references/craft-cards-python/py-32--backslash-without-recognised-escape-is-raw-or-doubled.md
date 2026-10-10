---
title: A Python string or bytes literal holds no backslash before a character that starts no recognised escape sequence, and writes such a backslash as a raw string or a doubled backslash
rule_id: PY-32
domain: code
step: [implement, review]
applies_to: [python]
triggers: ['\\[^\\\x27"abfnrtvx0-7NuU\n]', '\b[bB]["\x27][^"\x27]*\\[NuU]']
scope: hunk
check_kind: mechanical
severity_default: major
---

# A Python string or bytes literal holds no backslash before a character that starts no recognised escape sequence, and writes such a backslash as a raw string or a doubled backslash

## Thesis
Every backslash in a Python string or bytes literal either begins an escape sequence Python recognises for that kind of literal or is written as a doubled backslash or inside a raw literal (prefix `r` or `R`); in a bytes literal, `\N`, `\u` and `\U` begin no recognised escape.

## Rationale
Python leaves every unrecognised escape sequence in the string unchanged, that is, the backslash is left in the result, so `\z` is the same as `\\z`, which is not clear to the reader of the code. Unrecognised escape sequences produce a `DeprecationWarning` since Python 3.6 and a `SyntaxWarning` since Python 3.12, and the reference states that in a future Python version they will raise a `SyntaxError`. One literal can mix both kinds of backslash: in `"C:\data\reports"` the `\d` stays as written while `\r` is the recognised escape for an ASCII carriage return. For bytes literals, the escape sequences only recognised in string literals (`\N`, `\u`, `\U`) fall into the category of unrecognised escapes. A raw literal treats backslashes as literal characters, and in a non-raw literal the `\\` escape sequence denotes a single backslash character, so either spelling yields the backslash without an unrecognised escape.

## Example
```python
bad:  report_dir = "C:\data\reports"   # \d is kept, \r becomes a carriage return
      pattern = "\d+\.\d+"
good: report_dir = r"C:\data\reports"
      pattern = r"\d+\.\d+"
```

## Limits
A backslash that begins a recognised escape is outside the rule: `\\`, `\'`, `\"`, `\a`, `\b`, `\f`, `\n`, `\r`, `\t`, `\v`, an octal `\ooo`, a hex `\xhh`, a backslash before a newline, and in string literals `\N{name}`, `\uxxxx` and `\Uxxxxxxxx`. A raw literal cannot end in a single backslash, since the backslash would escape the following quote character, so a value that ends in a backslash doubles it instead of taking the `r` prefix.

## Validator
Grep the hunk for a backslash inside a string or bytes literal followed by a character other than a backslash, a quote, `a`, `b`, `f`, `n`, `r`, `t`, `v`, `x`, an octal digit or a newline, and in a bytes literal for `\N`, `\u` or `\U`. Open the literal and read its prefix: an `r` or `R` prefix makes it raw and ends the check; in a string literal `\N`, `\u` and `\U` are recognised escapes. Validator question: **Does a non-raw string or bytes literal in the hunk hold a backslash followed by a character that begins no escape sequence Python recognises for that kind of literal?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-32`, severity major, `file`, `symbol`, `code` = the literal as written in the diff, `fix` = the same literal with an `r` prefix or each lone backslash doubled, such as `r"C:\data\reports"`, `rationale` = Python keeps the backslash of an unrecognised escape, warns with SyntaxWarning since 3.12 and states that a future version raises SyntaxError, while the same literal may hold recognised escapes such as `\r`).

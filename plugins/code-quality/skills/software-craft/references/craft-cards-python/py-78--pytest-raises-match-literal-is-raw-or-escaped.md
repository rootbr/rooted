---
title: A string literal passed as match to pytest.raises is a raw string or is escaped whenever it contains a regex metacharacter
rule_id: PY-78
domain: tests
step: [test, review]
applies_to: [python, tests]
triggers: ['pytest[.]raises\(.*\bmatch\s*=\s*["''][^"'']*[.^$*+?{}()|\[\]]', '\bmatch\s*=\s*["''][^"'']*[.^$*+?{}()|\[\]]']
scope: hunk
check_kind: mechanical
severity_default: minor
---

# A string literal passed as match to pytest.raises is a raw string or is escaped whenever it contains a regex metacharacter

## Thesis
A string literal passed as `match=` to pytest.raises that contains a regex metacharacter such as `.`, `(` or `*` is a raw string `r"..."` when it is meant as a regular expression, and has its metacharacters escaped with backslashes or the whole string wrapped in `re.escape()` when it is meant as the literal message.

## Rationale
pytest.raises treats `match` as a string containing a regular expression, or a regular expression object, that is tested against the string representation of the exception and its PEP 678 `__notes__` using `re.search`. The `match` argument is implicitly converted to a regex, so an ordinary literal leaves unstated whether the string is meant as a regex or as a plain pattern. In a regular expression, `.` in the default mode matches any character except a newline, and `(...)` matches whatever regular expression is inside the parentheses and indicates the start and end of a group, so these characters in a message copied verbatim carry pattern meaning. To match a literal string that may contain special characters, the pattern can first be escaped with `re.escape`; a raw string signals the intention that the pattern is a regular expression.

## Example
```python
bad:  with pytest.raises(ValueError, match="invalid port (expected 1-65535)."):
          parse_port("x")
good: with pytest.raises(ValueError, match=re.escape("invalid port (expected 1-65535).")):
          parse_port("x")
```

## Limits
A literal whose metacharacter still matches the intended message, as a trailing `.` matches the final period, is in the rule as well, because the rule asks the literal to state whether it is a regex or a plain pattern. A `match=` given as a raw string, as `re.escape(...)` or as a regular expression object meets the rule. In the callable form `pytest.raises(E, func, ...)`, `match` is passed through to the function and not used by pytest.raises, and the rule reaches only the `match` of pytest.raises.

## Validator
Grep the hunk for `pytest.raises(` calls whose `match=` value is a string literal without the r prefix. Read the literal for `.`, `^`, `$`, `*`, `+`, `?`, `{`, `}`, `[`, `]`, `|`, `(` or `)` not preceded by a backslash, and check that the literal is not the argument of `re.escape(`. Validator question: **Does a pytest.raises call in the hunk pass as match= a string literal without the r prefix that contains an unescaped regex metacharacter?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-78`, severity minor, `file`, `symbol`, `code` = the pytest.raises line with its match= literal, verbatim from the diff, `fix` = the literal wrapped as `re.escape("...")` when the message is meant literally, or written as `r"..."` when a pattern is meant, `rationale` = that match is tested with re.search, so the unescaped metacharacter carries regular-expression meaning).

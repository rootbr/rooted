---
title: A Python str.format call or %-format mapping passes exactly the arguments and keys its template's fields use, since an unused one is dropped without an error
rule_id: PY-35
domain: code
step: [implement, review]
applies_to: [python]
triggers: ['[.]format\(', '["\x27]\s*%\s*[({]']
scope: hunk
check_kind: mechanical
severity_default: major
---

# A Python str.format call or %-format mapping passes exactly the arguments and keys its template's fields use, since an unused one is dropped without an error

## Thesis
Every positional and keyword argument of a Python `str.format` call, and every key of a mapping formatted with the `%` operator, is used by a replacement field of the template, including on a template that holds no replacement field at all.

## Rationale
A string formatted with `%` or `str.format` does not return the expected text when some arguments are unused, and Python reports nothing: the `string.Formatter` class, which uses the same implementation as the built-in `str.format`, leaves the check for unused arguments to a `check_unused_args` hook to implement if desired. Unused positional arguments of `str.format` are redundant and often indicative of a mistake, and unused named placeholders in a printf-style mapping are likely indicative of a mistake. A printf-style format given too many or too few positional substitution values raises `TypeError` at runtime instead, so the silent cases are the unused `str.format` argument and the unused mapping key.

## Example
```python
bad:  label = "{x} {y}".format(x=1, y=2, z=3)
      line = "%(color)s fox" % {"color": "red", "action": "hops"}
good: label = "{x} {y} {z}".format(x=1, y=2, z=3)
      line = "%(color)s fox %(action)s" % {"color": "red", "action": "hops"}
```

## Limits
Logging calls take a `%`-style template too and log an error instead of raising an exception when the provided arguments are invalid; they are outside this card. An f-string reports any syntax mistake at compile time, but a forgotten pair of curly braces in it leads to no detectable error. A `string.Formatter` subclass whose `check_unused_args` raises an exception makes the check at run time.

## Validator
Grep the hunk for `.format(` calls and for `%` applied to a string literal with a dict display. Read the template's replacement fields (`{name}`, `{0}`, auto-numbered `{}`, `%(key)s`) and compare them with the arguments written in the call or the keys of the dict display; skip a call whose values come from `**` unpacking or from a mapping variable whose keys the hunk does not show. Validator question: **Does a `str.format` call or `%` mapping format in the hunk pass a positional argument, keyword argument or mapping key that no replacement field of its template uses?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-35`, severity major, `file`, `symbol`, `code` = the template and its arguments as written in the diff, `fix` = the template naming every value it receives, or the surplus argument removed, in Python, `rationale` = Python's str.format and %-mapping formatting drop an unused value without an error, so the text is not the one expected).

## Source
- SonarSource python S3457 (SonarSource/sonar-python python-checks/src/main/resources/org/sonar/l10n/py/rules/python/S3457.html) — "A string formatted with % will not return the expected text because some arguments are unused."; "A string formatted with str.format will not return the expected string because some arguments are unused."; "they will log an error instead of raising an exception when the provided arguments are invalid"; "any syntax mistake will cause a failure at compile time. However, it is easy to forget curly braces, which will not lead to any detectable errors." (fetched)
- CPython Doc/library/string.rst §Custom String Formatting (python/cpython Doc/library/string.rst) — "using the same implementation as the built-in"; "Implement checking for unused arguments if desired."; "is assumed to raise an exception if the check fails" (fetched)
- Ruff F523 string-dot-format-extra-positional-arguments (astral-sh/ruff crates/ruff_linter/src/rules/pyflakes/rules/strings.rs) — "Unused positional arguments are redundant, and often indicative of a mistake." (fetched)
- Ruff F504 percent-format-extra-named-arguments (astral-sh/ruff crates/ruff_linter/src/rules/pyflakes/rules/strings.rs) — "Unused named placeholders in printf-style format strings are unnecessary, and likely indicative of a mistake." (fetched)
- Ruff F507 percent-format-positional-count-mismatch (astral-sh/ruff crates/ruff_linter/src/rules/pyflakes/rules/strings.rs) — "When a printf-style format string is provided with too many or too few substitution values, it will raise a TypeError at runtime." (fetched)
- Pylint unused-format-string-argument (W1304) (pylint-dev/pylint doc/data/messages/u/unused-format-string-argument/bad.py) — 'print("{x} {y}".format(x=1, y=2, z=3))  # [unused-format-string-argument]' (fetched)
- Pylint unused-format-string-key (W1301) (pylint-dev/pylint doc/data/messages/u/unused-format-string-key/bad.py) — "The quick %(color)s fox jumps over the lazy dog." with the unused key action (fetched)
- Pylint format-string-without-interpolation (W1310) (pylint-dev/pylint doc/data/messages/f/format-string-without-interpolation/bad.py) — 'print("number".format(1))  # [format-string-without-interpolation]' (fetched)

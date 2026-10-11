---
title: Python code takes the current or an epoch-derived UTC moment from datetime.now(timezone.utc) or datetime.fromtimestamp(ts, timezone.utc), never from datetime.utcnow() or datetime.utcfromtimestamp(), which return naive values
rule_id: PY-33
domain: code
step: [implement, review]
applies_to: [python]
triggers: ['\butcnow\(', '\butcfromtimestamp\(']
scope: hunk
check_kind: mechanical
severity_default: major
---

# Python code takes the current or an epoch-derived UTC moment from datetime.now(timezone.utc) or datetime.fromtimestamp(ts, timezone.utc), never from datetime.utcnow() or datetime.utcfromtimestamp(), which return naive values

## Thesis
Python code takes the current UTC moment from `datetime.now(timezone.utc)` and converts a POSIX timestamp to a UTC moment with `datetime.fromtimestamp(ts, timezone.utc)`, in place of `datetime.utcnow()` and `datetime.utcfromtimestamp(ts)`.

## Rationale
`datetime.utcnow()` returns the current UTC date and time as a naive datetime, with `tzinfo` None, and `datetime.utcfromtimestamp()` returns the UTC datetime of a POSIX timestamp with `tzinfo` None, so the resulting object is naive: the two functions are not time zone aware, even though their names suggest otherwise. An aware object represents a specific moment in time, while a naive object does not contain enough information to unambiguously locate itself relative to other datetime objects, and many `datetime` methods treat naive datetime objects as local times. A value of `datetime.utcfromtimestamp(ts)` therefore fails to round-trip: its `.timestamp()` differs from `ts` when the system locale is not set to UTC. Both functions are deprecated since Python 3.12, and the documentation names `datetime.now` and `datetime.fromtimestamp` with UTC as their replacements.

## Example
```python
bad:  created_at = datetime.utcnow()
      expires_at = datetime.utcfromtimestamp(ts)
good: created_at = datetime.now(timezone.utc)
      expires_at = datetime.fromtimestamp(ts, timezone.utc)
```

## Limits
`datetime.fromtimestamp(ts)` without a time zone converts the timestamp to the platform's local date and time and returns a naive object, so the replacement passes the zone explicitly. On Python 3.11 and later the replacement can also be spelled with `datetime.UTC`, as in `datetime.now(tz=UTC)`. The card reaches calls of the two named functions only.

## Validator
Grep the hunk for `utcnow(` and `utcfromtimestamp(`. Open each call and confirm its receiver is the `datetime` class of the standard `datetime` module, imported as `datetime` or reached as `datetime.datetime`. Where the hunk already holds a replacement, confirm that `fromtimestamp` receives a time zone. Validator question: **Does the hunk call `utcnow()` or `utcfromtimestamp()` of the standard library `datetime` class?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-33`, severity major, `file`, `symbol`, `code` = the `utcnow()` or `utcfromtimestamp()` call as written in the diff, `fix` = `datetime.now(timezone.utc)` or `datetime.fromtimestamp(ts, timezone.utc)` in its place, `rationale` = both functions return naive values that many datetime methods treat as local time, and both are deprecated since Python 3.12).

## Source
- Python documentation library/datetime §datetime.utcnow (https://docs.python.org/3/library/datetime.html) — "Return the current UTC date and time, with tzinfo None"; "but returns the current UTC date and time, as a naive datetime object"; "Because naive datetime objects are treated by many datetime methods as local times"; "the recommended way to create an object representing the current time in UTC is by calling datetime.now(timezone.utc)"; "Deprecated since version 3.12: Use datetime.now() with UTC instead." (fetched)
- Python documentation library/datetime §datetime.utcfromtimestamp and §datetime.fromtimestamp (https://docs.python.org/3/library/datetime.html) — "(The resulting object is naive.)"; "Use datetime.fromtimestamp() with UTC instead."; "local date and time, and the returned datetime object is naive" (fetched)
- SonarSource python S6903 (SonarSource/sonar-python python-checks/src/main/resources/org/sonar/l10n/py/rules/python/S6903.html) — "The issue with these two functions is they are not time zone aware, even if their name would suggest otherwise."; "This assertion will fail if the system locale is not set to UTC. For this reason these 2 functions are deprecated in Python 3.12." (fetched)
- Ruff DTZ003 call-datetime-utcnow (astral-sh/ruff crates/ruff_linter/src/rules/flake8_datetimez/rules/call_datetime_utcnow.rs) — "While an aware object represents a specific moment in time, a naive object does not contain enough information to unambiguously locate itself relative to other datetime objects."; "datetime.datetime.utcnow() returns a naive datetime object; instead, use"; "Or, for Python 3.11 and later:" (fetched)
- Ruff DTZ004 call-datetime-utcfromtimestamp (astral-sh/ruff crates/ruff_linter/src/rules/flake8_datetimez/rules/call_datetime_utcfromtimestamp.rs) — "datetime.datetime.utcfromtimestamp() returns a naive datetime" (fetched)

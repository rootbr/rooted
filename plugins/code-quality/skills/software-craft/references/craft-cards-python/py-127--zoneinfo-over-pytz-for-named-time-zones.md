---
title: Code targeting Python 3.9 or later takes a named time zone from zoneinfo.ZoneInfo rather than pytz, whose zones take the earliest known offset unless attached through localize()
rule_id: PY-127
domain: code
step: [design, implement, review]
applies_to: [python]
triggers: ['^\s*import\s+pytz\b', '^\s*from\s+pytz\b', '\bpytz[.](?:timezone|utc|UTC|FixedOffset)\b', '[.]localize\(']
scope: file
check_kind: mechanical
severity_default: minor
---

# Code targeting Python 3.9 or later takes a named time zone from zoneinfo.ZoneInfo rather than pytz, whose zones take the earliest known offset unless attached through localize()

## Thesis
Where the project targets Python 3.9 or later, a named time zone is a `zoneinfo.ZoneInfo` attached to `tzinfo` through the `datetime` constructor, `datetime.replace` or `datetime.astimezone`, rather than a pytz zone object.

## Rationale
The `zoneinfo` module, added to the standard library in Python 3.9, provides `ZoneInfo` as a concrete implementation of the `datetime.tzinfo` abstract base class, intended to be attached to `tzinfo` through the constructor, `datetime.replace` or `datetime.astimezone`. A pytz zone object passed as the `tzinfo` argument of the `datetime.datetime` constructor uses the earliest known offset for that zone, which may not match the current or most commonly used offset: `datetime.datetime(2022, 1, 1, tzinfo=pytz.timezone('US/Eastern'))` is `2022-01-01 00:00:00-04:56`, where the zone's `localize` method gives `2022-01-01 00:00:00-05:00`. pytz needs that separate `localize` method to attach a zone correctly, and the wrong offset leads to subtle bugs, especially in calculations with datetime objects. A `ZoneInfo` object is used directly when a `datetime` is created and has no earliest-offset issue. The `fold` attribute, added to address ambiguous datetimes, obviates the need for pytz's non-standard `tzinfo` classes. pytz also includes its own copy of the IANA time zone database, which may not be as current as the system database that `zoneinfo` uses when one is available.

## Example
```python
bad:  from datetime import datetime
      import pytz
      start = datetime(2022, 1, 1, tzinfo=pytz.timezone("America/New_York"))
good: from datetime import datetime
      from zoneinfo import ZoneInfo
      start = datetime(2022, 1, 1, tzinfo=ZoneInfo("America/New_York"))
```

## Limits
Code that must also run on Python 3.8 or earlier is outside the rule, since `zoneinfo` exists from Python 3.9. A pytz zone attached through `localize` gets the correct offset, so on such code the finding is the move to `zoneinfo` rather than a wrong offset.

## Validator
Grep the file for `import pytz`, `from pytz`, `pytz.timezone(` and `.localize(` calls. Read the project's lowest supported Python version from `requires-python` in `pyproject.toml`, `python_requires` in `setup.cfg` or `setup.py`, or the Ruff `target-version`; a floor below 3.9 ends the check. For each pytz zone built from a zone name, trace where it is attached: the `tzinfo` argument of the `datetime` constructor, which takes the zone's earliest known offset, or `localize`, which attaches it correctly. A `pytz.utc` or `pytz.FixedOffset` use with no named zone is outside the question. Validator question: **Does code in a project whose floor is Python 3.9 or later build a named time zone from pytz rather than `zoneinfo.ZoneInfo`?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-127`, severity minor, `file`, `symbol`, `code` = the line that creates or attaches the pytz zone, `fix` = the same `datetime` built with `tzinfo=ZoneInfo("<zone name>")` after `from zoneinfo import ZoneInfo`, `rationale` = the earliest known offset a pytz zone takes through `tzinfo`, or the separate `localize` step it needs, on a project whose floor is Python 3.9 or later).

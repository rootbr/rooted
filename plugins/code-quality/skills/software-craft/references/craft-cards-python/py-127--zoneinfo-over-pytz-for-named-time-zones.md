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

## Source
- SonarSource sonar-python rule S6890 (https://raw.githubusercontent.com/SonarSource/sonar-python/master/python-checks/src/main/resources/org/sonar/l10n/py/rules/python/S6890.html) — 'This rule raises an issue when using the pytz library on a codebase using Python 3.9 or later.' … 'You can directly use zoneinfo timezone objects when creating datetime objects, making it more intuitive and less error-prone than pytz, which requires a separate localize method for this purpose.' … 'When a pytz timezone object is used, it defaults to the earliest known offset, which can lead to unexpected results. zoneinfo does not have this issue.' … 'zoneinfo uses the system’s IANA time zone database when available' … 'pytz includes its own copy of the IANA database, which may not be as current.' (fetched)
- SonarSource sonar-python rule S6887 (https://raw.githubusercontent.com/SonarSource/sonar-python/master/python-checks/src/main/resources/org/sonar/l10n/py/rules/python/S6887.html) — 'When you create a datetime object with a pytz timezone object as the tzinfo argument, it uses the earliest known offset for that timezone. This can lead to unexpected offsets, as the earliest known offset may not match the current or most commonly used offset for that timezone.' … 'This can lead to subtle bugs in your code, especially if you’re doing calculations with datetime objects.' … 'This method correctly handles historical changes and other timezone-related issues.' … '# Noncompliant: 2022-01-01 00:00:00-04:56' … '# OK: 2022-01-01 00:00:00-05:00' (fetched)
- CPython Doc/library/zoneinfo.rst §Using ZoneInfo (https://raw.githubusercontent.com/python/cpython/main/Doc/library/zoneinfo.rst) — ':class:`ZoneInfo` is a concrete implementation of the :class:`datetime.tzinfo` abstract base class, and is intended to be attached to ``tzinfo``, either via the constructor, the :meth:`datetime.replace <datetime.datetime.replace>` method or :meth:`datetime.astimezone <datetime.datetime.astimezone>`' … '.. versionadded:: 3.9' (fetched)
- PEP 615 §Using a pytz-like interface (https://raw.githubusercontent.com/python/peps/main/peps/pep-0615.rst) — 'was ultimately withdrawn / rejected for lack of ambiguous datetime support.' … "added the ``fold`` attribute to address this problem, but ``fold`` obviates the need for … non-standard ``tzinfo`` classes, and so a … interface is no longer necessary." (fetched)

---
title: A Python defaultdict gets its factory as the first positional argument, because a default_factory keyword becomes a dict entry and leaves missing keys raising KeyError
rule_id: PY-59
domain: performance
step: [implement, review]
applies_to: [python]
triggers: ['\bdefaultdict\(.*\bdefault_factory\s*=', '^\s*default_factory\s*=\s*[\w.]+\s*[,)]']
scope: hunk
check_kind: mechanical
severity_default: major
---

# A Python defaultdict gets its factory as the first positional argument, because a default_factory keyword becomes a dict entry and leaves missing keys raising KeyError

## Thesis
`collections.defaultdict` receives its factory as the first positional argument, as in `defaultdict(list)`, and not as the keyword `default_factory=`.

## Rationale
The first argument provides the initial value of the `default_factory` attribute, which defaults to `None`, and all remaining arguments are treated as if they were passed to the `dict` constructor, keyword arguments included. `defaultdict(default_factory=list)` therefore creates a dictionary with `{"default_factory": list}` as its initial entry instead of a dictionary that returns `[]` when a key is missing. With `default_factory` left at `None`, the defaultdict behaves like a regular dict for missing keys and raises `KeyError` when one is accessed. The constructor accepts the call, and the mistake is one that type checkers can't reliably detect. The factory given positionally restores the default: `defaultdict(list)` returns `[]` and `defaultdict(int)` returns `0` when a key is missing.

## Example
```python
bad:  from collections import defaultdict
      index = defaultdict(default_factory=list)
good: from collections import defaultdict
      index = defaultdict(list)
```

## Limits
Keyword arguments other than `default_factory` are initial entries by design, as for the `dict` constructor: `defaultdict(foo=1, bar=2)` starts with `{"foo": 1, "bar": 2}`. The `default_factory` keyword is almost always a mistake rather than always one; the remaining case is a dictionary meant to start with an entry under the key `"default_factory"`.

## Validator
Grep the hunk for `default_factory=`. Open the call that owns the keyword, which may start lines above in a multi-line argument list, and confirm it is `collections.defaultdict` under its imported name or alias, not `dataclasses.field()` or another callable whose own `default_factory` parameter takes the keyword by design.
Validator question: **Does a `collections.defaultdict` call pass `default_factory` as a keyword argument?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-59`, severity major, `file`, `symbol`, `code` = the defaultdict call with its `default_factory=` keyword, `fix` = the factory as the first positional argument, as `defaultdict(list)`, `rationale` = the keyword becomes an initial dict entry, `default_factory` stays `None` and a missing key raises `KeyError`).

## Source
- CPython Doc/library/collections.rst §defaultdict objects (https://raw.githubusercontent.com/python/cpython/main/Doc/library/collections.rst) — 'The first argument provides the initial value for the :attr:`default_factory` attribute; it defaults to ``None``. All remaining arguments are treated the same as if they were passed to the :class:`dict` constructor, including keyword arguments.' (fetched)
- CPython Doc/library/collections.rst §defaultdict objects (https://raw.githubusercontent.com/python/cpython/main/Doc/library/collections.rst) — 'If the :attr:`default_factory` attribute is ``None``, this raises a :exc:`KeyError` exception with the *key* as argument.' (fetched)
- Ruff RUF026 default-factory-kwarg (astral-sh/ruff crates/ruff_linter/src/rules/ruff/rules/default_factory_kwarg.rs) — 'As such, `defaultdict(default_factory=list)` will create a dictionary with `{"default_factory": list}` as its initial entry, instead of a dictionary that returns `[]` when a key is missing. Specifying a `default_factory` keyword argument is almost always a mistake, and one that type checkers can't reliably detect.' (fetched)
- Ruff RUF026 default-factory-kwarg (astral-sh/ruff crates/ruff_linter/src/rules/ruff/rules/default_factory_kwarg.rs) — 'For example, `defaultdict(foo=1, bar=2)` will create a dictionary with `{"foo": 1, "bar": 2}` as its initial entries.' (fetched)
- Ruff RUF026 default-factory-kwarg (astral-sh/ruff crates/ruff_linter/src/rules/ruff/rules/default_factory_kwarg.rs) — 'to create a dictionary that returns `0` or `[]` respectively when a key is missing' (fetched)
- SonarSource python S7507 (SonarSource/sonar-python python-checks/src/main/resources/org/sonar/l10n/py/rules/python/S7507.html) — 'It does not set the default factory for missing keys. The defaultdict behaves like a regular dict in this regard and will raise a KeyError when a missing key is accessed.' (fetched)

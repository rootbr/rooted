---
title: A default passed to os.getenv is a str or None, and a value of another type is obtained by converting the result
rule_id: PY-28
domain: code
step: [implement, review]
applies_to: [python]
triggers: ['\bgetenv\(\s*[^,()]+,\s*(default\s*=\s*)?(?!None\b|[rRbBuUfF]*[\x27"])\S', '\b(int|float|bool)\(\s*os[.]getenv\(']
scope: file
check_kind: mechanical
severity_default: major
---

# A default passed to os.getenv is a str or None, and a value of another type is obtained by converting the result

## Thesis
A default passed to `os.getenv` is a `str` or `None`; a value of another type is obtained by converting the result of a call whose default is a string, as in `int(os.getenv("WORKERS", "4"))`.

## Rationale
`os.getenv` returns the value of the environment variable as a string if it exists, or the default if it does not; with no default given, an unset variable yields `None`. A default that is not a string or `None` is therefore inconsistent with the return type of `os.getenv`: `os.getenv("PORT", 8080)` yields the `int` 8080 when `PORT` is unset and a `str` when it is set, so the type of the result depends on the environment, which can lead to confusing behavior. Passing the default as a string and converting the result, `int(os.getenv("PORT", "8080"))`, gives the conversion the same input type in both cases.

## Example
```python
bad:  port = os.getenv("PORT", 8080)
      workers = int(os.getenv("WORKERS", 4))
good: port = int(os.getenv("PORT", "8080"))
      workers = int(os.getenv("WORKERS", "4"))
```

## Limits
A `None` default, or no default, is in range: an unset variable then yields `None`. The rule covers `os.getenv`; `os.getenvb` returns the value of the variable as bytes if it exists, so the `str` expectation belongs to `os.getenv` only. A default given through a name is in range when that name holds a `str` or `None`.

## Validator
Grep the hunk for `getenv(` calls that pass a second positional argument or `default=`. For each, read the default: a string literal or `None` is in range; for a name, an attribute or a call, trace it to its assignment or annotation in the file. Validator question: **Does the hunk pass `os.getenv` a default that is neither a `str` nor `None`?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-28`, severity major, `file`, `symbol`, `code` = the `os.getenv(...)` call quoted verbatim, `fix` = the default written as a string with the result converted, such as `int(os.getenv("PORT", "8080"))`, `rationale` = `os.getenv` returns a `str` when the variable is set and the default unchanged when it is not, so a non-string default makes the result type depend on the environment).

## Source
- CPython Doc/library/os.rst §os.getenv (https://raw.githubusercontent.com/python/cpython/main/Doc/library/os.rst) — 'Return the value of the environment variable *key* as a string if it exists, or *default*' (fetched)
- CPython Doc/library/os.rst §os.getenvb (https://raw.githubusercontent.com/python/cpython/main/Doc/library/os.rst) — 'Return the value of the environment variable *key* as bytes if it exists' (fetched)
- Ruff PLW1508 invalid-envvar-default (astral-sh/ruff crates/ruff_linter/src/rules/pylint/rules/invalid_envvar_default.rs) — 'If an environment variable is set, `os.getenv` will return its value as a string.' (fetched)
- Ruff PLW1508 invalid-envvar-default (astral-sh/ruff crates/ruff_linter/src/rules/pylint/rules/invalid_envvar_default.rs) — 'will return `None`, or the default value if one is provided.' (fetched)
- Ruff PLW1508 invalid-envvar-default (astral-sh/ruff crates/ruff_linter/src/rules/pylint/rules/invalid_envvar_default.rs) — 'If the default value is not a string or `None`, then it will be inconsistent with the return type of `os.getenv`, which can lead to confusing behavior.' (fetched)
- Ruff PLW1508 invalid-envvar-default (astral-sh/ruff crates/ruff_linter/src/rules/pylint/rules/invalid_envvar_default.rs) — 'int(os.getenv("FOO", "1"))' (fetched)

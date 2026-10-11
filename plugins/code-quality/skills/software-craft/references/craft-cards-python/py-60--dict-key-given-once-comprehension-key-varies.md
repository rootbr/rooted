---
title: A Python dict display names each key once and a dict comprehension's key varies with its loop, because a repeated key silently keeps only the last value
rule_id: PY-60
domain: performance
step: [implement, review]
applies_to: [python]
triggers: ['(["\x27][^"\x27]+["\x27])\s*:.*\1\s*:', '\{\s*["\x27][^"\x27]*["\x27]\s*:[^}]*\bfor\b', '^\s*["\x27][\w.-]+["\x27]\s*:\s*\S']
scope: hunk
check_kind: mechanical
severity_default: major
---

# A Python dict display names each key once and a dict comprehension's key varies with its loop, because a repeated key silently keeps only the last value

## Thesis
A dict display gives each key once, and a dict comprehension's key expression varies with the comprehension's loop variable.

## Rationale
In a dict display and a dict comprehension alike, the expressions are evaluated from left to right and each key object is used as a key into the dictionary to store the corresponding value, so the same key may be specified multiple times and earlier values are overwritten by ones evaluated later. A display that repeats a key therefore keeps only the last value: when the repeated pair is identical the earlier entry is dead text, and when the values differ the earlier value is silently lost. A comprehension whose key is static, such as a string literal or a variable defined outside the comprehension and not updated during it, assigns every iteration to that same single key, so the dictionary contains one entry whose value is the one computed during the last iteration, despite the comprehension iterating over multiple values.

## Example
```python
bad:  config = {"timeout": 30, "retries": 3, "timeout": 60}
      names = {"name": row.name for row in rows}
good: config = {"timeout": 60, "retries": 3}
      names = {row.id: row.name for row in rows}
```

## Limits
Both forms are valid Python: a repeated key in a dictionary literal is likely a mistake and a static key in a comprehension usually one, not always. A comprehension whose key varies with the loop but repeats across elements, such as `{row.category: row for row in rows}`, keeps the last value given for each key, which is the documented behavior; its key is not static and the rule does not reach it. The rule covers the literal keys of one dict display and the key expression of a dict comprehension, not later assignments through `mapping[key] = value`.

## Validator
Grep the hunk for dict displays and dict comprehensions; a multi-line display spans the lines around the hunk, so open the whole display. List the display's literal keys and flag a key written twice, with the same value or a different one. For a comprehension, read the key expression before the colon and flag it when it is a literal or a name bound outside the comprehension and not rebound by it.
Validator question: **Does a dict display give the same key twice, or a dict comprehension use a static key, a literal or a name defined outside it and not updated during it?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-60`, severity major, `file`, `symbol`, `code` = the display with both occurrences of the key, or the comprehension with its static key, `fix` = the display with one entry for the key, or a key built from the loop variable, as `{row.id: row.name for row in rows}`, `rationale` = Python keeps only the last value for a repeated key, so the earlier entry is dead or lost and a static-key comprehension yields a dict of one item).

## Source
- CPython Doc/reference/expressions.rst §Dictionary displays (https://raw.githubusercontent.com/python/cpython/main/Doc/reference/expressions.rst) — 'At runtime, when a dictionary comprehension is evaluated, the expressions are evaluated from left to right. Each key object is used as a key into the dictionary to store the corresponding value.' (fetched)
- CPython Doc/reference/expressions.rst §Dictionary displays (https://raw.githubusercontent.com/python/cpython/main/Doc/reference/expressions.rst) — 'This means that you can specify the same key multiple times in the comprehension, and the final dictionary's value for a given key will be the last one given.' (fetched)
- CPython Doc/reference/expressions.rst §Comprehensions (https://raw.githubusercontent.com/python/cpython/main/Doc/reference/expressions.rst) — 'As in other kinds of dictionary displays, the same key may be specified multiple times. Earlier values are overwritten by ones that are evaluated later.' (fetched)
- Ruff F601 multi-value-repeated-key-literal (astral-sh/ruff crates/ruff_linter/src/rules/pyflakes/rules/repeated_keys.rs) — 'Dictionary keys should be unique. If a key is associated with multiple values, the earlier values will be overwritten. Including multiple values for the same key in a dictionary literal is likely a mistake.' (fetched)
- Ruff F601 multi-value-repeated-key-literal (astral-sh/ruff crates/ruff_linter/src/rules/pyflakes/rules/repeated_keys.rs) — 'Checks for dictionary literals that associate multiple values with the same key.' (fetched)
- flake8-bugbear B041 (PyCQA/flake8-bugbear README.rst) — 'Repeated key-value pair in dictionary literal.' (fetched)
- Ruff B035 static-key-dict-comprehension (astral-sh/ruff crates/ruff_linter/src/rules/flake8_bugbear/rules/static_key_dict_comprehension.rs) — 'Using a static key (like a string literal) in a dictionary comprehension is usually a mistake, as it will result in a dictionary with only one key, despite the comprehension iterating over multiple values.' (fetched)
- SonarSource python S7506 (SonarSource/sonar-python python-checks/src/main/resources/org/sonar/l10n/py/rules/python/S7506.html) — 'a variable defined outside the comprehension' (fetched)
- SonarSource python S7506 (SonarSource/sonar-python python-checks/src/main/resources/org/sonar/l10n/py/rules/python/S7506.html) — 'each iteration of the comprehension will attempt to assign a value to this same single key' (fetched)
- SonarSource python S7506 (SonarSource/sonar-python python-checks/src/main/resources/org/sonar/l10n/py/rules/python/S7506.html) — 'The consequence is that the dictionary will only contain one entry for that static key, and its value will be the one computed during the last iteration of the comprehension.' (fetched)

---
title: A pytest.warns block holds only the one simple statement expected to issue the warning, with setup and other calls outside it
rule_id: PY-80
domain: tests
step: [test, review]
applies_to: [python, tests]
triggers: ['^\s*with\s+pytest[.]warns\(', '^\s*with\s+.*,\s*pytest[.]warns\(']
scope: hunk
check_kind: mechanical
severity_default: minor
---

# A pytest.warns block holds only the one simple statement expected to issue the warning, with setup and other calls outside it

## Thesis
A `with pytest.warns(...)` block in a Python test contains only the single simple statement that is expected to issue the warning, and setup and further calls stand before or after the block.

## Rationale
`pytest.warns` requires the code inside the `with` block to issue at least one warning of the expected class or classes, and it records one `warnings.WarningMessage` for each warning emitted, whether or not that warning is of the expected class. Warnings are issued for conditions that normally do not warrant raising an exception and terminating the program, and the block records every warning emitted, so any statement in the block can supply the warning the check counts. With several statements in the block the test can therefore pass when it should fail: a setup call that issues the warning gives a false negative when the call under test issues none. Several calls in the block also leave it ambiguous which call is expected to emit the warning, while isolating the call under test makes the test explicit and unambiguous.

## Example
```python
bad:  with pytest.warns(DeprecationWarning):
          client = make_client()
          client.fetch("/v1")
good: client = make_client()
      with pytest.warns(DeprecationWarning):
          client.fetch("/v1")
```

## Limits
The rule reaches `pytest.warns` used as a context manager. The block may hold a single `for` loop whose body is only `pass` or `...`, to test iterator behaviour. A single statement that chains several calls, such as `get_item().process()`, passes the statement count while still leaving it ambiguous which call is expected to emit the warning.

## Validator
Grep the hunk for `with pytest.warns(`, whether it is the only context manager of the `with` statement or one of several. Open the block and list the statements of its body. Set aside a body that is one simple statement or one `for` loop whose body is only `pass` or `...`. For any other body, name the statements that are setup or further calls rather than the call expected to warn. Validator question: **Does the body of a `with pytest.warns(...)` block hold more than one statement, or one compound statement other than a `for` loop with an empty body?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-80`, severity minor, `file`, `symbol`, `code` = the `with pytest.warns(...)` line and the statements of its body, verbatim from the diff, `fix` = the Python test with setup and further calls moved before or after the block and only the call expected to warn left inside it, `rationale` = names the statement in the block, other than the call under test, that could issue the expected warning and let the test pass).

## Source
- Ruff PT031 pytest-warns-with-multiple-statements (astral-sh/ruff crates/ruff_linter/src/rules/flake8_pytest_style/rules/warns.rs) — 'When `pytest.warns` is used as a context manager and contains multiple statements, it can lead to the test passing when it should instead fail.' (fetched)
- Ruff PT031 pytest-warns-with-multiple-statements (astral-sh/ruff crates/ruff_linter/src/rules/flake8_pytest_style/rules/warns.rs) — 'A `pytest.warns` context manager should only contain a single simple statement that triggers the expected warning.' (fetched)
- Ruff PT031 pytest-warns-with-multiple-statements (astral-sh/ruff crates/ruff_linter/src/rules/flake8_pytest_style/rules/warns.rs) — 'False negative if setup triggers a warning but foo does not.' (fetched)
- Ruff PT031 pytest-warns-with-multiple-statements (astral-sh/ruff crates/ruff_linter/src/rules/flake8_pytest_style/rules/warns.rs) — 'This rule allows `pytest.warns` bodies to contain `for` loops with empty bodies (e.g., `pass` or `...` statements), to test iterator behavior.' (fetched)
- SonarSource python S9088 (SonarSource/sonar-python python-checks/src/main/resources/org/sonar/l10n/py/rules/python/S9088.html) — 'If you put several method calls inside a pytest.warns block, or chain multiple invocations in the tested expression, it becomes ambiguous which specific call is expected to emit the warning.' (fetched)
- SonarSource python S9088 (SonarSource/sonar-python python-checks/src/main/resources/org/sonar/l10n/py/rules/python/S9088.html) — 'By isolating the method call you want to test, you make the test explicit and unambiguous.' (fetched)
- pytest src/_pytest/recwarn.py §pytest.warns docstring (https://raw.githubusercontent.com/pytest-dev/pytest/main/src/_pytest/recwarn.py) — 'the code inside the ``with`` block must issue at least one warning of that class or classes.' (fetched)
- pytest src/_pytest/recwarn.py §pytest.warns docstring (https://raw.githubusercontent.com/pytest-dev/pytest/main/src/_pytest/recwarn.py) — 'one for each warning emitted (regardless of whether it is an ``expected_warning`` or not).' (fetched)
- CPython Doc/library/warnings.rst §warnings (https://raw.githubusercontent.com/python/cpython/main/Doc/library/warnings.rst) — 'where that condition (normally) doesn't warrant raising an exception and terminating the program.' (fetched)

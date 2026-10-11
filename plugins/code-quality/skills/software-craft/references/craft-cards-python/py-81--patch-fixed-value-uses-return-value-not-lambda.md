---
title: A mock.patch or mocker.patch that only makes the target return a fixed value passes return_value rather than a lambda that ignores its arguments
rule_id: PY-81
domain: tests
step: [test, refactor, review]
applies_to: [python, tests]
triggers: ['patch\(\s*[\x22\x27][^\x22\x27]+[\x22\x27]\s*,\s*lambda\b', 'patch[.]object\([^,]+,\s*[\x22\x27][^\x22\x27]+[\x22\x27]\s*,\s*lambda\b', '\bpatch\(.*\blambda\b']
scope: hunk
check_kind: mechanical
severity_default: minor
---

# A mock.patch or mocker.patch that only makes the target return a fixed value passes return_value rather than a lambda that ignores its arguments

## Thesis
When a `unittest.mock.patch`, `patch.object` or pytest-mock `mocker.patch` call only needs the patched target to return a fixed value, it passes `return_value=` rather than a `lambda` whose body uses none of its parameters.

## Rationale
With *new* omitted, `patch` replaces the target with a `MagicMock`, or an `AsyncMock` when the patched object is an async function, and passes its other keyword arguments, such as `return_value`, to that mock, or to *new_callable* when one is given; `patch.object` takes the same keyword arguments for configuring the mock it creates, and `patch` used as a context manager returns the created mock. That mock allows verification of the number of calls or of the arguments passed to the patched function through `assert_called_once_with` and related methods. A lambda passed in its place adds an unnecessary callable, and the mock no longer supports those assertions. An explicit `return_value` also conveys the intent better than a lambda that does not use the arguments passed to it, and it is robust to changes in the patched function's signature.

## Example
```python
bad:  mocker.patch("app.api.fetch", lambda *args: {"ok": True})
      assert sync_orders() == 1
good: fetch = mocker.patch("app.api.fetch", return_value={"ok": True})
      assert sync_orders() == 1
      fetch.assert_called_once_with("/v1/orders")
```

## Limits
A lambda that uses its parameters expresses custom behaviour rather than a constant stub and is outside the rule. A stub that must use the call arguments or run custom logic keeps a lambda or uses `side_effect`.

## Validator
Grep the hunk for `patch(`, `patch.object(` and `mocker.patch(` calls whose replacement argument is a `lambda`. Open the lambda and compare its body with its parameter list, `*args` and `**kwargs` included. Validator question: **Does a `patch`, `patch.object` or `mocker.patch` call pass a `lambda` whose body uses none of its parameters?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-81`, severity minor, `file`, `symbol`, `code` = the patch call with its lambda, verbatim from the diff, `fix` = the same Python patch call with `return_value=` set to the value the lambda returned and the returned mock bound to a name when the test asserts on calls, `rationale` = names that the lambda ignores its parameters and that the mock created with return_value keeps call assertions such as assert_called_once_with).

## Source
- Ruff PT008 pytest-patch-with-lambda (astral-sh/ruff crates/ruff_linter/src/rules/flake8_pytest_style/rules/patch.rs) — 'When patching calls, an explicit `return_value` better conveys the intent than a `lambda` function, assuming the `lambda` does not use the arguments passed to it.' (fetched)
- Ruff PT008 pytest-patch-with-lambda (astral-sh/ruff crates/ruff_linter/src/rules/flake8_pytest_style/rules/patch.rs) — '`return_value` is also robust to changes in the patched function's signature, and enables additional assertions to verify behavior.' (fetched)
- Ruff PT008 pytest-patch-with-lambda (astral-sh/ruff crates/ruff_linter/src/rules/flake8_pytest_style/rules/patch.rs) — 'allows for verification of the number of calls or the arguments passed to the patched function via `assert_called_once_with` and related methods.' (fetched)
- Ruff PT008 pytest-patch-with-lambda (astral-sh/ruff crates/ruff_linter/src/rules/flake8_pytest_style/rules/patch.rs) — 'If the lambda makes use of the arguments, no diagnostic is emitted.' (fetched)
- SonarSource python S9081 (SonarSource/sonar-python python-checks/src/main/resources/org/sonar/l10n/py/rules/python/S9081.html) — 'patch and mocker.patch often stub a dependency so the code under test receives a fixed value.' (fetched)
- SonarSource python S9081 (SonarSource/sonar-python python-checks/src/main/resources/org/sonar/l10n/py/rules/python/S9081.html) — 'The lambda adds an unnecessary callable, and the mock no longer supports the usual assertions such as assert_called_once_with.' (fetched)
- SonarSource python S9081 (SonarSource/sonar-python python-checks/src/main/resources/org/sonar/l10n/py/rules/python/S9081.html) — 'This rule does not raise when the lambda uses its parameters, because that expresses custom behavior rather than a constant stub.' (fetched)
- SonarSource python S9081 (SonarSource/sonar-python python-checks/src/main/resources/org/sonar/l10n/py/rules/python/S9081.html) — 'Keep a lambda (or side_effect) only when the stub must use call arguments or run custom logic.' (fetched)
- CPython Doc/library/unittest.mock.rst §patch (https://raw.githubusercontent.com/python/cpython/main/Doc/library/unittest.mock.rst) — 'If *new* is omitted, then the target is replaced with an :class:`AsyncMock` if the patched object is an async function or a :class:`MagicMock` otherwise.' (fetched)
- CPython Doc/library/unittest.mock.rst §patch (https://raw.githubusercontent.com/python/cpython/main/Doc/library/unittest.mock.rst) — ':func:`patch` takes arbitrary keyword arguments. These will be passed to :class:`AsyncMock` if the patched object is asynchronous, to :class:`MagicMock` otherwise or to *new_callable* if specified.' (fetched)
- CPython Doc/library/unittest.mock.rst §patch (https://raw.githubusercontent.com/python/cpython/main/Doc/library/unittest.mock.rst) — 'If :func:`patch` is used as a context manager the created mock is returned by the context manager.' (fetched)
- CPython Doc/library/unittest.mock.rst §patch.object (https://raw.githubusercontent.com/python/cpython/main/Doc/library/unittest.mock.rst) — 'Like :func:`patch`, :func:`patch.object` takes arbitrary keyword arguments for configuring the mock object it creates.' (fetched)

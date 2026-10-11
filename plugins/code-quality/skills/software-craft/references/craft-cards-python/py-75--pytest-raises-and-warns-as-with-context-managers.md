---
title: pytest.raises, pytest.warns and pytest.deprecated_call wrap the code they check as the context manager of a with statement, never as a bare call or in the callable form
rule_id: PY-75
domain: tests
step: [test, review]
applies_to: [python, tests]
triggers: ['^\s*pytest[.]raises\(', '^\s*\w+\s*=\s*pytest[.](raises|warns|deprecated_call)\(', '^\s*pytest[.](warns|deprecated_call)\(', 'pytest[.](raises|warns)\(\s*[\w.]+\s*,\s*[\w.]+\s*[,)]']
scope: hunk
check_kind: mechanical
severity_default: major
---

# pytest.raises, pytest.warns and pytest.deprecated_call wrap the code they check as the context manager of a with statement, never as a bare call or in the callable form

## Thesis
A pytest test wraps the code that must raise in `with pytest.raises(E):` and the code that must warn in `with pytest.warns(W):` or `with pytest.deprecated_call():`, so each checker is the context manager of a with statement; the test writes it neither as a bare call statement nor in the callable form `pytest.raises(E, func, *args)`, `pytest.warns(W, func, *args)` or `pytest.deprecated_call(func, *args)`.

## Rationale
`pytest.raises(ValueError)` written as a statement without `with` constructs a context manager and discards it, so the test passes even when the following code does not raise. pytest.warns checks the code inside the `with` block, which must issue at least one warning of the expected class or classes; called without a callable, it only returns its checker object. In the with form, the block must raise the expected exception, or the test fails. The callable form executes the function and fails when no exception is raised, so it still checks, but the context-manager form is more readable, easier to extend and supports additional keyword arguments: in the callable form, `match` is not used by pytest.raises and is passed through to the function. Refactoring the callable form into a bare standalone call silently stops verifying exceptions.

## Example
```python
bad:  pytest.raises(ValueError)
      parse_port("x")
      excinfo = pytest.raises(ValueError, parse_port, "x")
      pytest.warns(UserWarning, load_config, "old.ini")
good: with pytest.raises(ValueError):
          parse_port("x")
      with pytest.raises(ValueError) as excinfo:
          parse_port("x")
      with pytest.warns(UserWarning):
          load_config("old.ini")
```

## Limits
The callable form still executes the function and fails when no exception is raised, so a finding on it concerns readability and keyword arguments, not a test that checks nothing. A checker assigned to a name and entered by a later `with` statement in the same test is used as a context manager and meets the rule.

## Validator
Grep the hunk for `pytest.raises(`, `pytest.warns(` and `pytest.deprecated_call(` at the start of a statement or on the right of an assignment, and for a call that passes a callable and its arguments after the expected exception or warning. Open the enclosing test function and check whether each call is the context expression of a `with` statement, or whether its assigned result is entered by a later `with` statement in the same function. Validator question: **Is a pytest.raises, pytest.warns or pytest.deprecated_call call in the hunk neither a with statement's context manager nor entered by a later with statement, or does it pass the code under test as a callable with its arguments?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-75`, severity major, `file`, `symbol`, `code` = the pytest.raises, pytest.warns or pytest.deprecated_call line and the call it is meant to check, verbatim from the diff, `fix` = the check rewritten as `with pytest.raises(ValueError):` or `with pytest.warns(UserWarning):` with the code under test indented inside the block, `rationale` = that a call outside a with statement constructs the checker and discards it, so the test passes when the code does not raise, or that the callable form passes `match` through to the function instead of using it).

## Source
- SonarSource python S9000 (SonarSource/sonar-python python-checks/src/main/resources/org/sonar/l10n/py/rules/python/S9000.html) — 'pytest.raises(ValueError) without with constructs a context manager and discards it. The test passes even when the following code does not raise:' (fetched); 'This executes bootstrap_session(df=-1) and fails when no exception is raised.' (fetched); 'The with block must raise the expected exception, or the test fails.' (fetched); 'Refactoring this form into a bare standalone call silently stops verifying exceptions.' (fetched)
- Ruff RUF061 legacy-form-pytest-raises (astral-sh/ruff crates/ruff_linter/src/rules/ruff/rules/legacy_form_pytest_raises.rs) — 'The context-manager form is more readable, easier to extend, and supports additional keyword arguments.' (fetched)
- pytest src/_pytest/raises.py §pytest.raises docstring (https://raw.githubusercontent.com/pytest-dev/pytest/main/src/_pytest/raises.py) — 'Use ``pytest.raises`` as a context manager, which will capture the exception of the given type, or any of its subclasses' (fetched); 'This is only used when ``pytest.raises`` is used as a context manager, and passed through to the function otherwise.' (fetched)
- pytest src/_pytest/recwarn.py §pytest.warns docstring and body (https://raw.githubusercontent.com/pytest-dev/pytest/main/src/_pytest/recwarn.py) — 'the code inside the ``with`` block must issue at least one warning of that class or classes.' (fetched); 'This function should be used as a context manager' (fetched); 'return WarningsChecker(expected_warning, match_expr=match, _ispytest=True)' (fetched)
- Caveat: S9000 describes pytest.raises; for pytest.warns and pytest.deprecated_call the bare-call reading rests on the pytest.warns docstring and body.

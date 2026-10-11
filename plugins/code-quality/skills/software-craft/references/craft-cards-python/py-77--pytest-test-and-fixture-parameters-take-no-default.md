---
title: A pytest test function or fixture declares no default value on a parameter, because pytest then never injects the fixture of that name
rule_id: PY-77
domain: tests
step: [test, review]
applies_to: [python, tests]
triggers: ['^\s*(async\s+)?def\s+test\w*\([^)]*=', '^\s*@pytest[.]fixture\b']
scope: hunk
check_kind: mechanical
severity_default: major
---

# A pytest test function or fixture declares no default value on a parameter, because pytest then never injects the fixture of that name

## Thesis
Every parameter of a pytest test function or fixture is declared without a default value, so that pytest can inject the fixture of the same name into it.

## Rationale
pytest's getfuncargnames returns the names of a function's mandatory arguments, the arguments that are not bound to an instance or type as in instance or class methods and that do not have default values. A default on a pytest test or fixture parameter is therefore always used: the parameter has the default value during the test regardless of whether a fixture with the same name is defined, because pytest does not inject a fixture of the same name when a default is present. The default hides a missing fixture and makes the test run with a hard-coded value instead of the intended fixture, so the test can pass while the real fixture is never applied.

## Example
```python
bad:  @pytest.fixture
      def port():
          return 8443
      def test_parse_port(port=8080):
          assert parse_port(str(port)) == port
good: def test_parse_port(port):
          assert parse_port(str(port)) == port
```

## Limits
The rule reaches the parameters of pytest test functions and fixtures; a helper function in a test module that is neither a test nor a fixture keeps its defaults. Where a parameter name is not meant as a fixture dependency, the remedy is to stop treating the name as a fixture dependency rather than to keep the default.

## Validator
Grep the hunk for a `def test…(` signature with `=` inside its parentheses and for functions decorated with `@pytest.fixture`. Open each test function or fixture at the hunk and read its whole parameter list, including parameters on continuation lines. Validator question: **Does a pytest test function or fixture in the hunk declare a default value on any of its parameters?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-77`, severity major, `file`, `symbol`, `code` = the test or fixture signature with the defaulted parameter, verbatim from the diff, `fix` = the same signature without the default, such as `def test_parse_port(port):`, `rationale` = that pytest injects a fixture only into a parameter without a default, so the test always runs with the hard-coded value).

## Source
- Ruff PT028 pytest-parameter-with-default-argument (astral-sh/ruff crates/ruff_linter/src/rules/flake8_pytest_style/rules/test_functions.rs) — 'Such a parameter will always have the default value during the test regardless of whether a fixture with the same name is defined.' (fetched)
- SonarSource python S9106 (SonarSource/sonar-python python-checks/src/main/resources/org/sonar/l10n/py/rules/python/S9106.html) — 'A default on a pytest test or fixture parameter is always used. Pytest does not inject a fixture of the same name when a default is present:' (fetched); 'That hides missing fixtures and makes the test run with a hard-coded value instead of the intended fixture.' (fetched); 'so tests can pass with hard-coded values while the real fixture is never applied' (fetched); 'This rule raises an issue when a pytest test or fixture parameter declares a default value.' (fetched); 'Remove the default so pytest can inject the parameter, or stop treating the name as a fixture dependency.' (fetched)
- pytest src/_pytest/compat.py §getfuncargnames docstring (https://raw.githubusercontent.com/pytest-dev/pytest/main/src/_pytest/compat.py) — "Return the names of a function's mandatory arguments." (fetched); "Aren't bound to an instance or type as in instance or class methods." (fetched); "Don't have default values." (fetched)

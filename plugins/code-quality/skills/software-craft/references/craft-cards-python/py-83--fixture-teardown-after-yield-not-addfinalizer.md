---
title: A pytest fixture that needs teardown yields its value and runs the teardown after the yield, keeping request.addfinalizer for a factory fixture that registers one cleanup per object it makes
rule_id: PY-83
domain: tests
step: [test, refactor, review]
applies_to: [python, tests]
triggers: ['\brequest[.]addfinalizer\(', '[.]addfinalizer\(']
scope: hunk
check_kind: mechanical
severity_default: suggestion
---

# A pytest fixture that needs teardown yields its value and runs the teardown after the yield, keeping request.addfinalizer for a factory fixture that registers one cleanup per object it makes

## Thesis
A pytest fixture with teardown yields its value and runs the cleanup after the `yield`, rather than registering the cleanup with `request.addfinalizer` and returning the value; `request.addfinalizer` stays for the factory-as-fixture pattern, where teardown is registered inside a nested factory that creates resources on demand.

## Rationale
pytest offers two ways to clean up in fixture code: sequential, through the `yield` statement, and callback-based, through `request.addfinalizer`. A yield fixture runs setup before the `yield` and teardown after it, and pytest drives it as a Python generator: it uses `addfinalizer` behind the scenes to register a function that resumes the generator, which in turn calls the teardown code. The sequential form keeps setup, the value and teardown in one linear flow and is considered the cleaner and more straightforward option; a finalizer brings a similar result with a bit more verbosity, and registering it while returning the resource scatters setup and cleanup.

## Example
```python
bad:  @pytest.fixture
      def db_conn(request):
          conn = connect()
          request.addfinalizer(conn.close)
          return conn
good: @pytest.fixture
      def db_conn():
          conn = connect()
          yield conn
          conn.close()
```

## Limits
In the factory-as-fixture pattern the fixture returns a function that creates resources on demand, and that function registers one finalizer per resource it makes; `request.addfinalizer` remains appropriate there. The two forms differ when setup fails: if a yield fixture raises an exception before yielding, pytest does not run the teardown code after its `yield`, while a finalizer runs once it has been added even if the fixture raises afterwards. A fixture that makes several state-changing steps is therefore converted by limiting each fixture to one state-changing action bundled with its own teardown code.

## Validator
Grep the hunk for `.addfinalizer(`. Open the enclosing function and decide whether it is a `@pytest.fixture` body that registers its own cleanup and then returns the resource, or a nested factory function that registers one cleanup per resource it creates. Count the state-changing steps of the fixture before proposing the fix. Validator question: **Does a pytest fixture register its teardown with `request.addfinalizer` in its own body, outside a nested factory function, and return the value?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-83`, severity suggestion, `file`, `symbol`, `code` = the `request.addfinalizer(...)` call and the fixture's `return` line, verbatim from the diff, `fix` = the Python fixture with `yield` in place of `return` and the cleanup call after the `yield`, split into one fixture per state-changing step when it makes several, `rationale` = names that the sequential yield form keeps setup, value and teardown in one linear flow).

## Source
- Ruff PT021 pytest-fixture-finalizer-callback (astral-sh/ruff crates/ruff_linter/src/rules/flake8_pytest_style/rules/fixture.rs) — '`pytest` offers two ways to perform cleanup in fixture code. The first is sequential (via the `yield` statement), the second callback-based (via `request.addfinalizer`).' (fetched)
- Ruff PT021 pytest-fixture-finalizer-callback (astral-sh/ruff crates/ruff_linter/src/rules/flake8_pytest_style/rules/fixture.rs) — 'The sequential approach is more readable and should be preferred, unless the fixture uses the "factory as fixture" pattern.' (fetched)
- SonarSource python S9080 (SonarSource/sonar-python python-checks/src/main/resources/org/sonar/l10n/py/rules/python/S9080.html) — 'Pytest fixtures can clean up either with a sequential yield (setup before yield, teardown after)' (fetched)
- SonarSource python S9080 (SonarSource/sonar-python python-checks/src/main/resources/org/sonar/l10n/py/rules/python/S9080.html) — 'The sequential style is clearer for ordinary fixtures: setup, provide the value, then tear down in one linear flow.' (fetched)
- SonarSource python S9080 (SonarSource/sonar-python python-checks/src/main/resources/org/sonar/l10n/py/rules/python/S9080.html) — 'Registering teardown with request.addfinalizer while returning the resource scatters setup and cleanup' (fetched)
- SonarSource python S9080 (SonarSource/sonar-python python-checks/src/main/resources/org/sonar/l10n/py/rules/python/S9080.html) — 'request.addfinalizer remains appropriate for the factory-as-fixture pattern, where teardown must be registered inside a nested factory that creates resources on demand.' (fetched)
- pytest doc/en/how-to/fixtures.rst §Teardown/Cleanup, 2. Adding finalizers directly (https://raw.githubusercontent.com/pytest-dev/pytest/main/doc/en/how-to/fixtures.rst) — 'While yield fixtures are considered to be the cleaner and more straightforward option, there is another choice' (fetched)
- pytest doc/en/how-to/fixtures.rst §Teardown/Cleanup, 2. Adding finalizers directly (https://raw.githubusercontent.com/pytest-dev/pytest/main/doc/en/how-to/fixtures.rst) — 'It brings a similar result as yield fixtures, but requires a bit more verbosity.' (fetched)
- pytest doc/en/how-to/fixtures.rst §Teardown/Cleanup, 2. Adding finalizers directly (https://raw.githubusercontent.com/pytest-dev/pytest/main/doc/en/how-to/fixtures.rst) — 'pytest will run that finalizer once it's been added, even if that fixture raises an exception after adding the finalizer.' (fetched)
- pytest doc/en/how-to/fixtures.rst §Teardown/Cleanup, 1. yield fixtures (https://raw.githubusercontent.com/pytest-dev/pytest/main/doc/en/how-to/fixtures.rst) — 'If a yield fixture raises an exception before yielding, pytest won't try to run the teardown code after that yield fixture's ``yield`` statement.' (fetched)
- pytest doc/en/how-to/fixtures.rst §Teardown/Cleanup (https://raw.githubusercontent.com/pytest-dev/pytest/main/doc/en/how-to/fixtures.rst) — 'yield fixtures use `addfinalizer` behind the scenes: when the fixture executes, `addfinalizer` registers a function that resumes the generator, which in turn calls the teardown code.' (fetched)
- pytest doc/en/how-to/fixtures.rst §Safe fixture structure (https://raw.githubusercontent.com/pytest-dev/pytest/main/doc/en/how-to/fixtures.rst) — 'The safest and simplest fixture structure requires limiting fixtures to only making one state-changing action each, and then bundling them together with their teardown code' (fetched)
- pytest doc/en/how-to/fixtures.rst §Factories as fixtures (https://raw.githubusercontent.com/pytest-dev/pytest/main/doc/en/how-to/fixtures.rst) — 'Instead of returning data directly, the fixture instead returns a function which generates the data.' (fetched)

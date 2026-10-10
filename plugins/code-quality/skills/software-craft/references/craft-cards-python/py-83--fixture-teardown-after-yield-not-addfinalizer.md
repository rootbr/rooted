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

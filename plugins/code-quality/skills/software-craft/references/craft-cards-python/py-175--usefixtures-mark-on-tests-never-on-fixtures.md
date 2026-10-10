---
title: A pytest.mark.usefixtures mark names at least one fixture and sits on a test function, a test class or a module's pytestmark, never on a fixture function
rule_id: PY-175
domain: tests
step: [test, review]
applies_to: [python, tests]
triggers: ['^\s*@(pytest[.])?mark[.]usefixtures\(', 'usefixtures\(\s*\)', '^\s*@(pytest[.])?fixture\b']
scope: hunk
check_kind: mechanical
severity_default: major
---

# A pytest.mark.usefixtures mark names at least one fixture and sits on a test function, a test class or a module's pytestmark, never on a fixture function

## Thesis
In Python test code run by pytest, every `pytest.mark.usefixtures` mark names at least one fixture and is applied to a test function, a test class or a module's `pytestmark`, never to a function decorated with `@pytest.fixture`; a fixture that needs another fixture declares that fixture as a parameter of its own.

## Rationale
pytest marks can only be applied to tests and have no effect on fixtures, and `pytest.mark.usefixtures` marks a test function as using the given fixture names. On a test class the mark makes the named fixture required for the execution of each test method, just as if each method declared it as an argument, and `pytestmark = pytest.mark.usefixtures(...)` specifies the same fixture usage at the test module level. Stacked on `@pytest.fixture`, the mark never had any effect, and it is a common error: users expect the named fixture to be used when the decorated fixture is invoked, when in fact the mark has no effect at all. Applying a mark to a fixture function is deprecated in pytest 7.4, from which pytest issues a warning when it encounters it, and removed in pytest 9.0, where it is an error. Test functions request the fixtures they require by declaring them as arguments, and fixtures can request and use other fixtures in the same way, declaring them as parameters, so a fixture's dependency on another fixture belongs in its own parameter list. A `@pytest.mark.usefixtures()` that is passed no argument is useless and should be removed.

## Example
```python
bad:  @pytest.mark.usefixtures("clean_database")
      @pytest.fixture
      def user(): ...
      @pytest.mark.usefixtures()
      def test_login(user): ...
good: @pytest.fixture
      def user(clean_database): ...
      def test_login(user): ...
```

## Limits
Fixtures required by all tests of a project can be listed in the `usefixtures` option of the pytest configuration file; that option carries no mark and is outside this rule. A `usefixtures` mark added from a hook can only load fixtures when applied to a test function before test setup, for example in `pytest_collection_modifyitems`; such programmatically added marks are outside the decorator and `pytestmark` spellings this rule reads. Every other mark stacked on a fixture function has no effect for the same reason, since marks can only be applied to tests; this rule covers the `usefixtures` mark only.

## Validator
Grep the hunk for `mark.usefixtures(` and for `@pytest.fixture` or a bare `@fixture` imported from pytest. For each `usefixtures` mark, open the definition it decorates and read its whole decorator list, above and below the mark, for `@pytest.fixture`, `@pytest.fixture(...)` or `@fixture`. For each fixture decorator in the hunk, read the same decorator list in the file for a `usefixtures` mark the hunk does not show. Read the argument list of every `usefixtures(` call, including one assigned to `pytestmark` or placed in a `pytestmark` list, and note a call whose argument list is empty. A mark that names at least one fixture and sits on a test function, a test class or `pytestmark` passes. Validator question: **Does a `pytest.mark.usefixtures` mark in the hunk share a decorator list with a pytest fixture decorator, or name no fixture at all?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-175`, severity major, `file`, `symbol`, `code` = the `usefixtures` decorator line together with the fixture decorator it is stacked with, or the empty `usefixtures()` call, `fix` = the fixture declaring the named fixture as a parameter with the mark deleted, as `@pytest.fixture` over `def user(clean_database):`, or the empty mark removed or given its fixture names, `rationale` = names that marks have no effect on fixtures and that pytest 9.0 makes a mark on a fixture an error, or that a `usefixtures()` without arguments is useless).

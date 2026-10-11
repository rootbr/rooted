---
title: A pytest.mark.parametrize decorator never receives an empty argvalues collection, which pytest collects and skips by default
rule_id: PY-84
domain: tests
step: [test, review]
applies_to: [python, tests]
triggers: ['parametrize\([^)]*,\s*(\[\s*\]|\(\s*\)|list\(\)|tuple\(\))\s*[,)]', '\bargvalues\s*=\s*(\[\s*\]|\(\s*\)|list\(\)|tuple\(\))']
scope: hunk
check_kind: mechanical
severity_default: major
---

# A pytest.mark.parametrize decorator never receives an empty argvalues collection, which pytest collects and skips by default

## Thesis
`@pytest.mark.parametrize` receives at least one case in its argvalues; an empty sequence such as `[]` or `()` is not passed as the values argument.

## Rationale
With an empty argvalues, parametrize has no value sets to iterate over. Under pytest's default `empty_parameter_set_mark = skip`, the test is collected and skipped with "got empty parameter set", so the suite still passes while providing no coverage for that function, and bugs in the code under test may go undetected. Unlike mistakes that cause failures, an empty parametrized collection fails silently; it typically comes from deleting or commenting out all test cases, from a test whose structure was created before its cases were added, or from a refactoring that moved or removed the cases.

## Example
```python
bad:  @pytest.mark.parametrize("payload", [])
      def test_decode(payload):
          assert decode(payload) is not None
good: @pytest.mark.parametrize("payload", [b"", b"\x00", b"ok"])
      def test_decode(payload):
          assert decode(payload) is not None
```

## Limits
A project that sets `empty_parameter_set_mark` to `fail_at_collect` gets an exception when parametrize collects an empty parameter set, and one that sets it to `xfail` gets the test marked xfail(run=False). A test whose cases are not written yet is rewritten without parametrize, with the values inlined in its body, or marked explicitly with `@pytest.mark.skip(reason=...)` on a function without parameters; removing only the decorator while keeping its parameters makes pytest treat those names as fixtures and fail at setup.

## Validator
Grep the hunk for `parametrize(` and `argvalues=`, and read the values argument. When it is a name, open its assignment in the file and check whether it is bound to an empty list, tuple, `list()` or `tuple()`. Validator question: **Does a `@pytest.mark.parametrize` decorator receive an empty argvalues collection, written in place or through a name bound to one?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-84`, severity major, `file`, `symbol`, `code` = the parametrize decorator with its empty values argument, verbatim from the diff, `fix` = the Python decorator with at least one case in its values, or the test rewritten without parametrize, `rationale` = names that under the default empty_parameter_set_mark = skip the test is collected and skipped, so it runs nothing while the suite passes).

## Source
- SonarSource python S8998 (SonarSource/sonar-python python-checks/src/main/resources/org/sonar/l10n/py/rules/python/S8998.html) — 'When @pytest.mark.parametrize has no value sets to iterate over, the test is silently skipped during collection' (fetched)
- SonarSource python S8998 (SonarSource/sonar-python python-checks/src/main/resources/org/sonar/l10n/py/rules/python/S8998.html) — 'with an empty sequence (list, tuple, or other iterable) as the values argument.' (fetched)
- SonarSource python S8998 (SonarSource/sonar-python python-checks/src/main/resources/org/sonar/l10n/py/rules/python/S8998.html) — 'Passing an empty list to @pytest.mark.parametrize collects the test but skips it with got empty parameter set for' (fetched)
- SonarSource python S8998 (SonarSource/sonar-python python-checks/src/main/resources/org/sonar/l10n/py/rules/python/S8998.html) — 'The suite still passes while providing no coverage for that function.' (fetched)
- SonarSource python S8998 (SonarSource/sonar-python python-checks/src/main/resources/org/sonar/l10n/py/rules/python/S8998.html) — 'Bugs in your code may go undetected' (fetched)
- SonarSource python S8998 (SonarSource/sonar-python python-checks/src/main/resources/org/sonar/l10n/py/rules/python/S8998.html) — 'Unlike mistakes that cause failures, an empty parametrized test collection fails silently.' (fetched)
- SonarSource python S8998 (SonarSource/sonar-python python-checks/src/main/resources/org/sonar/l10n/py/rules/python/S8998.html) — 'Accidentally deleting or commenting out all test cases' (fetched)
- SonarSource python S8998 (SonarSource/sonar-python python-checks/src/main/resources/org/sonar/l10n/py/rules/python/S8998.html) — 'Incomplete test implementation (test structure created but cases not yet added)' (fetched)
- SonarSource python S8998 (SonarSource/sonar-python python-checks/src/main/resources/org/sonar/l10n/py/rules/python/S8998.html) — 'Refactoring mistakes where test cases were moved or removed' (fetched)
- SonarSource python S8998 (SonarSource/sonar-python python-checks/src/main/resources/org/sonar/l10n/py/rules/python/S8998.html) — 'do not simply remove the decorator while keeping its parameters: pytest will treat those names as fixtures and fail at setup' (fetched)
- SonarSource python S8998 (SonarSource/sonar-python python-checks/src/main/resources/org/sonar/l10n/py/rules/python/S8998.html) — 'Instead, either add the missing cases, rewrite the test without parametrization (inline the values in the function body), or mark the test explicitly with @pytest.mark.skip' (fetched)
- pytest doc/en/reference/reference.rst §Configuration Options, empty_parameter_set_mark (https://raw.githubusercontent.com/pytest-dev/pytest/main/doc/en/reference/reference.rst) — '``skip`` skips tests with an empty parameterset' (fetched; the option defaults to skip)
- pytest doc/en/reference/reference.rst §Configuration Options, empty_parameter_set_mark (https://raw.githubusercontent.com/pytest-dev/pytest/main/doc/en/reference/reference.rst) — '``xfail`` marks tests with an empty parameterset as xfail(run=False)' (fetched)
- pytest doc/en/reference/reference.rst §Configuration Options, empty_parameter_set_mark (https://raw.githubusercontent.com/pytest-dev/pytest/main/doc/en/reference/reference.rst) — '``fail_at_collect`` raises an exception if parametrize collects an empty parameter set' (fetched)

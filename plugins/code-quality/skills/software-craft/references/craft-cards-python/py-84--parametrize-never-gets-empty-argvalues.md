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

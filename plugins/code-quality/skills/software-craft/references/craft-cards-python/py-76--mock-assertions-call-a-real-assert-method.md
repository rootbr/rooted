---
title: A unittest.mock assertion calls a real assert_* method of the mock with parentheses, never a bare attribute or a misspelled name that Mock creates on access or rejects as not a valid assertion
rule_id: PY-76
domain: tests
step: [test, review]
applies_to: [python, tests, dynamic-types]
triggers: ['[.]assert_(called|called_once|not_called|awaited|awaited_once|not_awaited)\s*$', '[.]assert_\w+\s*(#.*)?$', '[.](called_once_with|called_with|called_once|not_called|any_call|has_calls)\(']
scope: hunk
check_kind: mechanical
severity_default: major
---

# A unittest.mock assertion calls a real assert_* method of the mock with parentheses, never a bare attribute or a misspelled name that Mock creates on access or rejects as not a valid assertion

## Thesis
A statement meant as a unittest.mock assertion calls, with parentheses, an assertion method that Mock defines, such as `assert_called_once()` or `assert_called_once_with(...)`; it neither reads such a method as a bare attribute, as in `mock.assert_called_once`, nor calls a misspelled name such as `called_once_with(...)` in its place.

## Rationale
Mock and MagicMock objects create all attributes and methods as you access them, so an unknown name that Mock does not reject becomes another Mock, including a misspelled assertion method, and the test keeps passing even though the intended assertion never ran. A statement that reads `mock.assert_called_once` without parentheses is a mock attribute access that should be replaced with the method call. By default, accessing any attribute whose name starts with assert, assret, asert, aseert or assrt raises AttributeError, and passing `unsafe=True` allows access to these attributes; CPython's unittest.mock source raises the same AttributeError, naming the attribute not a valid assertion, for an assertion method's name without its `assert_` prefix, such as `called_once_with`. Where Mock rejects the misspelled name, the test fails with AttributeError instead of running the assertion; where Mock creates it, as for any name on a mock built with `unsafe=True`, the test passes without asserting.

## Example
```python
bad:  send_mock.assert_called_once
      send_mock.called_once_with("a@b.c")
good: send_mock.assert_called_once()
      send_mock.assert_called_once_with("a@b.c")
```

## Limits
A mock built with a spec raises AttributeError for any attribute not in the spec, so a misspelled name fails the test there; a bare read of a real `assert_*` method is still an attribute access in place of the call. Reading a real Mock attribute inside an `assert` statement, such as `assert mock.called`, where `called` is a boolean representing whether or not the mock object has been called, is an assertion and meets the rule.

## Validator
Grep the hunk for a statement that ends in a mock's `assert_*` name with no parentheses, and for a call of `called_once_with`, `called_with`, `called_once`, `not_called`, `any_call`, `has_calls` or another near miss of an assertion method's name. Open the test to confirm that the receiver is a Mock, a MagicMock or a mock that patch returns. Validator question: **Does a statement in the hunk read one of a mock's assertion methods without calling it, or call on a mock a name that is not one of Mock's assertion methods in place of one?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-76`, severity major, `file`, `symbol`, `code` = the mock assertion line verbatim from the diff, `fix` = the line as a call of the real assertion method, such as `send_mock.assert_called_once_with("a@b.c")`, `rationale` = that a bare attribute read or a misspelled name never runs the intended assertion: Mock creates an unknown name as another Mock, or rejects it with AttributeError).

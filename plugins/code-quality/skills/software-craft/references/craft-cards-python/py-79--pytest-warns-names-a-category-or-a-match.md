---
title: A pytest.warns check names the expected warning category and passes a non-empty match whenever it names no category or the base Warning
rule_id: PY-79
domain: tests
step: [test, review]
applies_to: [python, tests]
triggers: ['pytest[.]warns\(\s*\)', 'pytest[.]warns\(\s*Warning\s*[,)]', 'pytest[.]warns\([^)]*\bmatch\s*=\s*(""|'''')']
scope: hunk
check_kind: mechanical
severity_default: minor
---

# A pytest.warns check names the expected warning category and passes a non-empty match whenever it names no category or the base Warning

## Thesis
A `pytest.warns` check narrows the warning it expects: it names the specific category the code under test must issue, or, when it names no category or the base `Warning`, it passes a non-empty `match=` pattern for the expected message.

## Rationale
pytest.warns declares `expected_warning` with the default `Warning`, and the base Warning class is the root of the warning hierarchy and catches every warning subtype. `pytest.warns(Warning)` will catch any Warning and may catch warnings that are unrelated to the code under test, and `pytest.warns()` does the same because it defaults to Warning. For a function that should emit a DeprecationWarning, a test that only checks that a warning occurred cannot distinguish that expected DeprecationWarning from an unexpected UserWarning from a different code path or an unexpected ResourceWarning from a resource leak: all three scenarios make the test pass. A `match` pattern narrows the expectation to the message; an empty `match=""` is an error as well.

## Example
```python
bad:  with pytest.warns(Warning):
          parse(legacy=True)
      with pytest.warns(Warning, match=""):
          parse(legacy=True)
      with pytest.warns():
          parse(legacy=True)
good: with pytest.warns(DeprecationWarning, match="legacy is deprecated"):
          parse(legacy=True)
```

## Limits
A more specific category such as UserWarning or DeprecationWarning used without `match=` is outside the rule. Omitting the category while passing an effective `match=` meets the rule, because pytest.warns defaults to Warning and the message pattern narrows the expectation. In Ruff the warning names that require a `match` parameter can be configured (`lint.flake8-pytest-style.warns-require-match-for`, `lint.flake8-pytest-style.warns-extend-require-match-for`), and where the project's linter expects an expected warning as the first argument of every `pytest.warns` call, the category is named even when `match` is given.

## Validator
Grep the hunk for `pytest.warns(` calls. Read the first positional argument or `expected_warning=` and the `match=` keyword of each. Validator question: **Does a pytest.warns call in the hunk name no warning category or the base Warning, and pass no match= or an empty match string?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-79`, severity minor, `file`, `symbol`, `code` = the pytest.warns line verbatim from the diff, `fix` = the call with the specific category the code issues and a match pattern for its message, such as `pytest.warns(DeprecationWarning, match="legacy is deprecated")`, `rationale` = that Warning, the default category, catches every warning subtype, so the test passes on a warning unrelated to the code under test).

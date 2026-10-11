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

## Source
- Ruff PT030 pytest-warns-too-broad (astral-sh/ruff crates/ruff_linter/src/rules/flake8_pytest_style/rules/warns.rs) — '`pytest.warns(Warning)` will catch any `Warning` and may catch warnings that are unrelated to the code under test. To avoid this, `pytest.warns` should be called with a `match` parameter.' (fetched); 'empty string is also an error' (fetched); 'The warning names that require a `match` parameter can be configured' (fetched)
- Ruff PT029 pytest-warns-without-warning (astral-sh/ruff crates/ruff_linter/src/rules/flake8_pytest_style/rules/warns.rs) — '`pytest.warns` expects to receive an expected warning as its first argument.' (fetched)
- SonarSource python S9075 (SonarSource/sonar-python python-checks/src/main/resources/org/sonar/l10n/py/rules/python/S9075.html) — 'This is an issue when test code verifies that a warning was emitted without specifying its type and without checking its message, or when it uses the overly broad base Warning type without checking the message.' (fetched); 'The base Warning class is the root of the warning hierarchy and catches every warning subtype.' (fetched); 'All three scenarios would make the test pass' (fetched); 'More specific warning types such as UserWarning or DeprecationWarning are not covered by this rule when used without match=.' (fetched); 'Omitting the warning type while providing an effective match= is not an issue, because pytest.warns defaults to Warning and the message pattern narrows the expectation.' (fetched)
- pytest src/_pytest/recwarn.py §pytest.warns signature (https://raw.githubusercontent.com/pytest-dev/pytest/main/src/_pytest/recwarn.py) — 'expected_warning: type[Warning] | tuple[type[Warning], ...] = Warning,' (fetched)
- Caveat: PT029 also says a call without a category fails at runtime; the fetched pytest.warns signature gives the category the default Warning, so the card does not carry that statement.

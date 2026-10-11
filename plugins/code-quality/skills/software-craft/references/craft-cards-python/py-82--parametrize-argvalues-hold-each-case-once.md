---
title: The argvalues of one pytest.mark.parametrize hold each case once, with no row repeated
rule_id: PY-82
domain: tests
step: [test, review]
applies_to: [python, tests]
triggers: ['@pytest[.]mark[.]parametrize\(', '\bpytest[.]param\(']
scope: hunk
check_kind: mechanical
severity_default: minor
---

# The argvalues of one pytest.mark.parametrize hold each case once, with no row repeated

## Thesis
The argvalues collection of one `@pytest.mark.parametrize` decorator holds each case once: no entry repeats another, with entries compared as expressions (literals, names, calls and other forms), not only as literal values, because pytest runs a repeated entry as a further test item and, with `strict_parametrization_ids` at its default `false`, suffixes its duplicate ID with `0`, `1`, ... rather than reporting the repeat.

## Rationale
`@pytest.mark.parametrize` runs the decorated test once for each entry in its values collection, so a duplicate case executes the same scenario more than once. When the repeat gives two parameter sets the same ID, pytest, with `strict_parametrization_ids` at its default `false`, makes the IDs unique by adding `0`, `1`, ... to them and emits no error. Duplicate test cases are redundant: the repeat wastes CI time and usually signals a copy-paste mistake, an intended distinct case that was never updated, so coverage looks broader than it is.

## Example
```python
bad:  @pytest.mark.parametrize("port", [80, 443, 443])
      def test_connects(port):
          assert connect("localhost", port).ok
good: @pytest.mark.parametrize("port", [80, 443, 8443])
      def test_connects(port):
          assert connect("localhost", port).ok
```

## Limits
Rarely, repeated identical entries are intentional when each run exercises mutable shared state; those stay when the repeat is deliberate, and removing them may affect tests that rely on mutable global state. When the repeated entry was meant to be a different scenario, the fix replaces it with the intended distinct inputs. A project that sets `strict_parametrization_ids = true` gets an error from pytest for non-unique parameter set IDs.

## Validator
Grep the hunk for `@pytest.mark.parametrize(` and open the decorator's argvalues collection. Compare its entries as written expressions, `pytest.param(...)` wrappers included, and look for a comment or shared state in the test that shows a repeat is deliberate. Validator question: **Does one `@pytest.mark.parametrize` argvalues collection hold the same entry twice, with nothing showing that the repeat is deliberate for mutable shared state?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-82`, severity minor, `file`, `symbol`, `code` = the parametrize decorator with the repeated entries, verbatim from the diff, `fix` = the Python decorator with the repeat removed or replaced by the intended distinct case, `rationale` = names the repeated entry and that the test runs the same scenario again under a suffixed ID).

## Source
- Ruff PT014 pytest-duplicate-parametrize-test-cases (astral-sh/ruff crates/ruff_linter/src/rules/flake8_pytest_style/rules/parametrize.rs) — 'Duplicate test cases are redundant and should be removed.' (fetched)
- Ruff PT014 pytest-duplicate-parametrize-test-cases (astral-sh/ruff crates/ruff_linter/src/rules/flake8_pytest_style/rules/parametrize.rs) — 'tests that rely on mutable global state may be affected by removing duplicate test cases.' (fetched)
- SonarSource python S9078 (SonarSource/sonar-python python-checks/src/main/resources/org/sonar/l10n/py/rules/python/S9078.html) — '@pytest.mark.parametrize runs the decorated test once for each entry in its values collection. Duplicate cases therefore execute the same scenario more than once.' (fetched)
- SonarSource python S9078 (SonarSource/sonar-python python-checks/src/main/resources/org/sonar/l10n/py/rules/python/S9078.html) — 'That wastes CI time and usually signals a copy-paste mistake: an intended distinct case was never updated, so coverage looks broader than it is.' (fetched)
- SonarSource python S9078 (SonarSource/sonar-python python-checks/src/main/resources/org/sonar/l10n/py/rules/python/S9078.html) — 'Duplicates are detected by comparing the parametrize entries as expressions (literals, names, calls, and other AST forms), not only literal values.' (fetched)
- SonarSource python S9078 (SonarSource/sonar-python python-checks/src/main/resources/org/sonar/l10n/py/rules/python/S9078.html) — 'Rarely, repeated identical entries are intentional when each run exercises mutable shared state; keep those only when that is deliberate.' (fetched)
- SonarSource python S9078 (SonarSource/sonar-python python-checks/src/main/resources/org/sonar/l10n/py/rules/python/S9078.html) — 'If the repeated entry was meant to be a different scenario, replace it with the intended distinct inputs.' (fetched)
- pytest doc/en/reference/reference.rst §Configuration Options, strict_parametrization_ids (https://raw.githubusercontent.com/pytest-dev/pytest/main/doc/en/reference/reference.rst) — 'If set to ``true``, pytest emits an error if it detects non-unique parameter set IDs.' (fetched)
- pytest doc/en/reference/reference.rst §Configuration Options, strict_parametrization_ids (https://raw.githubusercontent.com/pytest-dev/pytest/main/doc/en/reference/reference.rst) — 'If not set, pytest automatically handles this by adding `0`, `1`, ... to duplicate IDs, making them unique.' (fetched; the option defaults to false)

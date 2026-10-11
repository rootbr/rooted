---
title: Code that tests the running Python version compares sys.version_info with a tuple and never parses the sys.version string or compares one version component alone
rule_id: PY-72
domain: tooling
step: [implement, review]
applies_to: [python]
triggers: ['\bsys[.]version\s*\[', '\bsys[.]version\s*(==|!=|<=|>=|<|>)', '(==|!=|<=|>=|<|>)\s*sys[.]version\b', '\bsys[.]version_info\s*\[\s*0\s*\]\s*[=!]=', '\bsys[.]version_info\s*(\[\s*1\s*\]|[.]minor)\s*(==|!=|<=|>=|<|>)', '\bsix[.]PY3\b']
scope: hunk
check_kind: mechanical
severity_default: major
---

# Code that tests the running Python version compares sys.version_info with a tuple and never parses the sys.version string or compares one version component alone

## Thesis
A check of the running interpreter's version compares `sys.version_info` with a tuple, as in `sys.version_info >= (3, 10)`, and reads a single component, when it needs one, as `sys.version_info.major` or `sys.version_info.minor` rather than as a character of a string. It never slices, indexes or string-compares `sys.version`, never tests `sys.version_info[0] == 3` or `sys.version_info[0] != 3`, never compares `sys.version_info[1]` or `sys.version_info.minor` with an integer, and uses `not six.PY2` where `six.PY3` would test for Python 3.

## Rationale
`sys.version` is a string containing the interpreter's version number plus information on the build number and compiler, and the CPython documentation says not to extract version information out of it but to use `sys.version_info`; `sys.version_info` is a tuple of the five version components, all integers except the release level, and it can be compared to other tuples without issue. A slice or index of the string breaks once a component has more than one digit: on Python 3.10 `sys.version[:3]` is `"3.1"` and `sys.version[2]` is `"1"`, and on a two-digit major version such as 10 `sys.version[0]` and `sys.version[:1]` select only the first digit. A string comparison is performed lexicographically, not semantically, so `sys.version > "3.9"` evaluates to False on Python 3.10, and a comparison with a string literal would fail once the major number reaches 10. A test of one component breaks when the major number is incremented: `sys.version_info[0] == 3`, used to verify Python 3 or greater, fails on Python 4, as does `sys.version_info[0] != 3` used to detect Python 2; a minor-number comparison such as `sys.version_info[1] < 7`, meant for 3.6 or earlier, would also hold on 4.0; and `six.PY3` evaluates to False on Python 4 and greater, where `not six.PY2` stays True.

## Example
```python
bad:  if sys.version > "3.9":
          use_new_parser()
good: if sys.version_info >= (3, 9):
          use_new_parser()
```

## Limits
Reading one component for display is outside the rule: `sys.version_info.minor` gives the whole number, so `f"{sys.version_info.minor}"` is `"10"` on Python 3.10, and `sys.version_info.major` does the same for the major number. Printing `sys.version` whole, the string the interactive interpreter displays when it starts, extracts nothing and is outside the rule. Version information that the tuple does not hold comes from the functions provided by the `platform` module.

## Validator
Grep the added lines for `sys.version` followed by `[` or by a comparison operator, a comparison operator before `sys.version`, `sys.version_info[0]` followed by `==` or `!=`, `sys.version_info[1]` or `sys.version_info.minor` followed by a comparison operator, and `six.PY3`. Confirm that the name is the `sys` module's `version` string (a `from sys import version` alias counts) and not `sys.version_info`, and that a `sys.version_info[1]` or `.minor` comparison is with an integer. Printing or logging `sys.version` whole is no finding. Validator question: **Does an added line slice, index or string-compare `sys.version`, test `sys.version_info[0]` with `==` or `!=`, compare `sys.version_info[1]` or `sys.version_info.minor` with an integer, or test `six.PY3`?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-72`, severity major, `file`, `symbol`, `code` = the version test, verbatim, `fix` = the test rewritten as a comparison of `sys.version_info` with a tuple, such as `sys.version_info >= (3, 10)`, or as `not six.PY2` for `six.PY3`, `rationale` = the version on which the test answers wrongly, such as Python 3.10 for a string comparison or Python 4 for a minor-number or `six.PY3` test).

## Source
- CPython Doc/library/sys.rst §sys.version (python/cpython Doc/library/sys.rst) — 'A string containing the version number of the Python interpreter plus additional information on the build number and compiler used.'; 'This string is displayed when the interactive interpreter is started.'; 'Do not extract version information out of it, rather, use :data:`version_info` and the functions provided by the :mod:`platform` module.' (fetched)
- CPython Doc/library/sys.rst §sys.version_info (python/cpython Doc/library/sys.rst) — 'A tuple containing the five components of the version number'; 'All values except *releaselevel* are integers' (fetched)
- Ruff YTT101 sys-version-slice3 (astral-sh/ruff crates/ruff_linter/src/rules/flake8_2020/rules/subscript.rs) — '`sys.version[:3]` will truncate the version number (e.g., `"3.10"` would become `"3.1"`)'; 'which can be compared to other tuples without issue' (fetched)
- Ruff YTT102 sys-version2 (astral-sh/ruff crates/ruff_linter/src/rules/flake8_2020/rules/subscript.rs) — '`sys.version[2]` will select the first digit of the minor number only (e.g., `"3.10"` would evaluate to `"1"`)'; 'Evaluates to "10" on Python 3.10.' (fetched)
- Ruff YTT103 sys-version-cmp-str3 (astral-sh/ruff crates/ruff_linter/src/rules/flake8_2020/rules/compare.rs) — 'the comparison will be performed lexicographically, not semantically. For example, `sys.version > "3.9"` will evaluate to `False` when using Python 3.10' (fetched)
- Ruff YTT201 sys-version-info0-eq3 (astral-sh/ruff crates/ruff_linter/src/rules/flake8_2020/rules/compare.rs) — 'Using `sys.version_info[0] == 3` to verify that the major version is Python 3 or greater will fail if the major version number is ever incremented (e.g., to Python 4).'; 'using `sys.version_info[0] != 3` to check for Python 2 will also fail if the major version number is incremented.' (fetched)
- Ruff YTT202 six-py3 (astral-sh/ruff crates/ruff_linter/src/rules/flake8_2020/rules/name_or_attribute.rs) — '`six.PY3` will evaluate to `False` on Python 4 and greater.'; 'use `not six.PY2` to validate that the current Python major version is _not_ equal to 2' (fetched)
- Ruff YTT203 sys-version-info1-cmp-int (astral-sh/ruff crates/ruff_linter/src/rules/flake8_2020/rules/compare.rs) — 'Comparisons based on the current minor version number alone can cause subtle bugs and would likely lead to unintended effects if the Python major version number were ever incremented (e.g., to Python 4).'; 'This will be printed on Python 4.0.' (fetched)
- Ruff YTT204 sys-version-info-minor-cmp-int (astral-sh/ruff crates/ruff_linter/src/rules/flake8_2020/rules/compare.rs) — 'Checks for comparisons that test `sys.version_info.minor` against an integer.' (fetched)
- Ruff YTT301 sys-version0 (astral-sh/ruff crates/ruff_linter/src/rules/flake8_2020/rules/subscript.rs) — '`sys.version[0]` will select the first digit of the major version number only (e.g., `"10.2"` would evaluate to `"1"`)'; 'use `sys.version_info.major` to access the current major version number' (fetched)
- Ruff YTT302 sys-version-cmp-str10 (astral-sh/ruff crates/ruff_linter/src/rules/flake8_2020/rules/compare.rs) — 'such that the comparison would fail if the major version number were ever incremented to Python 10 or higher' (fetched)
- Ruff YTT303 sys-version-slice1 (astral-sh/ruff crates/ruff_linter/src/rules/flake8_2020/rules/subscript.rs) — 'this will select the first digit of the major version number only (e.g., `"10.0"` would evaluate to `"1"`)' (fetched)

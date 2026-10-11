---
title: A string prefix or suffix is tested with startswith or endswith, and on Python 3.9 or later removed with removeprefix or removesuffix, rather than through a slice whose bound counts the affix's length by hand
rule_id: PY-123
domain: code
step: [implement, refactor, review]
applies_to: [python]
triggers: ['\[\s*:\s*-?\d+\s*\]\s*[!=]=\s*[rbuRBU]?["\x27]', '\[\s*-\d+\s*:\s*\]\s*[!=]=\s*[rbuRBU]?["\x27]', '["\x27]\s*[!=]=\s*[\w.]+\[\s*-?\d*\s*:\s*-?\d*\s*\]', '\[\s*-?\d*\s*:\s*-?\d*\s*\]\s+if\s+[\w.]+[.](?:startswith|endswith)\(', '^\s*[\w.]+\s*=\s*[\w.]+\[\s*(?:-?\d+\s*:|:\s*-\d+)\s*\]\s*$']
scope: hunk
check_kind: mechanical
severity_default: minor
---

# A string prefix or suffix is tested with startswith or endswith, and on Python 3.9 or later removed with removeprefix or removesuffix, rather than through a slice whose bound counts the affix's length by hand

## Thesis
A Python check whether a string starts or ends with fixed text calls `str.startswith` or `str.endswith`, not a comparison of a slice such as `s[:3] == "bar"`; where the project targets Python 3.9 or later, a prefix or suffix removed only after such a check is removed with `str.removeprefix` or `str.removesuffix`, not through a slice.

## Rationale
A slice comparison has to name the exact length of the substring it compares, so the code depends on the author counting the length of the literal. A slice bound that is wrong raises no error — a bound greater than `len(s)` is taken as `len(s)` — so a miscount leaves the comparison or the strip working on other text than the literal. `startswith` and `endswith` accept a pattern of any length and are cleaner and less error prone than slicing for a prefix or suffix check. `str.removeprefix(prefix)` returns `string[len(prefix):]` when the string starts with the prefix and a copy of the original string otherwise; `str.removesuffix(suffix)` returns `string[:-len(suffix)]` when the string ends with the suffix and that suffix is not empty, and a copy of the original string otherwise; both were introduced in Python 3.9.

## Example
```python
bad:  if url[:7] == "http://":
          scheme = "http"
      name = name[:-4] if name.endswith(".txt") else name
good: if url.startswith("http://"):
          scheme = "http"
      name = name.removesuffix(".txt")
```

## Limits
A slice that reads a field by position, rather than checking for a prefix or suffix, is outside the rule. A strip whose slice bound is `len(prefix)` behind a `startswith(prefix)` check computes what `removeprefix` returns, and one whose bound is `-len(suffix)` behind an `endswith(suffix)` check computes what `removesuffix` returns for a non-empty suffix; neither depends on a hand count, so there the finding is readability only. Below Python 3.9 the two methods do not exist, so there the guarded slice stays and only the check half of the rule applies. `removeprefix` and `removesuffix` return a copy of the original string when the affix is absent, so code that also acts on whether the affix was present keeps its `startswith` or `endswith` check and replaces only the slice.

## Validator
Grep the hunk for a slice with a numeric bound compared with `==` or `!=` against a string literal, in either order, and for a slice taken inside an `if` branch or a conditional expression guarded by `startswith` or `endswith`. For a comparison, check that the slice runs from the start or to the end of the string, which makes it a prefix or suffix check. For a guarded strip, read the project's Python floor from `requires-python` in `pyproject.toml` or Ruff's `target-version`; below 3.9, judge the comparison half only. Validator question: **Does the hunk check a fixed prefix or suffix by comparing a slice with a literal, or, in a project targeting Python 3.9 or later, strip a prefix or suffix through a slice behind a `startswith` or `endswith` check?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-123`, severity minor, `file`, `symbol`, `code` = the slice comparison or the guarded slice, verbatim, `fix` = the `s.startswith("...")` or `s.endswith("...")` check, or the `s.removeprefix("...")` or `s.removesuffix("...")` call that replaces the guarded slice, `rationale` = whether the slice bound is the affix length counted by hand, which a miscount turns into a silent mismatch, or a `len()` bound, which is readability only).

## Source
- PEP 8 Style Guide for Python Code §Programming Recommendations (https://raw.githubusercontent.com/python/peps/main/peps/pep-0008.rst) — 'instead of string slicing to check for prefixes or suffixes.' and 'startswith() and endswith() are cleaner and less error prone' (fetched)
- SonarSource/sonar-python S6659 (SonarSource/sonar-python python-checks/src/main/resources/org/sonar/l10n/py/rules/python/S6659.html) — 'allow you to check for patterns of varying lengths.' and 'With string slicing, you would need to specify the exact length of the substring to compare.' (fetched); its Error Handling paragraph says an over-long slice raises IndexError, which the CPython slice note below contradicts, so that claim is not carried.
- PEP 616 String methods to remove prefixes and suffixes §Motivating examples from the Python standard library, benefit 1 (https://raw.githubusercontent.com/python/peps/main/peps/pep-0616.rst) — 'The code will not depend on the user to count the length of a literal.' (fetched)
- Ruff FURB188 slice-to-remove-prefix-or-suffix (astral-sh/ruff crates/ruff_linter/src/rules/refurb/rules/slice_to_remove_prefix_or_suffix.rs) — 'The rule is only applied if your project targets Python 3.9 or later.' and 'introduced in Python 3.9, have the same behavior while being more readable and efficient.' (fetched)
- CPython Doc/builtins/stdtypes.rst §str.removeprefix and §str.removesuffix (https://raw.githubusercontent.com/python/cpython/main/Doc/builtins/stdtypes.rst) — 'If the string starts with the prefix string, return string[len(prefix):]. Otherwise, return a copy of the original string' and 'If the string ends with the suffix string and that suffix is not empty, return string[:-len(suffix)]. Otherwise, return a copy of the original string' (fetched)
- CPython Doc/builtins/stdtypes §Common Sequence Operations, slice note (https://docs.python.org/3/builtins/stdtypes.html) — 'If i or j is greater than len(s) ... use len(s)' (fetched)

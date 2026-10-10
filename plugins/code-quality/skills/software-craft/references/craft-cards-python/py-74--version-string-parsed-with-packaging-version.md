---
title: A package version string such as __version__ is parsed with packaging.version and never split on dots and converted with int
rule_id: PY-74
domain: tooling
step: [implement, review]
applies_to: [python]
triggers: ['\bmap\(\s*int\s*,[^)]*version', '__version__[.]split\(', '\bversion\([^)]*\)[.]split\(']
scope: hunk
check_kind: mechanical
severity_default: major
---

# A package version string such as __version__ is parsed with packaging.version and never split on dots and converted with int

## Thesis
Code that reads or compares a package's version string, such as a module's `__version__`, parses it with `packaging.version.Version` or `packaging.version.parse` and compares the parsed values; it never builds a tuple with `map(int, __version__.split("."))`.

## Rationale
A `__version__` does not always contain integral-like elements. Under the version specifiers specification a public version identifier follows the scheme `[N!]N(.N)*[{a|b|rc}N][.postN][.devN]` and is separated into up to five segments (epoch, release, pre-release, post-release and development release), and a local version identifier appends `+` and a local version label to it. Splitting such a string on dots and calling `int()` on the pieces raises `ValueError: invalid literal for int() with base 10` on a piece such as `post1`. The `packaging.version` module implements the format of that specification: `Version` and `parse` return values that compare as versions, so `parse("1.0a5") < Version("1.0")` is True, and that expose segments such as `epoch`, `release` and `pre`.

## Example
```python
bad:  if tuple(map(int, lib.__version__.split("."))) >= (2, 0):
          enable_fast_path()
good: from packaging.version import Version
      if Version(lib.__version__) >= Version("2.0"):
          enable_fast_path()
```

## Limits
The running interpreter's version needs no parsing: `sys.version_info` is already a tuple whose components, except the release level, are integers. A string that does not follow the version scheme is rejected by `Version`, which raises `InvalidVersion`, as `Version("french toast")` does.

## Validator
Grep the added lines for `map(int, ...)` over a value whose name contains `version`, for `__version__.split(`, and for `.split(` applied to the result of a `version(...)` call such as `importlib.metadata.version(...)`. Confirm that the split value is a package version string and that its pieces are converted with `int`. Validator question: **Does an added line split a package version string on dots and convert the pieces with `int`?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-74`, severity major, `file`, `symbol`, `code` = the `split(".")` and `int` expression, verbatim, `fix` = the comparison through `packaging.version`, such as `Version(lib.__version__) >= Version("2.0")` with `from packaging.version import Version`, `rationale` = a version segment `int()` fails on, such as `post1`, and the version scheme that allows it).

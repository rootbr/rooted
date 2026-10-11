---
title: New Python code that builds, inspects or acts on file-system paths uses pathlib.Path rather than the string functions of os, os.path and glob, unless measured path-handling cost calls for the string functions
rule_id: PY-38
domain: code
step: [implement, refactor, review]
applies_to: [python]
triggers: ['\bos[.]path[.](join|exists|isfile|isdir|basename|dirname|splitext|abspath|getsize|expanduser)\(', '\bos[.](makedirs|mkdir|remove|unlink|rename|replace|rmdir|listdir|getcwd|stat)\(', '\bglob[.](glob|iglob)\(']
scope: hunk
check_kind: mechanical
severity_default: suggestion
---

# New Python code that builds, inspects or acts on file-system paths uses pathlib.Path rather than the string functions of os, os.path and glob, unless measured path-handling cost calls for the string functions

## Thesis
New code that joins, inspects, lists, creates or removes file-system paths uses pathlib.Path, its / operator and its methods (resolve, exists, mkdir, unlink, iterdir, glob, parent, name, suffix) wherever a Path method corresponds to the os, os.path or glob function, unless a measurement shows the path handling to be a cost the string functions reduce, or the code handles paths as plain strings by design.

## Rationale
Python's standard library carries two path APIs: the lower-level, string-based functions of os.path, os and glob, and the object-oriented pathlib, whose documentation keeps a table mapping os functions to their Path equivalents. pathlib offers a high-level API for path manipulation, as compared to the lower-level API offered by os.path; when possible, Path methods and the / operator can improve readability over the os.path counterparts, so Path(root) / "folder" / "file.py" replaces nested os.path.join calls, and pathlib can improve the type safety of the code as well. Within pathlib, a reader unsure which of its classes is right for the task is pointed to Path, which instantiates a concrete path for the platform the code runs on.

## Example
```python
bad:  config_path = os.path.join(base_dir, "config", "app.toml")
      os.makedirs(os.path.dirname(config_path), exist_ok=True)
      backups = glob.glob(os.path.join(base_dir, "*.bak"))
good: config_path = Path(base_dir) / "config" / "app.toml"
      config_path.parent.mkdir(parents=True, exist_ok=True)
      backups = list(Path(base_dir).glob("*.bak"))
```

## Limits
The two sides separate on cost and on string handling. While pathlib can improve readability and type safety, it can be less performant than the lower-level alternatives that work directly with strings, especially on older versions of Python, and the pathlib documentation keeps os.path for low-level path manipulation on strings; path handling that a measurement shows to be a hot spot, and code that treats paths as plain strings by design, keep the string functions, while other new path code uses pathlib. The replacements are not exact equivalents: Path.resolve() resolves symlinks while os.path.abspath() does not, and it returns a Path object where abspath returns str or bytes, a change in return type that can break code using the value; glob.glob() excludes hidden files by default and builds a list, while Path.glob() includes hidden files by default and returns a lazy iterator. Working os.path code that a change leaves alone is outside the rule, which covers new code.

## Validator
Grep the added lines of the hunk for os.path functions (join, exists, isfile, isdir, basename, dirname, splitext, abspath, getsize, expanduser), the os file functions (makedirs, mkdir, remove, unlink, rename, replace, rmdir, listdir, getcwd, stat) and glob.glob or glob.iglob. Open the enclosing function to see whether the value is a file-system path and whether the surrounding code already holds Path objects or works on strings by design. Skip a call in code a profile or benchmark in the change names as a path-handling hot spot, and a call whose Path counterpart would change behaviour the code relies on (symlink resolution, hidden files, a str return). Validator question: **Does new code call an os, os.path or glob function on a file-system path where a Path method or operator corresponds and neither a measured cost nor deliberate string handling is shown?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-38`, severity suggestion, `file`, `symbol`, `code` = the os, os.path or glob call, quoted verbatim from the diff, `fix` = the Path form, e.g. `Path(base_dir) / "config" / "app.toml"` or `config_path.exists()`, with a note where resolve or glob behaves differently, `rationale` = pathlib's high-level API can improve readability and type safety over the string functions of os.path, os and glob).

## Source
- Ruff PTH118 os-path-join (astral-sh/ruff crates/ruff_linter/src/rules/flake8_use_pathlib/violations.rs) — 'When possible, using `Path` object methods such as `Path.joinpath()` or the `/` operator can improve readability over the `os.path` module's counterparts' (fetched)
- Ruff PTH118 os-path-join (astral-sh/ruff crates/ruff_linter/src/rules/flake8_use_pathlib/violations.rs) — 'While using `pathlib` can improve the readability and type safety of your code, it can be less performant than the lower-level alternatives that work directly with strings, especially on older versions of Python.' (fetched)
- Ruff PTH118 os-path-join (astral-sh/ruff crates/ruff_linter/src/rules/flake8_use_pathlib/violations.rs) — 'Path(ROOT_PATH) / "folder" / "file.py"' (fetched)
- Ruff PTH110 os-path-exists (astral-sh/ruff crates/ruff_linter/src/rules/flake8_use_pathlib/rules/os_path_exists.rs) — '`pathlib` offers a high-level API for path manipulation, as compared to the lower-level API offered by `os.path`.' (fetched)
- Ruff PTH100 os-path-abspath (astral-sh/ruff crates/ruff_linter/src/rules/flake8_use_pathlib/rules/os_path_abspath.rs) — 'This rule's fix is always marked as unsafe because `Path.resolve()` resolves symlinks, while `os.path.abspath()` does not.' (fetched)
- Ruff PTH100 os-path-abspath (astral-sh/ruff crates/ruff_linter/src/rules/flake8_use_pathlib/rules/os_path_abspath.rs) — '`os.path.abspath()` returns `str` or `bytes` (`AnyStr`), while `Path.resolve()` returns a `Path` object.' (fetched)
- Ruff PTH100 os-path-abspath (astral-sh/ruff crates/ruff_linter/src/rules/flake8_use_pathlib/rules/os_path_abspath.rs) — 'This change in return type can break code that uses the return value.' (fetched)
- Ruff PTH207 glob (astral-sh/ruff crates/ruff_linter/src/rules/flake8_use_pathlib/rules/glob_rule.rs) — 'as compared to the lower-level API offered by `os` and `glob`' (fetched)
- Ruff PTH207 glob (astral-sh/ruff crates/ruff_linter/src/rules/flake8_use_pathlib/rules/glob_rule.rs) — 'Note that `glob.glob()` and `Path.glob()` are not exact equivalents' (fetched)
- Ruff PTH207 glob (astral-sh/ruff crates/ruff_linter/src/rules/flake8_use_pathlib/rules/glob_rule.rs) — 'Under the hood, `glob.glob()` simply converts the iterator to a list.' (fetched)
- Ruff PTH207 glob (astral-sh/ruff crates/ruff_linter/src/rules/flake8_use_pathlib/rules/glob_rule.rs) — '`Path.glob()` returns a lazy iterator.' (fetched)
- Ruff PTH207 glob (astral-sh/ruff crates/ruff_linter/src/rules/flake8_use_pathlib/rules/glob_rule.rs) — 'Hidden files are excluded by default.' (fetched)
- Ruff PTH207 glob (astral-sh/ruff crates/ruff_linter/src/rules/flake8_use_pathlib/rules/glob_rule.rs) — 'Includes hidden files by default.' (fetched)
- CPython Doc/library/pathlib.rst §introduction (https://raw.githubusercontent.com/python/cpython/main/Doc/library/pathlib.rst) — 'is most likely what you need' (fetched)
- CPython Doc/library/pathlib.rst §introduction (https://raw.githubusercontent.com/python/cpython/main/Doc/library/pathlib.rst) — 'The pathlib module -- object-oriented filesystem paths.' (fetched)
- CPython Doc/library/pathlib.rst §introduction (https://raw.githubusercontent.com/python/cpython/main/Doc/library/pathlib.rst) — 'For low-level path manipulation on strings, you can also use the' (fetched)
- CPython Doc/library/pathlib.rst §Corresponding tools (https://raw.githubusercontent.com/python/cpython/main/Doc/library/pathlib.rst) — 'Below is a table mapping various :mod:`os` functions to their corresponding' (fetched)

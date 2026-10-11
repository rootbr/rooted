---
title: Program code ends the process with sys.exit and never with the exit or quit builtins that the site module adds for the interactive shell
rule_id: PY-49
domain: design
step: [implement, review]
applies_to: [python]
triggers: ['(?<![\w.])(exit|quit)\s*\(', '^\s*(exit|quit)\s*\(']
scope: hunk
check_kind: mechanical
severity_default: minor
---

# Program code ends the process with sys.exit and never with the exit or quit builtins that the site module adds for the interactive shell

## Thesis
Python program and library code that ends the process calls `sys.exit()`, and leaves `exit()` and `quit()`, which the `site` module adds to the built-in namespace, to the interactive interpreter shell.

## Rationale
The `site` module, imported automatically during startup except when the `-S` command-line option is given, adds `exit` and `quit` to the built-in namespace; they are useful for the interactive interpreter shell and should not be used in programs. Because `site` is not guaranteed to be imported, calling them may result in a `NameError` at runtime, whereas `sys.exit` does not rely on the site module being available: the `sys` module is guaranteed to exist in all contexts.

## Example
```python
bad:  if __name__ == "__main__":
          main()
          exit(0)
good: import sys
      if __name__ == "__main__":
          main()
          sys.exit(0)
```

## Limits
`exit()` and `quit()` are useful in the interactive interpreter shell. The replacement by `sys.exit` is not a safe mechanical fix, as behavior can change in two ways: where `site` is not imported (`python -S`) the original code would raise a `NameError` while the fixed code would execute normally, and `site.exit` treats a tuple argument as a regular object and always returns exit code 1, while `sys.exit` interprets the tuple's contents, so an empty tuple results in exit code 0 and `(2,)` in exit code 2.

## Validator
Grep the hunk for a call `exit(` or `quit(` that is not an attribute call such as `parser.exit()` or `self.quit()`. Open the file and confirm the name is the builtin: the module neither defines nor imports its own `exit` or `quit`, and the file is program or library code rather than a transcript of an interactive session. Where the argument is a tuple, carry the exit code it yields under `site.exit` into the fix. Validator question: **Does program or library code in the hunk call the builtin `exit()` or `quit()`?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-49`, severity minor, `file`, `symbol`, `code` = the `exit(...)` or `quit(...)` call, verbatim, `fix` = `import sys` at the top of the module and `sys.exit(...)` with the same exit code, `rationale` = `exit` and `quit` come from the `site` module, which `-S` leaves unimported, while `sys` is always available).

## Source
- CPython Doc/builtins/constants.rst §Constants added by the site module (python/cpython Doc/builtins/constants.rst) — 'which is imported automatically during startup, except if the :option:`-S` command-line option is given) adds several constants to the built-in namespace.' (fetched)
- CPython Doc/builtins/constants.rst §Constants added by the site module (python/cpython Doc/builtins/constants.rst) — 'They are useful for the interactive interpreter shell and should not be used in programs.' (fetched)
- Ruff PLR1722 sys-exit-alias (astral-sh/ruff crates/ruff_linter/src/rules/pylint/rules/sys_exit_alias.rs) — 'However, it is not _guaranteed_ to be imported, and so using these functions may result in a `NameError` at runtime.' (fetched)
- Ruff PLR1722 sys-exit-alias (astral-sh/ruff crates/ruff_linter/src/rules/pylint/rules/sys_exit_alias.rs) — 'Prefer `sys.exit()`, as the `sys` module is guaranteed to exist in all contexts.' (fetched)
- Ruff PLR1722 sys-exit-alias (astral-sh/ruff crates/ruff_linter/src/rules/pylint/rules/sys_exit_alias.rs) — 'the original code would raise a `NameError`, while the fixed code would execute normally.' (fetched)
- Ruff PLR1722 sys-exit-alias (astral-sh/ruff crates/ruff_linter/src/rules/pylint/rules/sys_exit_alias.rs) — '`site.exit` treats tuples as regular objects and always returns exit code 1, while `sys.exit` interprets tuple contents to determine the exit code: an empty tuple () results in exit code 0, and a single-element tuple like (2,) uses that element' (fetched)
- Pylint consider-using-sys-exit (R1722) (pylint-dev/pylint, the R1722 message description, cached in the harvest index beside doc/data/messages/c/consider-using-sys-exit/bad.py) — 'does not rely on the site module being available' (fetched)

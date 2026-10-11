---
title: A Python handler that calls add_note() on the exception it caught re-raises or otherwise uses that exception, and never lets the noted exception drop
rule_id: PY-172
domain: errors
step: [handle-errors, review]
applies_to: [python, exceptions]
triggers: ['\b\w+[.]add_note\(', '__notes__']
scope: hunk
check_kind: mechanical
severity_default: major
---

# A Python handler that calls add_note() on the exception it caught re-raises or otherwise uses that exception, and never lets the noted exception drop

## Thesis
A Python `except` handler that calls `add_note()` on the exception it caught re-raises that exception or otherwise uses it, by raising it, chaining it, returning, storing or grouping it, before the handler ends.

## Rationale
`BaseException.add_note()` (Python 3.11 and later) adds a string to the exception's notes, which appear in the standard traceback after the exception string; it exists because further information may be available when the exception is caught and re-raised, or included in an `ExceptionGroup`. The notes are rendered with their exception: the standard traceback rendering includes all notes, in the order they were added, after the exception. A caught exception that receives a note and is then not used points to a forgotten `raise`.

## Example
```python
bad:  try:
          config = load(path)
      except OSError as exc:
          exc.add_note(f"while loading {path}")
good: try:
          config = load(path)
      except OSError as exc:
          exc.add_note(f"while loading {path}")
          raise
```

## Limits
A handler that passes the noted exception on conforms: it re-raises it with a bare `raise` or `raise exc`, raises a new exception `from` it, returns or stores it, or collects it into an `ExceptionGroup`. The rule reaches the caught exception; a note added to a new exception that the handler builds is outside it.

## Validator
Grep the hunk for `.add_note(`. Open the enclosing `except ... as name:` handler and check that the receiver of `add_note()` is the name the handler binds. Trace that name to the end of the handler: a `raise` (bare, `raise name` or `raise ... from name`), a `return`, an assignment or `append`, a call that receives it, or an `ExceptionGroup` built with it counts as use. Validator question: **Does the handler call `add_note()` on the exception it caught and then end without raising or otherwise using that exception?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-172`, severity major, `file`, `symbol`, `code` = the handler's `except` line and its `add_note(...)` call, `fix` = the same handler with a bare `raise` after the `add_note()` call, `rationale` = the handler ends without using the noted exception, so the exception and its note are dropped).

## Source
- flake8-bugbear B040 (PyCQA/flake8-bugbear README.rst) — 'Caught exception with call to ``add_note`` not used. Did you forget to ``raise`` it?' (fetched)
- CPython Doc/builtins/exceptions.rst §Base classes, BaseException.add_note (https://raw.githubusercontent.com/python/cpython/main/Doc/builtins/exceptions.rst) — 'notes which appear in the standard traceback after the exception string.' (fetched)
- CPython Doc/tutorial/errors.rst §Enriching Exceptions with Notes (https://raw.githubusercontent.com/python/cpython/main/Doc/tutorial/errors.rst) — 'There are cases where it is useful to add information after the exception was caught.' (fetched)
- CPython Doc/tutorial/errors.rst §Enriching Exceptions with Notes (https://raw.githubusercontent.com/python/cpython/main/Doc/tutorial/errors.rst) — 'The standard traceback rendering includes all notes, in the order they were added, after the exception.' (fetched)
- PEP 678 §Abstract (https://raw.githubusercontent.com/python/peps/main/peps/pep-0678.rst) — 'Because further information may be available when the exception is caught and re-raised, or included in an ``ExceptionGroup``, this PEP proposes to add ``BaseException.add_note(note)``' (fetched)
- PEP 678 header (https://raw.githubusercontent.com/python/peps/main/peps/pep-0678.rst) — 'Python-Version: 3.11' (fetched)

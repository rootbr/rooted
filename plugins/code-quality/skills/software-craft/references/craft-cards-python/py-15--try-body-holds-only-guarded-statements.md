---
title: A Python try block holds only the statements whose exceptions its handlers are written for, and code meant to run only when they raised nothing goes in the else clause or after the try statement
rule_id: PY-15
domain: errors
step: [handle-errors, refactor, review]
applies_to: [python, exceptions]
triggers: ['^\s*try\s*:\s*(#.*)?$', '^\s*except\*?\b.*:\s*(#.*)?$']
scope: hunk
check_kind: semantic
severity_default: minor
---

# A Python try block holds only the statements whose exceptions its handlers are written for, and code meant to run only when they raised nothing goes in the else clause or after the try statement

## Thesis
A `try` block holds the minimum code whose exceptions its `except` clauses are written to handle. A statement that should run only when that code raised nothing, a success-path `return` included, goes in the try statement's `else` clause or after the statement, and a statement that only prepares the guarded code goes before it.

## Rationale
When an exception occurs anywhere in the `try` suite, the search for a handler starts at its `except` clauses, so a statement added to the suite for the success path brings its own failures under the handler: the handler accidentally catches an exception that was not raised by the code it protects, and the bug is masked. Python gives that code a place inside the same statement: the `else` clause is executed if control leaves the `try` suite, no exception was raised and no `return`, `continue` or `break` was executed, and exceptions raised in the `else` clause are not handled by the preceding `except` clauses. A `return` inside the `try` block may also be overridden by control flow in `except` and `finally` blocks, or unintentionally suppress an exception. A try clause with many statements makes unexpected exceptions harder to detect and debug; narrowing it to the code that may raise the exceptions the handlers anticipate, with the other statements before or after it, avoids that.

## Example
```python
bad:  try:
          config = json.loads(text)
          return build_app(config)
      except json.JSONDecodeError:
          return None
good: try:
          config = json.loads(text)
      except json.JSONDecodeError:
          return None
      else: return build_app(config)
```

## Limits
Statement counts are proxies for this defect: a linter's default allows up to 5 statements in a try clause, while its reference implementation uses a default that corresponds to 1. The finder judges which statements the handlers are written for, and a `try` block whose every statement may raise the exceptions its handlers anticipate is correct at any length. Code after the try statement runs whenever the statement completes, after a handler that falls through as well; code that must run only when the `try` suite raised nothing belongs in the `else` clause.

## Validator
Grep the hunk for `try:` headers and open each whole try statement with its `except` clauses. For every statement in the `try` suite, decide whether it, or a call it makes, is the code the handlers' exception types are written for. Mark each other statement: a success-path `return`, a call that consumes the guarded result, setup that cannot raise the handled types. Validator question: **Does the try suite hold a statement that the except clauses are not written for and that belongs in the else clause, after the try statement or before it?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-15`, severity minor, `file`, `symbol`, `code` = the `try` suite and its `except` header quoted verbatim from the diff, `fix` = the suite reduced to the guarded statements with the rest moved into `else:`, after the try statement or before it, `rationale` = the handler also catches exceptions of its type raised by statements it was not written for and masks a bug there).

## Source
- PEP 8 §Programming Recommendations (python/peps peps/pep-0008.rst) — 'Additionally, for all try/except clauses, limit the ``try`` clause to the absolute minimum amount of code necessary. Again, this avoids masking bugs' (fetched)
- CPython Doc/tutorial/errors.rst §Handling Exceptions (python/cpython Doc/tutorial/errors.rst) — 'The use of the :keyword:`!else` clause is better than adding additional code to the :keyword:`try` clause because it avoids accidentally catching an exception that wasn't raised by the code being protected by the :keyword:`!try` ... :keyword:`!except` statement.' (fetched)
- CPython documentation reference/compound_stmts §except clause, §else clause (https://docs.python.org/3/reference/compound_stmts.html) — 'When an exception occurs in the try suite, a search for an exception handler is started. ... The optional else clause is executed if the control flow leaves the try suite, no exception was raised, and no return, continue, or break statement was executed. Exceptions in the else clause are not handled by the preceding except clauses.' (fetched)
- Ruff TRY300 try-consider-else (astral-sh/ruff crates/ruff_linter/src/rules/tryceratops/rules/try_consider_else.rs) — 'The `try`-`except` statement has an `else` clause for code that should run _only_ if no exceptions were raised. Returns in `try` blocks may exhibit confusing or unwanted behavior, such as being overridden by control flow in `except` and `finally` blocks, or unintentionally suppressing an exception.' (fetched)
- Ruff PLW0717 too-many-statements-in-try-clause (astral-sh/ruff crates/ruff_linter/src/rules/pylint/rules/too_many_try_statements.rs) — 'By default, this rule allows up to 5 statements ... Try clauses with many statements make unexpected exceptions harder to detect and debug. Instead, consider narrowing the try clause to only encompass code that may raise exceptions you can anticipate or know about, moving all other statements either before or after the try clause, or factoring out a helper function. ... uses a different default setting. To replicate it exactly, set `lint.pylint.max-statements-in-try` to 1.' (fetched) — a preview rule; the default of 1 is that of the reference implementation.
- Pylint too-many-try-statements (W0717), message description (pylint-dev/pylint pylint/extensions/broad_try_clause.py, W0717; harvest items.jsonl) — 'Try clause contains too many statements.' (fetched)

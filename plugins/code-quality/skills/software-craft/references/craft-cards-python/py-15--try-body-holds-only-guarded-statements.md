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

---
title: A Python @contextmanager generator whose code after yield must run on exit puts the yield in a try whose finally runs that code
rule_id: PY-16
domain: errors
step: [implement, handle-errors, review]
applies_to: [python, exceptions]
triggers: ['^\s*@(contextlib[.])?contextmanager\b', '^\s*([\w, ]+=\s*)?yield\b']
scope: file
check_kind: mechanical
severity_default: major
---

# A Python @contextmanager generator whose code after yield must run on exit puts the yield in a try whose finally runs that code

## Thesis
In a generator decorated with `contextlib.contextmanager`, code after the `yield` that must run when the `with` block exits, such as closing a file or a connection or releasing a lock, sits in the `finally` of a `try` around the `yield`, or the resource is acquired by a nested `with` that encloses the `yield`.

## Rationale
`contextlib.contextmanager` executes the block nested in the `with` statement at the point where the generator yields, and resumes the generator after the block is exited. If an unhandled exception occurs in the block, it is reraised inside the generator at the point where the yield occurred, so code after an unprotected `yield` never executes when the `with` block raises. The same code is also skipped when the generator is closed early, for example when a consumer stops iterating before the generator is exhausted, and in those cases resources such as files, locks or connections can stay open. Wrapping the `yield` in `try`/`finally` makes the cleanup always run; nesting the resource acquisition in a `with` is the other repair.

## Example
```python
bad:  @contextmanager
      def opened(path):
          handle = open(path, "w")
          yield handle
          handle.close()
good:     handle = open(path, "w")
          try:
              yield handle
          finally:
              handle.close()
```

## Limits
Statements after the `yield` that are not cleanup, such as optional logging that is safe to skip, are outside the rule, and cleanup already guaranteed by a nested `with` or by an enclosing `try`/`finally` satisfies it. A `try`/`except` around the `yield` that traps the exception merely to log it or to perform some action, rather than to suppress it entirely, reraises that exception; otherwise the context manager indicates to the `with` statement that the exception has been handled, and execution resumes with the statement after the `with` statement.

## Validator
Grep the hunk for `@contextmanager` or `@contextlib.contextmanager` and for `yield`. Open each decorated generator in the file. For each `yield`, list the statements that follow it and pick those that release a resource or restore state the `with` block borrowed: `close()`, `release()`, `unlock()`, `rollback()`, a restored setting. Trace whether the `yield` sits inside a `try` whose `finally` runs that statement, or inside a `with` that acquired the resource. Validator question: **Does a @contextmanager generator release a resource after a yield that is neither inside a try whose finally runs the release nor inside a with that holds the resource?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-16`, severity major, `file`, `symbol`, `code` = the `yield` line and the release statement after it, `fix` = `try: yield handle` with the release in `finally: handle.close()`, or the resource acquired by `with open(path) as handle:` around the `yield`, `rationale` = an exception from the `with` block is reraised at the `yield`, so the release after it is skipped and the resource stays open).

## Source
- CPython Doc/library/contextlib.rst §contextmanager (python/cpython Doc/library/contextlib.rst) — 'At the point where the generator yields, the block nested in the :keyword:`with` statement is executed. The generator is then resumed after the block is exited.' (fetched)
- CPython Doc/library/contextlib.rst §contextmanager (python/cpython Doc/library/contextlib.rst) — 'If an unhandled exception occurs in the block, it is reraised inside the generator at the point where the yield occurred.' (fetched)
- CPython Doc/library/contextlib.rst §contextmanager (python/cpython Doc/library/contextlib.rst) — 'If an exception is trapped merely in order to log it or to perform some action (rather than to suppress it entirely), the generator must reraise that exception.' (fetched)
- CPython Doc/library/contextlib.rst §contextmanager (python/cpython Doc/library/contextlib.rst) — 'Otherwise the generator context manager will indicate to the :keyword:`!with` statement that the exception has been handled, and execution will resume with the statement immediately following the :keyword:`!with` statement.' (fetched)
- Ruff RUF075 fallible-context-manager (astral-sh/ruff crates/ruff_linter/src/rules/ruff/rules/fallible_context_manager.rs) — 'However, if an exception is raised inside the `with` block, code after an unprotected `yield` will never execute.' (fetched); a preview rule.
- SonarSource python S9152 (SonarSource/sonar-python python-checks/src/main/resources/org/sonar/l10n/py/rules/python/S9152.html) — 'the generator is closed early, for example when a consumer stops iterating before the generator is exhausted' (fetched)
- SonarSource python S9152 (SonarSource/sonar-python python-checks/src/main/resources/org/sonar/l10n/py/rules/python/S9152.html) — 'In those cases, resources such as files, locks, or connections can stay open.' (fetched)
- SonarSource python S9152 (SonarSource/sonar-python python-checks/src/main/resources/org/sonar/l10n/py/rules/python/S9152.html) — 'Wrap the yield in try/finally so cleanup always runs, or nest resource acquisition in a with' (fetched)
- SonarSource python S9152 (SonarSource/sonar-python python-checks/src/main/resources/org/sonar/l10n/py/rules/python/S9152.html) — 'If statements after yield are not cleanup (for example optional logging that is safe to skip), or cleanup is already guaranteed by a nested with or an enclosing try/finally the analyzer failed to see, treat that as a false positive.' (fetched)

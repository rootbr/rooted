---
title: A Python handler that catches BaseException, as a bare except or except BaseException or except SystemExit, re-raises it after cleanup or logs the traceback, and a catch-all for program errors writes except Exception
rule_id: PY-12
domain: errors
step: [handle-errors, review]
applies_to: [python, exceptions]
triggers: ['^\s*except\s*:', '^\s*except\*?\b[^:]*\b(BaseException|SystemExit|KeyboardInterrupt)\b']
scope: hunk
check_kind: mechanical
severity_default: major
---

# A Python handler that catches BaseException, as a bare except or except BaseException or except SystemExit, re-raises it after cleanup or logs the traceback, and a catch-all for program errors writes except Exception

## Thesis
A handler whose clause reaches `BaseException` (a bare `except:`, which is equivalent to `except BaseException:`, an `except BaseException`, or an `except` naming `SystemExit` or `KeyboardInterrupt`) either lets the exception propagate with `raise` after its cleanup or prints or logs the traceback; a handler meant to catch all exceptions that signal program errors writes `except Exception:` instead.

## Rationale
`BaseException` includes `KeyboardInterrupt`, `SystemExit` and `Exception`. Python derives `SystemExit`, raised by `sys.exit()`, and `KeyboardInterrupt`, raised when the user hits the interrupt key, from `BaseException` instead of `Exception`, so that code that catches `Exception` does not accidentally catch them and they propagate up and make the interpreter exit. A bare `except:` catches both, which makes a program harder to interrupt with Control-C and can disguise other problems, and a handler that catches them without re-raising may prevent the program from exiting as expected. `except Exception:` catches all exceptions that signal program errors and leaves those two to propagate. A handler that does reach `BaseException` has two accepted uses: one that does its cleanup and then lets the exception propagate upwards with `raise`, which also lets the interpreter exit as expected, and one that prints or logs the traceback, so that at least the user is aware an error has occurred.

## Example
```python
bad:  for job in jobs:
          try:
              job.run()
          except:
              failures += 1
good: for job in jobs:
          try:
              job.run()
          except Exception:
              logger.exception("job %s failed", job)
```

## Limits
The sources split on a handler that prints or logs the traceback and does not re-raise. One position limits a bare `except` to that case and to cleanup followed by `raise`, and does not flag a broad handler that re-raises or that logs with `exc_info` enabled; the stricter position asks that the exception be raised again whenever a more specific class cannot be caught, and reports an `except BaseException:` with no `raise` at the top level of its block. The separating condition is the printed or logged traceback: this card does not report a handler reaching `BaseException` that re-raises or prints or logs the traceback, while under the strict reading the logging handler re-raises as well. A third position reports every bare `except:` whatever its body, one form of it asking for `except Exception:` or, when catching everything is meant, an explicit `except BaseException:`; the spelling of the clause belongs to that position, and this card judges what the handler does. Where cleanup is the handler's only purpose, `try...finally` can be a better way to write it.

## Validator
Grep the hunk for `except:` and for `except` or `except*` clauses that name `BaseException`, `SystemExit` or `KeyboardInterrupt`, alone or in a tuple. Open each such handler's body and look at its top level for a `raise` (bare, of the bound name or of another exception) or a `sys.exit()` call, which raises `SystemExit`, and for a call that prints or logs the traceback: `logger.exception(...)`, a logging call with `exc_info` enabled, `traceback.print_exc()`. Validator question: **Does a handler that reaches BaseException finish without a top-level `raise` and without printing or logging the traceback?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-12`, severity major, `file`, `symbol`, `code` = the `except` header and its handler body quoted verbatim from the diff, `fix` = `except Exception:` with the handling kept, or the `BaseException` handler ending in `raise` after its cleanup, `rationale` = the handler catches `SystemExit` and `KeyboardInterrupt` and may keep `sys.exit()` and Control-C from stopping the program).

## Source
- PEP 8 §Programming Recommendations (python/peps peps/pep-0008.rst) — 'A bare ``except:`` clause will catch SystemExit and KeyboardInterrupt exceptions, making it harder to interrupt a program with Control-C, and can disguise other problems. If you want to catch all exceptions that signal program errors, use ``except Exception:`` (bare except is equivalent to ``except BaseException:``). A good rule of thumb is to limit use of bare 'except' clauses to two cases: 1. If the exception handler will be printing out or logging the traceback; at least the user will be aware that an error has occurred. 2. If the code needs to do some cleanup work, but then lets the exception propagate upwards with ``raise``. ``try...finally`` can be a better way to handle this case.' (fetched)
- CPython documentation library/exceptions §SystemExit, §KeyboardInterrupt (https://docs.python.org/3/library/exceptions.html) — 'This exception is raised by the sys.exit() function. It inherits from BaseException instead of Exception so that it is not accidentally caught by code that catches Exception. This allows the exception to properly propagate up and cause the interpreter to exit. ... Raised when the user hits the interrupt key ... The exception inherits from BaseException so as to not be accidentally caught by code that catches Exception and thus prevent the interpreter from exiting.' (fetched)
- Ruff E722 bare-except (astral-sh/ruff crates/ruff_linter/src/rules/pycodestyle/rules/bare_except.rs) — 'A bare `except` catches `BaseException` which includes `KeyboardInterrupt`, `SystemExit`, `Exception`, and others. Catching `BaseException` can make it hard to interrupt the program (e.g., with Ctrl-C) and can disguise other problems.' (fetched)
- Pylint bare-except (W0702) (pylint-dev/pylint doc/data/messages/b/bare-except/details.rst) — 'A good rule of thumb is to limit use of bare ‘except’ clauses to two cases: - If the exception handler will be printing out or logging the traceback; at least the user will be aware that an error has occurred. - If the code needs to do some cleanup work, but then lets the exception propagate upwards with raise.' (fetched)
- flake8-bugbear B001 (PyCQA/flake8-bugbear README.rst) — 'Do not use bare ``except:``, it also catches unexpected events like memory errors, interrupts, system exit, and so on. Prefer ``except Exception:``. If you're sure what you're doing, be explicit and write ``except BaseException:``.' (fetched)
- flake8-bugbear B036 (PyCQA/flake8-bugbear README.rst) — 'Found ``except BaseException:`` without re-raising (no ``raise`` in the top-level of the ``except`` block). This catches all kinds of things (Exception, SystemExit, KeyboardInterrupt...) and may prevent a program from exiting as expected.' (fetched)
- SonarSource python S5754 (SonarSource/sonar-python python-checks/src/main/resources/org/sonar/l10n/py/rules/python/S5754.html) — 'It should, however, be raised again to allow the interpreter to exit as expected. ... It is recommended to catch instead a more specific exception. If it is not possible, the exception should be raised again.' (fetched)
- Ruff BLE001 blind-except (astral-sh/ruff crates/ruff_linter/src/rules/flake8_blind_except/rules/blind_except.rs) — 'Overly broad `except` clauses can lead to unexpected behavior, such as catching `KeyboardInterrupt` or `SystemExit` exceptions that prevent the user from exiting the program. ... Exceptions that are re-raised will _not_ be flagged ... Exceptions that are logged with `exc_info` enabled will _not_ be flagged' (fetched)

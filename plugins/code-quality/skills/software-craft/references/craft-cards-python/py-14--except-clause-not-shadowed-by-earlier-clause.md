---
title: No except clause of a Python try names an exception class that an earlier clause or a base class in the same clause already catches
rule_id: PY-14
domain: errors
step: [handle-errors, review]
applies_to: [python, exceptions]
triggers: ['^\s*except\*?\s*\(', '^\s*except\*?\s+[\w.]+(\s+as\s+\w+)?\s*:']
scope: file
check_kind: semantic
severity_default: major
---

# No except clause of a Python try names an exception class that an earlier clause or a base class in the same clause already catches

## Thesis
The `except` clauses of a `try` statement run from the most specific class to the most general, and each class is caught in one place: no clause names a class that an earlier clause already catches, by the same class or by one of its base classes, and no tuple lists a class twice or beside its own base class.

## Rationale
Python inspects the `except` clauses in turn until one matches the exception, and a clause matches when its expression evaluates to the exception's class or a non-virtual base class of it, or to a tuple that contains such a class. A handler for a derived class placed after a handler for its base class therefore never triggers: the base-class handler matches the derived class and is the only one executed. Of two clauses for the same class only the first is executed, and after a clause that catches `BaseException` no subsequent clause catches anything, a bare `except:` included. Inside one tuple, a repeated class or a subclass listed beside its parent does not fail and has no effect. Such a handler is dead code that will never catch any exception, so the handling written in it, such as a retry for one error type, never runs; a class repeated in a tuple means either that it is not the class that should be caught or that it is duplicated code.

## Example
```python
bad:  try:
          value = parse(raw)
      except Exception: value = None
      except (ValueError, UnicodeDecodeError): value = parse(clean(raw))
good: try:
          value = parse(raw)
      except ValueError: value = parse(clean(raw))
      except Exception: value = None
```

## Limits
One position limits this check to builtin exceptions, since the hierarchy of other classes is not known from the source; for a project's own exception classes the finder opens their definitions in the file to establish the base classes. Matching uses the class and its non-virtual base classes, so a class only registered on an abstract base class is not caught by a clause naming that base, and such a pair is outside the rule. A later tuple clause that still names a class no earlier clause catches runs for that class; only the covered entries decide nothing, and the fix removes them, not the clause.

## Validator
Grep the hunk for `except` headers and open the whole try statement they belong to. List each clause's classes in source order. For each class, check whether an earlier clause names it or one of its base classes, and whether its own tuple names it twice or names one of its base classes: use the builtin hierarchy for builtins (`Exception` covers `ValueError`, `ValueError` covers `UnicodeDecodeError`, `RuntimeError` covers `NotImplementedError`, `OSError` covers `FileNotFoundError`) and open the class definitions the file holds for project exceptions; a project class defined in another file has no base classes the finder can establish, so such a pair is not flagged. Validator question: **Does an except clause or a tuple entry name a class that an earlier clause already catches or that a base class in the same tuple covers?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-14`, severity major, `file`, `symbol`, `code` = the covering and the covered `except` headers quoted verbatim from the diff, `fix` = the clauses reordered from the most specific class to the most general, or the covered class removed from the tuple, `rationale` = the earlier clause or the base class in the tuple already matches that class, so the later handling never runs).

## Source
- CPython documentation reference/compound_stmts §except clause (https://docs.python.org/3/reference/compound_stmts.html) — 'When an exception occurs in the try suite, a search for an exception handler is started. This search inspects the except clauses in turn until one is found that matches the exception. ... The raised exception matches an except clause whose expression evaluates to the class or a non-virtual base class of the exception object, or to a tuple that contains such a class.' (fetched)
- SonarSource python S1045 (SonarSource/sonar-python python-checks/src/main/resources/org/sonar/l10n/py/rules/python/S1045.html) — 'This rule raises an issue when an except statement has had all its exceptions caught by a previous except clause. ... an except block is dead code as it will never catch any exception ... If there is a handler for a base class followed by a handler for class derived from that base class, the second handler will never trigger: The handler for the base class will match the derived class, and will be the only executed handler. When multiple except statements try to catch the same exception class, only the first one will be executed. In Python 3, BaseException is the parent of every exception class. When a BaseException is caught by an except clause, none of the subsequent except statement will catch anything. ... Order the except blocks from the most specialzed exception to the most generic ... Catch the same exception only once.' (fetched)
- flake8-bugbear B047 (PyCQA/flake8-bugbear README.rst) — 'Unreachable ``except`` handler. An earlier handler already catches a builtin exception that this one is a subclass of, e.g. ``except ValueError:`` after ``except Exception:``, or a bare ``except:`` after ``except BaseException:``. Only builtin exceptions are checked, since the hierarchy of other classes isn't known from the source.' (fetched)
- SonarSource python S5713 (SonarSource/sonar-python python-checks/src/main/resources/org/sonar/l10n/py/rules/python/S5713.html) — 'Repeating an exception class in a single except statement will not fail but it does not have any effect. Either the exception class is not the one which should be caught, or it is duplicated code which should be removed. Having a subclass and a parent class in the same except statement does not provide any benefit either. It is enough to keep only the parent class.' (fetched)
- Pylint overlapping-except (W0714), message description (pylint-dev/pylint doc/data/messages/o/overlapping-except/bad.py; harvest items.jsonl) — 'Used when exceptions in handler overlap or are identical' (fetched)

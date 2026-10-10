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

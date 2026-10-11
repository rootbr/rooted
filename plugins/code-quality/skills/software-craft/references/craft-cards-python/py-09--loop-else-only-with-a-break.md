---
title: A Python for or while loop carries an else clause only when its body contains a break of that loop
rule_id: PY-09
domain: code
step: [implement, refactor, review]
applies_to: [python]
triggers: ['^\s*else\s*:\s*(#.*)?$', '^\s*else\s*:\s*\S']
scope: file
check_kind: mechanical
severity_default: minor
---

# A Python for or while loop carries an else clause only when its body contains a break of that loop

## Thesis
A Python for or while loop carries an else clause only when its body contains a break that terminates that loop; a loop with no such break has its else removed and the else body dedented after the loop, or gains the break the else was meant to pair with.

## Rationale
In a for or while loop the else clause executes when the loop finishes without executing break: a break executed in the loop body terminates the loop without executing the else suite, and a return or a raised exception skips the else as well. break terminates the nearest enclosing loop, so only a break of this loop, not one inside a nested loop, can skip its else. A loop with an else and no such break therefore always executes the else part, unless an exception is raised or return is used, and the else clause is redundant: its statements belong on the same scope as the loop itself.

## Example
```python
bad:  for number in numbers:
          if number % 2 == 0:
              return number
      else:
          print("no even number")
good: for number in numbers:
          if number % 2 == 0:
              return number
      print("no even number")
```

## Limits
A loop whose body breaks on a hit and whose else handles the miss is the use the else clause exists for, and the rule leaves it alone. A break inside a nested loop terminates only that nested loop and does not count for the outer loop's else. Moving the else body after a loop that has no break keeps the behaviour: the moved code runs on normal termination, and a return or a raised exception skips it just as it skipped the else.

## Validator
Grep the hunk for `else:` lines. For each, open the file and find the statement the else belongs to: the for or while header at the same indentation, not an if or a try. Read the loop body and look for a break whose nearest enclosing loop is this one, skipping breaks inside nested for or while loops. Validator question: **Does a for or while loop carry an else clause while its body holds no break that terminates this loop?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-09`, severity minor, `file`, `symbol`, `code` = the loop header and its `else:` line, verbatim, `fix` = the else removed and its body dedented after the loop, or a `break` added where the loop finds what it searches for, `rationale` = that a loop without break always runs its else unless return or an exception leaves first, so the clause is redundant).

## Source
- CPython Doc/tutorial/controlflow.rst §else Clauses on Loops (https://raw.githubusercontent.com/python/cpython/main/Doc/tutorial/controlflow.rst) — 'In a :keyword:`!for` or :keyword:`!while` loop the :keyword:`!break` statement may be paired with an :keyword:`!else` clause.  If the loop finishes without executing the :keyword:`!break`, the :keyword:`!else` clause executes.' (fetched)
- CPython Doc/tutorial/controlflow.rst §else Clauses on Loops (https://raw.githubusercontent.com/python/cpython/main/Doc/tutorial/controlflow.rst) — 'other ways of ending the loop early, such as a :keyword:`return` or a raised exception, will also skip execution of the :keyword:`else` clause.' (fetched)
- Python documentation, Compound statements §The for statement (https://docs.python.org/3/reference/compound_stmts.html) — 'A break statement executed in the first suite terminates the loop without executing the else clause' (fetched)
- CPython Doc/reference/simple_stmts.rst §The break statement (https://raw.githubusercontent.com/python/cpython/main/Doc/reference/simple_stmts.rst) — 'It terminates the nearest enclosing loop, skipping the optional :keyword:`!else` clause if the loop has one.' (fetched)
- Ruff PLW0120 useless-else-on-loop (astral-sh/ruff crates/ruff_linter/src/rules/pylint/rules/useless_else_on_loop.rs) — 'If a loop _always_ terminates "normally" (i.e., does _not_ contain a `break`), then the `else` clause is redundant, as the code inside the `else` clause will always be executed.' (fetched)
- Pylint useless-else-on-loop (W0120) (pylint-dev/pylint doc/data/messages/u/useless-else-on-loop/bad.py) — 'Loops should only have an else clause if they can exit early with a break statement, otherwise the statements under else should be on the same scope as the loop itself.' (fetched)
- SonarSource python S2836 (SonarSource/sonar-python python-checks/src/main/resources/org/sonar/l10n/py/rules/python/S2836.html) — 'In other words, a loop with an else but no break statement will always execute the else part (unless of course an exception is raised or return is used).' (fetched)

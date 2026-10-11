---
title: A Python generator function returns a value only where a caller delegates to it with yield from, and otherwise ends with a bare return
rule_id: PY-116
domain: performance
step: [implement, review]
applies_to: [python]
triggers: ['^\s*return\s+(?!None\b)[^\s#]', '^\s*yield\b', '\byield\s+from\b']
scope: file
check_kind: semantic
severity_default: major
---

# A Python generator function returns a value only where a caller delegates to it with yield from, and otherwise ends with a bare return

## Thesis
A Python function whose body contains yield or yield from ends early with a bare return, and writes return with a value only where a caller delegates to it with yield from and uses the value of that yield from expression.

## Rationale
In a generator function, return indicates that the generator is done and raises StopIteration; the returned value, if any, is used to construct that StopIteration and becomes its value attribute, so it is not sent to the caller the way a normal function's return value is. Most callers iterate a generator with a for loop, which swallows StopIteration automatically and discards the returned value entirely, without an error. A generator that returns an iterable on an early branch therefore gives its caller nothing for that branch: list() of the call evaluates to [] instead of the iterable's elements. The consumer that receives the value is yield from: when the subgenerator returns, the value attribute of the raised StopIteration becomes the value of the yield from expression. A bare return, without a value, simply ends the generator's execution early and loses nothing.

## Example
```python
bad:  def matching_paths(dir_path, pattern=None):
          if pattern is None:
              return dir_path.glob("*")
          yield from (p for p in dir_path.glob("*") if p.match(pattern))
good: def matching_paths(dir_path, pattern=None):
          if pattern is None:
              yield from dir_path.glob("*")
              return
          yield from (p for p in dir_path.glob("*") if p.match(pattern))
```

## Limits
A subgenerator written to be delegated to, whose result the delegating generator takes as the value of `result = yield from sub()`, returns its value deliberately: return with a value used in conjunction with yield from is the use the generator protocol provides: the value becomes StopIteration.value and the value of the yield from expression. Code that drives a generator by hand with next() or send() and catches the StopIteration reaches the value through its value attribute as well, and a value read that way is deliberate too. The rule reaches a return with a value in the body of a function that itself contains yield or yield from; a return inside a nested function belongs to that function and is judged there.

## Validator
Grep the hunk for a return statement followed by an expression. Open the enclosing function at file scope and check whether its own body, outside nested def and lambda, contains yield or yield from. If it does, trace the function's callers in the diff and the file: a caller that writes `x = yield from f(...)`, or that catches StopIteration from next() or send() and reads its value attribute, uses the value; a for loop, list(), tuple(), sum() or any other ordinary consumer drops it. Validator question: **Does a function whose own body contains yield or yield from return a value that no caller receives through a yield from expression or the value attribute of StopIteration?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-116`, severity major, `file`, `symbol`, `code` = the `return <value>` line and one `yield` line of the same function, verbatim from the diff, `fix` = `yield from <value>` followed by a bare `return`, or a bare `return` where the value is not needed, in Python, `rationale` = the returned value becomes `StopIteration.value`, which a for loop, list() or sum() discards, so the caller silently receives nothing for that branch).

## Source
- SonarSource/sonar-python rule S2712, Python (SonarSource/sonar-python python-checks/src/main/resources/org/sonar/l10n/py/rules/python/S2712.html) — 'Most callers iterate generators with a for loop, which swallows StopIteration automatically and discards the returned value entirely.' (fetched)
- SonarSource/sonar-python rule S2712, Python (SonarSource/sonar-python python-checks/src/main/resources/org/sonar/l10n/py/rules/python/S2712.html) — 'A bare return (without a value) in a generator is fine — it simply ends the generator’s execution early' (fetched)
- Ruff B901 return-in-generator (astral-sh/ruff crates/ruff_linter/src/rules/flake8_bugbear/rules/return_in_generator.rs) — 'the `return` statement will cause the generator to raise `StopIteration` with the value provided, rather than returning the value to the caller.' (fetched)
- Ruff B901 return-in-generator (astral-sh/ruff crates/ruff_linter/src/rules/flake8_bugbear/rules/return_in_generator.rs) — 'Checks for `return {value}` statements in functions that also contain `yield` or `yield from` statements.' (fetched)
- Ruff B901 return-in-generator (astral-sh/ruff crates/ruff_linter/src/rules/flake8_bugbear/rules/return_in_generator.rs) — 'in reality, though, `list(get_file_paths())` evaluates to `[]`' (fetched)
- flake8-bugbear B901 (PyCQA/flake8-bugbear README.rst) — 'In Python 3 ``return x`` can be used in a generator as a return value in conjunction with ``yield from``.' (fetched)
- CPython Doc/reference/simple_stmts.rst §The return statement (https://raw.githubusercontent.com/python/cpython/main/Doc/reference/simple_stmts.rst) — 'The returned value (if any) is used as an argument to construct :exc:`StopIteration` and becomes the :attr:`StopIteration.value` attribute.' (fetched)
- CPython Doc/reference/expressions.rst §Yield expressions (https://raw.githubusercontent.com/python/cpython/main/Doc/reference/expressions.rst) — 'When the underlying iterator is complete, the :attr:`~StopIteration.value` attribute of the raised :exc:`StopIteration` instance becomes the value of the yield expression.' (fetched)
- Caveat: the ruff rule is a preview rule; the Sonar rule flags every return with a value in a generator, and the yield from pairing rests on the flake8-bugbear README and the language reference.

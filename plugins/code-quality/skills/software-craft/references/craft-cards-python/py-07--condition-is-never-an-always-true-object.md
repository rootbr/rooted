---
title: A Python condition is never an object that is always true, such as an uncalled function or method, a lambda, a generator expression or a non-empty string or container literal
rule_id: PY-07
domain: code
step: [implement, review]
applies_to: [python, dynamic-types]
triggers: ['^\s*(el)?if\s+(not\s+)?[\w.]*\b(is|has|can|should)_\w+\s*:', '^\s*(while|assert)\s+(not\s+)?[\w.]*\b(is|has|can|should)_\w+\s*($|,|:)', '^\s*assert\s+\(?\s*[^,()]+\s+for\s+\w+\s+in\s', '^\s*assert\s+f?["\x27]', '\b(if|while|assert)\s+(not\s+)?lambda\b']
scope: file
check_kind: semantic
severity_default: major
---

# A Python condition is never an object that is always true, such as an uncalled function or method, a lambda, a generator expression or a non-empty string or container literal

## Thesis
The test of a Python if, elif, while or assert statement or of a conditional expression is never an object whose truth value is fixed as true: a function, method or lambda object, a generator object, a non-empty string, an f-string with literal text, a non-zero number or a non-empty list, set or dict literal. A predicate is called, `if user.is_admin():`; a generator expression meant as a test is passed to `all()`; an assert message follows its condition after a comma.

## Rationale
Any object can be tested for truth value, and by default an object is considered true unless its class defines either a `__bool__()` method that returns False or a `__len__()` method that returns zero. Functions always evaluate to true in a boolean context, so `if user.is_admin:` without the call tests the method object, never its result, and the branch always runs. `assert <generator_expression>` is always true, and so are a non-empty string — often a message written without its condition, like `assert "x must be positive"` — a non-zero number, an f-string with literal text, a non-empty list, set or dict literal and a lambda. Such a test is a constant: either it has no effect on the execution flow, or some code will never be executed. Since any object can be tested for truth value, nothing raises: the missing call, the missing `all()` or the missing condition shows only as a test that always passes, and calling the predicate, passing the generator to `all()` or giving the assert its condition restores the check.

## Example
```python
bad:  if user.is_admin:
          grant(user)
      assert (price > 0 for price in prices)
      assert "price must be positive"
good: if user.is_admin():
          grant(user)
      assert all(price > 0 for price in prices)
      assert price > 0, "price must be positive"
```

## Limits
The rule reaches only a test whose truth value is fixed by its kind. A name or attribute whose value can be false is tested correctly by its truth value: a property or a stored flag holding a bool, a container that can be empty, an object whose class defines `__bool__()` or `__len__()`, and a name that holds either a function or `None`, such as an optional callback, since `None` is false. A loop written as `while True:` and left by break or return keeps its constant condition on purpose and is outside the rule.

## Validator
Grep the hunk for if, elif, while and assert lines and conditional expressions whose test is a bare name or attribute with no call, above all an `is_`, `has_`, `can_` or `should_` name, a generator expression, a lambda, or a string, f-string, number, list, set or dict literal. For a bare name or attribute, open the file and find what it names: a `def` in the class or module, a lambda assignment, a property or a stored value; follow an import to its definition when it is in the repository. Validator question: **Is the test of an if, elif, while or assert statement or of a conditional expression a function, method or lambda object, a generator object, or a non-empty string, f-string with literal text, non-zero number or non-empty list, set or dict literal?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-07`, severity major, `file`, `symbol`, `code` = the condition line, verbatim, `fix` = the condition that can be false, such as `if user.is_admin():`, `assert all(price > 0 for price in prices)` or `assert price > 0, "price must be positive"`, `rationale` = that the test is an object Python always treats as true, so the branch always runs or the assert never fails).

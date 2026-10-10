---
title: A Python value chosen by a condition is written as x if cond else y, never as cond and x or y, which yields y whenever x is falsy
rule_id: PY-145
domain: code
step: [implement, refactor, review]
applies_to: [python]
triggers: ['=\s*[^=#][^#]*\band\b[^#]*\bor\b', '\breturn\b[^#]*\band\b[^#]*\bor\b']
scope: hunk
check_kind: semantic
severity_default: major
---

# A Python value chosen by a condition is written as x if cond else y, never as cond and x or y, which yields y whenever x is falsy

## Thesis
A Python expression that chooses one of two values by a condition is the conditional expression `x if cond else y`, not the and/or form `cond and x or y`, because that form yields y whenever x is false even though cond is true.

## Rationale
In Python, `x and y` returns x when x is false and otherwise evaluates and returns y, and `x or y` returns x when x is true and otherwise evaluates and returns y; neither restricts its result to False and True. `cond and x or y` therefore returns x only when cond and x are both true. When x is false — False, None, numeric zero of any type, or an empty string or container — the `or` evaluates and returns y although cond holds, and a false literal in the x position, as in `cond and False or y`, makes the whole expression y on every input. The form is the ternary syntax used before Python 2.5, and it is unsafe because it can give wrong results when the value for the true case has a false boolean value. `x if cond else y` evaluates cond first and returns x when cond is true and y otherwise.

## Example
```python
bad:  maximum = x >= y and x or y      # x = 0, y = -1 gives -1
      prefix = verbose and "" or "> "  # always "> "
good: maximum = x if x >= y else y
      prefix = "" if verbose else "> "
```

## Limits
An and/or expression that is not a choice between two values is outside the rule: `s or "foo"`, which replaces an empty string with a default, relies on `or` returning its operand, and the condition of an if or while statement uses only the truth value of the whole expression. When x is a value that is never false, such as a non-empty string literal, the and/or form gives the right result; the conditional expression is still the better form.

## Validator
Grep the hunk for an expression in which `and` is followed by `or` at the same nesting level, in an assignment, a return, a call argument, a lambda body or a comprehension's result rather than in the condition of an if, elif or while statement. Confirm the shape `A and B or C`, with no parentheses that group it differently, and that it picks B or C by A rather than computing a truth value. Determine whether B can be false: a literal False, None, 0 or an empty string or container, or a name or call that can produce one. Validator question: **Does the hunk choose between two values with the and/or form `cond and x or y`?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-145`, severity major, `file`, `symbol`, `code` = the and/or expression quoted verbatim from the diff, `fix` = the conditional expression, such as `maximum = x if x >= y else y`, `rationale` = the x operand, the values for which it is false and the y the expression then yields although the condition holds).

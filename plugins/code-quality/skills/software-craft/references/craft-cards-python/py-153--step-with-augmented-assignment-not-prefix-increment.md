---
title: A Python number is stepped with += 1 or -= 1, never with ++x or --x, which parse as two unary signs and leave the value unchanged
rule_id: PY-153
domain: code
step: [implement, review]
applies_to: [python]
triggers: ['(^\s*|[=(,\[]\s*|\breturn\s+)\+\+\s*[A-Za-z_(]', '(^\s*|[=(,\[]\s*|\breturn\s+)--\s*[A-Za-z_(]']
scope: hunk
check_kind: mechanical
severity_default: major
---

# A Python number is stepped with += 1 or -= 1, never with ++x or --x, which parse as two unary signs and leave the value unchanged

## Thesis
A Python number is incremented with `x += 1` and decremented with `x -= 1`, never with `++x` or `--x`, because Python does not support the unary prefix increment or decrement operator and each of these forms is equivalent to `x`.

## Rationale
Python does not support the C-style pre-increment or pre-decrement operator. Writing `++n` is equivalent to `+(+(n))` and writing `--n` is equivalent to `-(-(n))`: the unary `+` yields its numeric argument unchanged and the unary `-` yields the negation of its numeric argument, so in both cases the expression is equivalent to `n`. A statement `++retries` therefore leaves `retries` at the value it had, and a loop that counts this way never advances its counter.

## Example
```python
bad:  while not send(message):
          ++retries
good: while not send(message):
          retries += 1
```

## Limits
`x++` and `x--` at the end of a statement are outside the rule: the grammar gives the unary `+` and `-` their operand after the sign, so these postfix forms leave the operator without an operand and do not parse. On an object whose class overrides `__pos__` or `__neg__`, `++x` and `--x` call that special method twice, so the result is whatever the method returns rather than the operand unchanged.

## Validator
Grep the hunk for `++` or `--` directly before a name, a call or a parenthesis, at the start of a statement or after `=`, `(`, `[`, `,` or `return`. Skip text inside strings, docstrings and comments, such as command-line flags (`--verbose`), and binary subtraction of a negated operand (`a - -b`), whose left operand is an expression. Validator question: **Does code in the hunk, outside strings and comments, apply `++` or `--` as a prefix to an operand, other than a binary minus followed by a unary minus?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-153`, severity major, `file`, `symbol`, `code` = the statement with the `++` or `--` prefix verbatim from the diff, `fix` = the augmented assignment, `retries += 1` or `retries -= 1`, `rationale` = names that Python has no prefix increment or decrement operator and that `++x` and `--x` are two unary signs equivalent to `x`).

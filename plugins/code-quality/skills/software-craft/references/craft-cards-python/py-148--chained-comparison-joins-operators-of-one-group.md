---
title: A Python chained comparison joins operators of one group only, value comparison, identity or membership, never a mix such as 0 < x is None
rule_id: PY-148
domain: code
step: [implement, review]
applies_to: [python]
triggers: ['\bin\s+[\w.\[\]()]+\s+(is|==|!=|<|>)', '(<=?|>=?|==|!=)\s*[\w.\[\]()]+\s+(is|in|not\s+in)\b', '\bis\s+(not\s+)?[\w.\[\]()]+\s+(in|not\s+in|==|!=|<|>)']
scope: hunk
check_kind: mechanical
severity_default: major
---

# A Python chained comparison joins operators of one group only, value comparison, identity or membership, never a mix such as 0 < x is None

## Thesis
A Python comparison chain takes its operators from one group only: the value comparisons `<`, `>`, `==`, `>=`, `<=` and `!=`, the identity tests `is` and `is not`, or the membership tests `in` and `not in`. A test that combines operators of two groups is written as separate comparisons joined by `and`, or with parentheses around the comparison whose result is tested.

## Rationale
In Python `is`, `is not`, `in` and `not in` are comparison operators beside `<`, `>`, `==`, `>=`, `<=` and `!=`, all comparison operations have the same priority, and comparisons can be chained arbitrarily. A chain `a op1 b op2 c ... y opN z` is equivalent to `a op1 b and b op2 c and ... y opN z`, except that each expression is evaluated at most once, and it implies no comparison between `a` and `c`. A chain that mixes groups therefore never applies its second operator to the result of the first: `0 < x is None` means `0 < x and x is None`. When one expression is part of two comparisons from different groups, the chain is probably a mistake, because `<` does not mean the same thing as `is`. The misread test is silently wrong or it fails: `0 < value is not None` evaluates `0 < value` first, and for a value of None that order comparison raises TypeError, since a default order comparison is not provided.

## Example
```python
bad:  if 0 < value is not None:
          use(value)
good: if value is not None and value > 0:
          use(value)
```

## Limits
A chain inside one group keeps the interpretation that is conventional in mathematics and is correct: `0 <= index < size` and `a == b == c` compare neighbouring operands, and even `x < y > z` is legal, since it compares `x` with `z` not at all. A chain made only of identity tests or only of membership tests also stays in one group and is outside the rule.

## Validator
Grep the hunk for a comparison that holds operators of two groups: a value comparison (`<`, `>`, `==`, `>=`, `<=`, `!=`) together with `is`, `is not`, `in` or `not in`, or an identity test together with a membership test. Open the line and confirm the operators sit in one chain: not separated by `and`, `or`, `not`, a comma or a parenthesis, not inside a string or a comment, and not the `in` of a for statement or of a comprehension's `for` clause. Validator question: **Does one unparenthesised comparison chain join operators from two of the groups value comparison, identity (is, is not) and membership (in, not in)?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-148`, severity major, `file`, `symbol`, `code` = the whole comparison chain, `fix` = the chain rewritten as separate comparisons joined by `and`, such as `value is not None and value > 0`, or with parentheses around the comparison whose result is tested, `rationale` = Python reads `a op1 b op2 c` as `a op1 b and b op2 c`, so the mixed chain never tests the result of its first comparison).

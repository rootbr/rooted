---
title: A Python comparison with a number, string, bytes or container literal or with a newly built object uses == or != and never is or is not
rule_id: PY-02
domain: code
step: [implement, review]
applies_to: [python]
triggers: ['\bis\s+(not\s+)?(-?\d|[bBuUrRfF]{0,2}[\x22\x27]|\(|\[|\{)', '(\d|[\x22\x27\}])\s+is\s+(not\s+)?\w|[\]\)]\s+is\s+(?!(not\s+)?None\b)(not\s+)?\w', '\bis\s+(not\s+)?(dict|list|set|tuple|complex)\(']
scope: hunk
check_kind: mechanical
severity_default: major
---

# A Python comparison with a number, string, bytes or container literal or with a newly built object uses == or != and never is or is not

## Thesis
A Python comparison whose operand is a number, string or bytes literal, a tuple, list, dict or set literal, or an object created only for that comparison, such as `dict(a=1)`, uses `==` or `!=`; `is` and `is not` stay for tests of whether two operands are the same object, such as a test for None.

## Rationale
`x is y` is true if and only if x and y are the same object. For immutable types, an operation that computes a new value may return a reference to any existing object with the same type and value, so identity with an integer, bytes, float, string, frozenset or tuple value is unreliable: the behaviour changes with the value, and the caching behind it is not part of the language specification and can vary between interpreters. Identity checks against literals such as strings and numbers can often work by accident in CPython but are not guaranteed by the language spec, and the compiler produces a SyntaxWarning for them that advises the equality tests `==` and `!=`. An `is` comparison against a list, set or dict literal compares the identities of the objects instead of their values and always evaluates to False, and any object created and used only in an identity check cannot be the same object as the other operand.

## Example
```python
bad:  if status is "done" or retries is 0:
          archive(job)
good: if status == "done" or retries == 0:
          archive(job)
      if result is None:
          retry(job)
```

## Limits
Identity stays the right test where the code means the same object: None is compared with `is` or `is not`, never the equality operators. The check reaches an operand written in the comparison as a literal or a new object, and a name bound to a new list, dict or set that is used only in that identity check; two names that both hold integers or strings are unreliable under `is` for the same reason but fall outside the triggers.

## Validator
Grep the hunk for `is` or `is not` followed by a digit, a minus sign and a digit, a string or bytes quote with an optional prefix, `(`, `[`, `{`, or a call to dict(), list(), set(), tuple() or complex(), and for such an operand written before `is`. Confirm the match is an identity comparison in code, not text in a string or a comment. For a name compared with `is`, open its binding in the function and check whether it was bound to a new list, dict or set only for this check. Validator question: **Does an `is` or `is not` comparison in the hunk have as an operand a number, string, bytes, tuple, list, dict or set literal, or an object created only for that comparison?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-02`, severity major, `file`, `symbol`, `code` = the identity comparison as written, `fix` = the same comparison with `==` in place of `is` and `!=` in place of `is not`, such as `if status == "done":`, `rationale` = identity with a literal depends on the interpreter's object caching, and a new object is never the same object as the other operand).

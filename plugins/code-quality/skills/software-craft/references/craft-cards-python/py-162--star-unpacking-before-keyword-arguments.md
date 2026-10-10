---
title: A Python call puts *iterable unpacking before its keyword arguments, because the unpacked values bind ahead of every keyword whatever the written order
rule_id: PY-162
domain: design
step: [implement, review]
applies_to: [python]
triggers: ['^(?!\s*(async\s+)?def\s).*\w\(.*\b\w+\s*=\s*[^=,][^,]*,\s*\*(?![*\s,)])', '^(?!\s*(async\s+)?def\s)(?!\s*lambda\b).*\b\w+=[^=,()]*,\s*\*(?!\*)[\w\[(]']
scope: hunk
check_kind: mechanical
severity_default: minor
---

# A Python call puts *iterable unpacking before its keyword arguments, because the unpacked values bind ahead of every keyword whatever the written order

## Thesis
A Python call writes each `*iterable` argument ahead of its keyword arguments, as in `f(*rest, key=value)`; a call that writes `*iterable` after a keyword argument, as in `f(key=value, *rest)`, is a finding.

## Rationale
Python treats the elements of a `*expression` argument as additional positional arguments, and although the `*expression` syntax may appear after explicit keyword arguments, it is processed before the keyword arguments and any `**expression` arguments. With `def f(a, b)`, the call `f(b=1, *(2,))` therefore binds `a=2` and `b=1`, and `f(a=1, *(2,))` raises TypeError because `a` receives multiple values. The keyword-first spelling works only when the keyword parameter is declared after all parameters supplied by the unpacked sequence, and this change of ordering can surprise and mislead readers; the form is supported only for backwards compatibility. Because the unpacking is processed before the keywords wherever it is written, moving it ahead of them changes no binding and makes the written order the order in which the arguments are processed.

## Example
```python
bad:  def connect(host, port, timeout=10): ...
      connect(timeout=5, *hosts)
good: def connect(host, port, timeout=10): ...
      connect(*hosts, timeout=5)
```

## Limits
A call whose keyword parameter is declared after every parameter the unpacked sequence fills, such as `foo(z=3, *[1, 2])` against `def foo(x, y, z)`, returns the expected `(1, 2, 3)` and is still a finding, because its written order differs from the order in which the arguments are processed. The rule reaches single-star unpacking in a call only: `**mapping` unpacking, whose contents are treated as additional keyword arguments, and the `*args` of a `def` or `lambda` parameter list are outside it. Using keyword arguments and `*expression` in the same call is unusual, so in practice the case does not often arise.

## Validator
Grep the hunk for a call whose argument list holds a `name=value` keyword argument followed, inside the same parentheses, by a single-star argument such as `*name`, `*(...)`, `*[...]` or `*func(...)`; skip `def` and `lambda` parameter lists and `**` mapping unpacking. When the call spans several lines, open the whole call and read the order of its arguments. Validator question: **Does a call in the hunk write a star-unpacked iterable argument after one of its keyword arguments?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-162`, severity minor, `file`, `symbol`, `code` = the call with the keyword argument and the star argument after it, verbatim, `fix` = the same call with the `*iterable` moved ahead of every keyword argument, as in `connect(*hosts, timeout=5)`, `rationale` = Python processes the unpacked values as positional arguments before any keyword, so the written order misleads and a keyword naming one of the filled parameters raises TypeError).

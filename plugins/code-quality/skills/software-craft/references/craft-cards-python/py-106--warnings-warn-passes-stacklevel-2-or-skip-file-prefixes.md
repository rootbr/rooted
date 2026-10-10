---
title: A Python warnings.warn call passes an explicit stacklevel of 2 or higher, or skip_file_prefixes on Python 3.12 and later, so the warning points at the caller instead of the warn line
rule_id: PY-106
domain: errors
step: [implement, review]
applies_to: [python, library, public-api]
triggers: ['\bwarnings[.]warn\(', '^\s*warn\(\s*(?:f?[\x22\x27]|\w)']
scope: hunk
check_kind: mechanical
severity_default: minor
---

# A Python warnings.warn call passes an explicit stacklevel of 2 or higher, or skip_file_prefixes on Python 3.12 and later, so the warning points at the caller instead of the warn line

## Thesis
A Python call to `warnings.warn` passes `stacklevel` set to 2 or higher, which outputs a stack frame from higher up the stack than the `warn` line, with 2 making the warning refer to the caller of the function that issues it, or, on Python 3.12 and later, passes a non-empty `skip_file_prefixes` tuple, which ignores the stack frames of those file prefixes when counting stack levels and implicitly overrides `stacklevel` to `max(2, stacklevel)`.

## Rationale
`warnings.warn` uses a `stacklevel` of 1 by default, which outputs the stack frame of the line on which `warn` is called; a higher number outputs a stack frame from higher up the stack. For a wrapper function or a deprecated API, the default makes the warning refer to the source of that function itself instead of to its caller, which defeats the purpose of the warning message. With `stacklevel=2` the warning refers to the caller and gives the caller more context about the warning. `skip_file_prefixes`, added in Python 3.12, is a tuple of strings naming the file prefixes whose stack frames are ignored when counting stack levels, which can be used to make the warning appear at call sites outside a package.

## Example
```python
bad:  def connect(host, timeout=None):
          if timeout is not None:
              warnings.warn("timeout= is deprecated; pass deadline=", DeprecationWarning)
          return open_connection(host, timeout)
good: def connect(host, timeout=None):
          if timeout is not None:
              warnings.warn("timeout= is deprecated; pass deadline=", DeprecationWarning, stacklevel=2)
          return open_connection(host, timeout)
```

## Limits
`stacklevel=2` is the lower bound of the rule, not the only correct value: an automatic fix that assigns 2 changes the behaviour of the code, and the author may wish to assign a higher stacklevel. Where the warning should appear at call sites outside a package and a constant `stacklevel` does not fit all call paths or is otherwise challenging to maintain, `skip_file_prefixes` is the documented means; it was added in Python 3.12. A `skip_file_prefixes` that is an explicitly empty tuple does not affect `stacklevel`, so it does not satisfy the rule.

## Validator
Grep the hunk for `warnings.warn(` and for a bare `warn(` call; trace a bare `warn` to `from warnings import warn` in the file. Open the whole call, which may span several lines, and read its keyword arguments `stacklevel` and `skip_file_prefixes`. Count a `stacklevel` given by a name or an expression as explicit; count a `skip_file_prefixes` given as a literal `()` as absent. Validator question: **Does a warnings.warn call in the hunk omit stacklevel or pass it as the literal 1, while it passes no non-empty skip_file_prefixes?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-106`, severity minor, `file`, `symbol`, `code` = the `warnings.warn(...)` call quoted verbatim from the diff, `fix` = the same call with `stacklevel=2`, or the higher level that reaches the caller, or with `skip_file_prefixes=(os.path.dirname(__file__),)` on Python 3.12 and later, `rationale` = names that the default stacklevel of 1 attributes the warning to the warn line instead of to the caller of the function that issues it).

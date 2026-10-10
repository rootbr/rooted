---
title: A Python call passes by position a positional-only parameter of a callee that takes **kwargs, because its name given as a keyword lands in kwargs and leaves the parameter unfilled
rule_id: PY-164
domain: design
step: [implement, review]
applies_to: [python]
triggers: ['def\s+\w+\(.*/\s*,.*\*\*\w+', '^(?!\s*(async\s+)?def\s).*\w\(\s*\w+\s*=(?!=)']
scope: callers
check_kind: semantic
severity_default: major
---

# A Python call passes by position a positional-only parameter of a callee that takes **kwargs, because its name given as a keyword lands in kwargs and leaves the parameter unfilled

## Thesis
A Python call to a function that declares a positional-only parameter (one before `/`) and a `**kwargs` parameter passes that parameter by position, as in `print_name("Jacob")`, rather than as a keyword argument of the same name, as in `print_name(name="Jacob")`.

## Rationale
Positional-only parameters cannot be passed by keyword, so their names can be used in `**kwds` without ambiguity: a keyword argument with the same name as a positional-only parameter is included in the `**kwargs` dict and fills no parameter slot. When all arguments have been processed, the parameter's slot is still unfilled and is filled with its default value; when it has no default, the call raises TypeError for the unfilled slot. With `def print_name(name="Sarah", /, **kwds)`, the call `print_name(name="Jacob")` raises nothing and prints Sarah, while `print_name("Jacob")` prints Jacob.

## Example
```python
bad:  def print_name(name="Sarah", /, **kwds):
          print(name)
      print_name(name="Jacob")  # prints Sarah
good: def print_name(name="Sarah", /, **kwds):
          print(name)
      print_name("Jacob")
```

## Limits
A call that passes the positional-only parameter by position and a key of the same name through `**kwargs`, as `foo(1, **{'name': 2})` does against `def foo(name, /, **kwds)`, is the documented use of `/` and is correct. A callee without a `**kwargs` parameter is outside this rule: there a keyword argument that does not correspond to a parameter it can fill raises TypeError, and no call runs with the default.

## Validator
For each call in the hunk that passes a keyword argument, resolve the callee and open its definition in the repository or the installed package; for a `def` in the hunk whose signature has a `/` and a `**` parameter, trace its callers in the repository. Check whether the keyword's name is a parameter listed before the `/` and whether the same signature declares a `**` parameter. Validator question: **Does a call pass, as a keyword argument, the name of a positional-only parameter of a callee that also declares a variadic keyword parameter such as kwargs?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-164`, severity major, `file`, `symbol`, `code` = the call with the keyword argument, verbatim, `fix` = the call passing that value by position in the parameter's place, as in `print_name("Jacob")`, `rationale` = the keyword lands in the callee's `**kwargs` because the parameter is positional-only, so the parameter keeps its default or the call raises TypeError).

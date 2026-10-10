---
title: A Python parameter with a default value is declared after *args as keyword-only, not before it
rule_id: PY-165
domain: design
step: [design, implement]
applies_to: [python]
triggers: ['def\s+\w+\(.*=[^,()]*,\s*\*(?![*\s,)])\w', 'lambda\s+[^:]*=[^,:]*,\s*\*(?!\*)\w']
scope: hunk
check_kind: mechanical
severity_default: minor
---

# A Python parameter with a default value is declared after *args as keyword-only, not before it

## Thesis
In a Python function that takes `*args`, a parameter with a default value is declared after `*args`, where it is keyword-only, as in `def func(*args, x=None)`, rather than before it, as in `def func(x=None, *args)`.

## Rationale
If there are N positional arguments, they are placed in the first N parameter slots, and `*args` receives only the excess positional arguments, so a defaulted parameter declared before `*args` takes the first positional argument whenever the caller passes any: `func(1, 2)` binds `x=1` and `args=(2,)`. A call that passes positional arguments and also passes that parameter by keyword ends up with multiple values for it: the keyword finds its slot already filled and the call raises TypeError, as `func(1, x=2)` does. A parameter that occurs after `*args` is keyword-only and can only be used as a keyword, so every positional argument goes to `*args` and the default holds unless the caller names the parameter.

## Example
```python
bad:  def func(x=None, *args):
          return [x, *args]
good: def func(*args, x=None):
          return [*args, x]
```

## Limits
A parameter without a default before `*args` is a required positional parameter and is outside this rule, as in `def write_multiple_items(file, separator, *args)`. A signature whose only parameters before `*args` are positional-only, declared before `/`, is outside it as well: those parameters cannot be passed by keyword, so a keyword cannot give them a second value. Moving a defaulted parameter after `*args` changes the call contract, since it can then only be used as a keyword: a caller that passed it by position passes it by name.

## Validator
Grep each `def` and `lambda` signature in the hunk for a parameter with a default value (`name=value`) followed, later in the same signature, by a `*name` parameter, not a bare `*` and not `**`; skip a signature whose parameters before `*name` are all positional-only (before `/`). Open the callers of the function in the repository that pass the defaulted parameter by position, since the fix moves them to the keyword. Validator question: **Does a signature in the hunk declare a positional-or-keyword parameter with a default value before its variadic positional parameter?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-165`, severity minor, `file`, `symbol`, `code` = the signature with the defaulted parameter before `*args`, verbatim, `fix` = the signature with that parameter moved after `*args`, as in `def func(*args, x=None):`, and its positional callers switched to the keyword, `rationale` = a defaulted parameter before `*args` takes the first positional argument and gets multiple values when also passed by keyword).

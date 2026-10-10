---
title: A Python exception is constructed with its message already formatted, never with a string literal holding %- or {}-placeholders followed by the values as further constructor arguments
rule_id: PY-171
domain: errors
step: [implement, handle-errors, review]
applies_to: [python, exceptions]
triggers: ['\braise\s+[\w.]+\(\s*[rRuU]?[\x22\x27][^\x22\x27]*%[-#0 +]*\d*([.]\d+)?[sdirfgexXoc(][^\x22\x27]*[\x22\x27]\s*,', '\b\w*(Error|Exception)\(\s*[rRuU]?[\x22\x27][^\x22\x27]*%[-#0 +]*\d*([.]\d+)?[sdirfgexXoc(][^\x22\x27]*[\x22\x27]\s*,', '\braise\s+[\w.]+\(\s*[rRuU]?[\x22\x27][^\x22\x27]*\{[^\x22\x27]*\}[^\x22\x27]*[\x22\x27]\s*,', '\b\w*(Error|Exception)\(\s*[rRuU]?[\x22\x27][^\x22\x27]*\{[^\x22\x27]*\}[^\x22\x27]*[\x22\x27]\s*,']
scope: hunk
check_kind: mechanical
severity_default: minor
---

# A Python exception is constructed with its message already formatted, never with a string literal holding %- or {}-placeholders followed by the values as further constructor arguments

## Thesis
A Python exception constructor receives its message already formatted, with the `%` operator, `str.format()` or an f-string; a constructor call with several arguments whose first is a string literal holding `%`-style or `{}`-style placeholders for the further arguments is the defect.

## Rationale
An exception instance has an `args` attribute that stores the arguments given to its constructor, and the built-in exception types define `__str__` to print all the arguments: `str()` of an instance returns the representation of the argument(s). No step fills the placeholders of the first argument from the others, so `str()` of the exception shows the representation of the whole argument tuple, the raw template beside the values. Applying the formatting before the call, as in `RuntimeError("..." % (a, b))`, hands the constructor one finished message.

## Example
```python
bad:  raise RuntimeError("timeout after %s s on %s", timeout, host)
good: raise RuntimeError(f"timeout after {timeout} s on {host}")
```

## Limits
The mechanism is that of the built-in `__str__`: an exception class of the project whose own `__init__` or `__str__` fills a template from further arguments takes this call shape by design, so open the class when it is not a built-in type. A `%` or a brace pair that is plain text rather than a placeholder intended for formatting, passed with values deliberately kept as separate arguments, is outside the rule.

## Validator
Grep the hunk for an exception constructor call, in a `raise` statement or assigned and raised later, whose first argument is a plain string literal (not an f-string) and which has at least one further argument. Check the literal for `%` followed by a conversion character, or for a `{...}` field, that the further arguments would fill. When the class is defined in the project, open it and check whether its `__init__` or `__str__` formats the template with the further arguments. Validator question: **Does an exception constructor here receive a string literal with `%` or `{}` placeholders as its first argument and the values for them as further arguments, with no `__init__` or `__str__` of the class that fills them in?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-171`, severity minor, `file`, `symbol`, `code` = the constructor call with the template and its arguments, `fix` = the call with one formatted message, as in `raise RuntimeError(f"timeout after {timeout} s on {host}")`, `rationale` = the exception stores the arguments as `args` and prints them as a tuple, so the placeholders stay unfilled).

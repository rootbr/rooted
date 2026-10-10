---
title: A Python 3.14 t-string evaluates to a string.templatelib.Template rather than a str, so it passes through a processing function before it is used as text
rule_id: PY-130
domain: code
step: [implement, review]
applies_to: [python]
triggers: ['(?:^|[\s(\[{,=:+])[tT][rR]?(["''])(?:(?!\1).)*\{', '(?:^|[\s(\[{,=:+])[rR][tT](["''])(?:(?!\1).)*\{', '\bstring[.]templatelib\b']
scope: file
check_kind: semantic
severity_default: major
---

# A Python 3.14 t-string evaluates to a string.templatelib.Template rather than a str, so it passes through a processing function before it is used as text

## Thesis
A t-string literal, available from Python 3.14, reaches printing, a parameter that expects a `str` or concatenation with a `str` only through a template processing function; where only the interpolated `str` is wanted, the literal is an f-string.

## Rationale
A t-string uses a `t` in place of the `f` prefix and evaluates not to `str` but to a `string.templatelib.Template` that holds the static string parts and the interpolated values separately, for template processing code that may return a string or any other type. `Template` provides no specialized `__str__()`, because there is no canonical way to convert a template to a string; `Template` and `Interpolation` provide `__repr__()` implementations. A t-string used without processing can therefore print an object representation instead of formatted text, or pass the wrong type to a function that expects a string, and concatenating a `Template` with a `str` is not supported. Such a use is almost always unintentional, from an author who expected the string-like behaviour of an f-string, which immediately evaluates to a string.

## Example
```python
bad:  print(t"Hello {name}")
good: print(f"Hello {name}")
      print(html(t"Hello {name}"))
```

## Limits
A t-string handed to a template processing function, or stored and returned for one, is the intended use: a template gives processing code the string and its interpolated values before they are combined, for safety checks, web templating and domain-specific languages. Concatenating two `Template` objects is supported, and a `str` that belongs in a template is wrapped in a `Template`, to treat it as a static string, or in an `Interpolation`, to treat it as dynamic.

## Validator
Grep the file for t-string literals, with a `t`, `T`, `tr` or `rt` prefix in any quote style, and for `string.templatelib` imports. Trace each t-string value to every place it is used: a call argument, a return, an assignment that flows on, an operator. Open the receiving function: it processes the template when it reads `.strings`, `.interpolations` or `.values`, iterates the template, or is annotated to take a `Template`. Validator question: **Does a t-string value reach `print`, `str()`, an f-string replacement field, a `+` with a `str` or a parameter that expects a `str` without passing through a template processing function?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-130`, severity major, `file`, `symbol`, `code` = the t-string literal and the call or operator that receives it, `fix` = the literal as an f-string where plain text is meant, or the template passed through its processing function first, `rationale` = a `Template` has no specialized `__str__()`, so the receiver gets an object representation or a value of the wrong type).

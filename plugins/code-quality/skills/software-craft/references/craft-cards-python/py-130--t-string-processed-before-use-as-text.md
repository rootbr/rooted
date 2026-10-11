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

## Source
- SonarSource sonar-python rule S7942 (https://raw.githubusercontent.com/SonarSource/sonar-python/master/python-checks/src/main/resources/org/sonar/l10n/py/rules/python/S7942.html) — 'Template strings, or t-strings, are a Python 3.14+ feature that creates Template objects, not regular strings. Unlike f-strings that immediately evaluate to strings, t-strings require explicit processing by a template processing function to be useful.' … 'This is almost always unintentional, as developers typically expect string-like behavior similar to f-strings.' … 'The Template object contains the static string parts and interpolated values separately' … 'Using an unprocessed template string can lead to unexpected behavior in your application, such as printing object representations instead of formatted strings, or passing the wrong type to functions that expect strings.' (fetched)
- PEP 750 §Abstract, §No Template.__str__() Implementation (https://raw.githubusercontent.com/python/peps/main/peps/pep-0750.rst) — 'Template strings are a generalization of f-strings, using a ``t`` in place of the ``f`` prefix. Instead of evaluating to ``str``, t-strings evaluate to a new type, ``Template``' … 'Templates provide developers with access to the string and its interpolated values *before* they are combined.' … 'enables safety checks, web templating, domain-specific languages, and more.' … 'The ``Template`` type does not provide a specialized ``__str__()`` implementation.' … 'This is because ``Template`` instances are intended to be used by template processing code, which may return a string or any other type. There is no canonical way to convert a Template to a string.' … 'The ``Template`` and ``Interpolation`` types both provide useful ``__repr__()`` implementations.' (fetched)
- CPython Doc/library/string.templatelib.rst §Template (https://raw.githubusercontent.com/python/cpython/main/Doc/library/string.templatelib.rst) — 'Concatenating a :class:`!Template` and a ``str`` is **not** supported.' … 'you should either wrap the string directly in a :class:`!Template` (to treat it as a static string) or use an :class:`!Interpolation` (to treat it as dynamic)' … '.. versionadded:: 3.14' (fetched); the same section shows two t-strings joined with + as a supported concatenation

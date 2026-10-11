---
title: A Python docstring is a plain string literal, never an f-string, because a formatted string literal in the docstring position leaves __doc__ None
rule_id: PY-122
domain: code
step: [implement, document, review]
applies_to: [python]
triggers: ['^\s*[fF][rR]?("""|\x27\x27\x27)', '^\s*[rR][fF]("""|\x27\x27\x27)', '^\s*[fF][rR]?["\x27][^"\x27]*["\x27]\s*$']
scope: hunk
check_kind: mechanical
severity_default: minor
---

# A Python docstring is a plain string literal, never an f-string, because a formatted string literal in the docstring position leaves __doc__ None

## Thesis
The first statement of a Python module, class, function or method that is meant as its docstring is a plain string literal, not a formatted string literal, whether or not the f-string holds a replacement field.

## Rationale
A docstring is a string literal that occurs as the first statement of a module, function, class or method definition, and it becomes the `__doc__` attribute of that object. A formatted string literal cannot serve as a docstring even when it holds no expression: Python interprets it as a joined string, so after `def foo(): f"Not a docstring"` the value of `foo.__doc__` is `None`. The text the author wrote is then reachable neither through `__doc__` nor by any automated documentation tooling. A plain string literal in the same position is a docstring and becomes the object's `__doc__`.

## Example
```python
bad:  def load(kind):
          f"""Load the {kind} record from the cache."""
          return cache[kind]
good: def load(kind):
          """Load the record of the given kind from the cache."""
          return cache[kind]
```

## Limits
The rule reaches the first statement of a module, class, function or method body only; a formatted string literal further down the body is not in the docstring position and is outside it. A raw prefix alone keeps a literal a docstring: `r"""..."""` is the documented form for a docstring that holds backslashes.

## Validator
Grep the hunk for a line that opens with a string literal carrying an `f` or `F` prefix, alone or combined with `r` or `R` in either order. Open the enclosing `def`, `async def`, `class` or module and check whether that literal is the first statement of the body, with only comments and blank lines before it. Validator question: **Is a formatted string literal the first statement of a module, class, function or method body, where its docstring would stand?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-122`, severity minor, `file`, `symbol`, `code` = the f-prefixed literal that opens the body, verbatim, `fix` = the same text as a plain `"""..."""` literal with each replacement field rewritten as words, `rationale` = an f-string in the docstring position is no docstring, so `__doc__` stays `None` and documentation tooling never sees the text).

## Source
- Ruff B021 f-string-docstring (astral-sh/ruff crates/ruff_linter/src/rules/flake8_bugbear/rules/f_string_docstring.rs) — 'Python will interpret the f-string as a joined string, rather than as a docstring. As such, the "docstring" will not be accessible via the `__doc__` attribute, nor will it be picked up by any automated documentation tooling.' (fetched)
- flake8-bugbear B021 (PyCQA/flake8-bugbear README.rst) — 'f-string used as docstring. This will be interpreted by python as a joined string rather than a docstring.' (fetched)
- CPython Doc/reference/lexical_analysis.rst §f-strings (https://raw.githubusercontent.com/python/cpython/main/Doc/reference/lexical_analysis.rst) — 'Formatted string literals cannot be used as :term:`docstrings <docstring>`, even if they do not include expressions' and its doctest '>>> print(foo.__doc__) None' (fetched)
- PEP 257 Docstring Conventions §What is a Docstring? (https://raw.githubusercontent.com/python/peps/main/peps/pep-0257.rst) — 'A docstring is a string literal that occurs as the first statement in a module, function, class, or method definition.' and 'Such a docstring becomes the ``__doc__`` special attribute of that object.' and 'Use ... raw triple double quotes ... if you use any backslashes in your docstrings.' (fetched)

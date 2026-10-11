---
title: A regular-expression pattern literal passed to re.compile or another re module function is written in Python's raw-string notation
rule_id: PY-36
domain: code
step: [implement, review]
applies_to: [python]
triggers: ['\b(re|regex)[.](compile|search|match|fullmatch|findall|finditer|split|sub|subn)\(\s*[bB]?[\x22\x27]']
scope: hunk
check_kind: mechanical
severity_default: minor
---

# A regular-expression pattern literal passed to re.compile or another re module function is written in Python's raw-string notation

## Thesis
The pattern literal passed as the first argument to re.compile, re.search, re.match, re.fullmatch, re.findall, re.finditer, re.split, re.sub or re.subn is written in raw-string notation, with the r prefix, so that its backslashes reach the re module as written.

## Rationale
Regular expressions use the backslash to mark special forms and to let a special character be used without its special meaning, and Python string literals use the same character for the same purpose. In an ordinary literal Python handles its own escapes before re sees the pattern: \b is a word boundary or a backspace in a regex depending on the context, but always a backspace in string and bytes literals, so "\bstop\b" hands re two backspace characters where the author meant two word boundaries. To match one literal backslash the regular expression must be \\, and each of those backslashes must be expressed as \\ inside an ordinary literal, so the pattern string becomes '\\\\'. An escape sequence that is invalid in Python's usage generates a SyntaxWarning, to become a SyntaxError, even when it is a valid escape sequence for a regular expression. In a literal prefixed with r, backslashes are not handled in any special way: r"\n" is a two-character string of a backslash and n, and re still matches it as a newline. Raw strings remove the double escaping.

## Example
```python
bad:  if re.search("\bstop\b", line):
          halt()
good: if re.search(r"\bstop\b", line):
          halt()
```

## Limits
The rule reads the literal at the call; a pattern that arrives as a name, an attribute, a concatenation or a function result is outside it. A literal with the no-op u prefix cannot take the r prefix beside it, since the two prefixes are incompatible; the fix removes the u and writes the literal with r alone. Adding r to a literal that already holds escape sequences alters the literal's runtime value: for an escape that keeps its meaning in a regex, such as \n, the match stays the same, while \b turns from a backspace into a word boundary, so a literal holding \b is rewritten according to what the author meant to match. The functions of the same names in the third-party regex module take patterns the same way and fall under the same rule.

## Validator
Grep the hunk for a call to re.compile, re.search, re.match, re.fullmatch, re.findall, re.finditer, re.split, re.sub or re.subn, or to the regex module's function of the same name, and read its first argument. Treat a string or bytes literal whose prefix holds r or R (r, rb, br in any case) as raw, and skip a first argument that is a name, an attribute, a call or a concatenation. For a non-raw literal holding \b, read the surrounding code to tell whether a word boundary or a backspace was meant, and state it in the fix. Validator question: **Is the first argument of this re or regex call a string or bytes literal without the r prefix?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-36`, severity minor, `file`, `symbol`, `code` = the call with its non-raw pattern literal, quoted verbatim from the diff, `fix` = the same call with the pattern in raw notation and each doubled backslash halved, e.g. `re.search(r"\bstop\b", line)`, `rationale` = Python handles the literal's escapes before re reads the pattern, so \b becomes a backspace and one literal backslash takes four).

## Source
- CPython Doc/library/re.rst §introduction (https://raw.githubusercontent.com/python/cpython/main/Doc/library/re.rst) — 'to indicate special forms or to allow special characters to be used without invoking their special meaning' (fetched)
- CPython Doc/library/re.rst §introduction (https://raw.githubusercontent.com/python/cpython/main/Doc/library/re.rst) — 'This collides with Python's usage of the same character for the same purpose in string literals' (fetched)
- CPython Doc/library/re.rst §introduction (https://raw.githubusercontent.com/python/cpython/main/Doc/library/re.rst) — 'to match a literal backslash, one might have to write ``'\\\\'`` as the pattern string' (fetched)
- CPython Doc/library/re.rst §introduction (https://raw.githubusercontent.com/python/cpython/main/Doc/library/re.rst) — 'because the regular expression must be ``\\``, and each backslash must be expressed as ``\\`` inside a regular Python string literal' (fetched)
- CPython Doc/library/re.rst §introduction (https://raw.githubusercontent.com/python/cpython/main/Doc/library/re.rst) — 'any invalid escape sequences in Python's usage of the backslash in string literals now generate a :exc:`SyntaxWarning` and in the future this will become a :exc:`SyntaxError`' (fetched)
- CPython Doc/library/re.rst §introduction (https://raw.githubusercontent.com/python/cpython/main/Doc/library/re.rst) — 'This behaviour will happen even if it is a valid escape sequence for a regular expression.' (fetched)
- CPython Doc/library/re.rst §introduction (https://raw.githubusercontent.com/python/cpython/main/Doc/library/re.rst) — 'is a two-character string containing' (fetched)
- CPython Doc/library/re.rst §introduction (https://raw.githubusercontent.com/python/cpython/main/Doc/library/re.rst) — 'The solution is to use Python's raw string notation for regular expression patterns; backslashes are not handled in any special way in a string literal prefixed with' (fetched)
- Ruff RUF039 unraw-re-pattern (astral-sh/ruff crates/ruff_linter/src/rules/ruff/rules/unraw_re_pattern.rs) — 'Regular expressions should be written using raw strings to avoid double escaping.' (fetched)
- Ruff RUF039 unraw-re-pattern (astral-sh/ruff crates/ruff_linter/src/rules/ruff/rules/unraw_re_pattern.rs) — 'which is word boundary or backspace in a regex, depending on the context, but always a backspace in string and bytes literals' (fetched)
- Ruff RUF039 unraw-re-pattern (astral-sh/ruff crates/ruff_linter/src/rules/ruff/rules/unraw_re_pattern.rs) — 'the fix alters the runtime value of the literal while retaining the regex semantics' (fetched)
- Ruff RUF039 unraw-re-pattern (astral-sh/ruff crates/ruff_linter/src/rules/ruff/rules/unraw_re_pattern.rs) — 'but the regex library will interpret `\\n` and will still match a newline' (fetched)
- Ruff RUF039 unraw-re-pattern (astral-sh/ruff crates/ruff_linter/src/rules/ruff/rules/unraw_re_pattern.rs) — 'the argument is a string with a (no-op) `u` prefix' (fetched)
- Ruff RUF039 unraw-re-pattern (astral-sh/ruff crates/ruff_linter/src/rules/ruff/rules/unraw_re_pattern.rs) — 'as the prefix is incompatible with the raw prefix' (fetched)
- Ruff RUF039 unraw-re-pattern (astral-sh/ruff crates/ruff_linter/src/rules/ruff/rules/unraw_re_pattern.rs) — 'Reports the following `re` and `regex` calls when their first arguments are not raw strings' (fetched)
- Caveat: RUF039 is a preview rule in Ruff and reports the same calls on the regex module.

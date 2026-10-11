---
title: A call to re.sub, re.subn or re.split passes count, maxsplit and flags as keyword arguments, never positionally
rule_id: PY-34
domain: code
step: [implement, review]
applies_to: [python]
triggers: ['\bre[.](sub|subn|split)\([^=]*,\s*re[.][A-Z]', '\bre[.]split\([^=]*,\s*\d+\s*\)', '\bre[.](sub|subn)\([^=]*,[^=]*,[^=]*,\s*\d+\s*\)']
scope: hunk
check_kind: mechanical
severity_default: major
---

# A call to re.sub, re.subn or re.split passes count, maxsplit and flags as keyword arguments, never positionally

## Thesis
A call to `re.sub`, `re.subn` or `re.split` that passes `count`, `maxsplit` or `flags` passes it as a keyword argument, never positionally.

## Rationale
`re.sub` and `re.subn` have the signature `(pattern, repl, string, count=0, flags=0)` and `re.split` has `(pattern, string, maxsplit=0, flags=0)`, while many other `re` functions have the form `f(pattern, string, flags)`, as in `search(pattern, string, flags=0)`. It is commonly assumed that `flags` is the third positional parameter, forgetting about `count` and `maxsplit`: a flag passed as the fourth positional argument of `re.sub` binds to `count`, a flag passed third to `re.split` binds to `maxsplit`, and `flags` keeps its default 0, so the flag is not applied. Python 3.13 deprecates passing `count` and `flags` positionally to `re.sub`, and `maxsplit` and `flags` positionally to `re.split`, and states that in future Python versions they will be keyword-only parameters.

## Example
```python
bad:  clean = re.sub(r"\s+", " ", text, re.IGNORECASE)
      head = re.split(r",", line, 1)
good: clean = re.sub(r"\s+", " ", text, flags=re.IGNORECASE)
      head = re.split(r",", line, maxsplit=1)
```

## Limits
The methods of a compiled pattern take no `flags` parameter, as in `Pattern.sub(repl, string, count=0)` and `Pattern.split(string, maxsplit=0)`, so they are outside the rule. A `count` or `maxsplit` passed positionally on purpose computes as intended, and the rule still asks for the keyword because the positional form is deprecated since Python 3.13.

## Validator
Grep the hunk for calls of `re.sub`, `re.subn` and `re.split`, and of these names imported from `re`. Count the positional arguments of each call: more than three for `re.sub` or `re.subn`, more than two for `re.split`. Validator question: **Does a call to `re.sub`, `re.subn` or `re.split` in the hunk pass `count`, `maxsplit` or `flags` as a positional argument?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-34`, severity major, `file`, `symbol`, `code` = the call as written in the diff, `fix` = the same call with `count=`, `maxsplit=` or `flags=` named, such as `re.sub(pattern, repl, text, flags=re.IGNORECASE)`, `rationale` = the fourth positional parameter of re.sub is count and the third of re.split is maxsplit, so a positional flag is read as a count and not applied, and the positional form is deprecated since Python 3.13).

## Source
- CPython Doc/library/re.rst §Functions (python/cpython Doc/library/re.rst) — "sub(pattern, repl, string, count=0, flags=0)"; "subn(pattern, repl, string, count=0, flags=0)"; "split(pattern, string, maxsplit=0, flags=0)"; "search(pattern, string, flags=0)"; "Passing count and flags as positional arguments is deprecated."; "Passing maxsplit and flags as positional arguments is deprecated."; "In future Python versions they will be" (fetched)
- CPython Doc/library/re.rst §Regular Expression Objects (python/cpython Doc/library/re.rst) — "Pattern.sub(repl, string, count=0)"; "Pattern.split(string, maxsplit=0)" (fetched)
- Ruff B034 re-sub-positional-args (astral-sh/ruff crates/ruff_linter/src/rules/flake8_bugbear/rules/re_sub_positional_args.rs) — "can lead to confusion, as most methods in the re module accept flags as the third positional argument, while re.sub, re.subn, and re.split have different signatures." (fetched)
- flake8-bugbear B034 (PyCQA/flake8-bugbear README.rst) — "It is commonly assumed that flags is the third positional parameter, forgetting about count/maxsplit, since many other re module functions are of the form f(pattern, string, flags)." (fetched)

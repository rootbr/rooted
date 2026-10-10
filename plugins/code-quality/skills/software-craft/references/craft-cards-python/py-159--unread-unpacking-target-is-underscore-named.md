---
title: A Python unpacking target the code never reads is named _ or with a leading underscore, and a local named with a leading underscore is never read
rule_id: PY-159
domain: code
step: [implement, refactor]
applies_to: [python]
triggers: ['^\s*[A-Za-z_]\w*\s*,\s*[A-Za-z_][\w, ]*=\s*[^=]', '^\s*for\s+\(?\s*[A-Za-z_]\w*\s*,\s*[A-Za-z_][\w, ]*\)?\s+in\b', '(?<![\w.])_[a-z]\w*\b']
scope: file
check_kind: semantic
severity_default: minor
---

# A Python unpacking target the code never reads is named _ or with a leading underscore, and a local named with a leading underscore is never read

## Thesis
A position of a Python tuple or list unpacking assignment, or of a `for` target that destructures each item, whose value the code never reads is named `_` or given a leading underscore; and a local variable of a function whose name starts with an underscore is not read, with `_` itself and dunder names outside this second half.

## Rationale
An unpacking assignment without a starred target requires an iterable with the same number of items as there are targets and assigns the items, from left to right, to the corresponding targets, so an unread position cannot be dropped without changing the unpacking. A variable that is defined but never used can confuse readers, and a leading underscore, or a name matching the configured dummy-variable pattern, marks the binding as intentionally unused; in a loop target the same prefix marks a variable kept only to destructure a tuple or other object. A leading underscore on a local conveys that it is intentionally unused within the function, so a later read of it causes confusion and suggests either that the variable could be given a clearer name or that the code is accidentally making use of the wrong variable.

## Example
```python
bad:  def describe(path, pairs):
          stem, ext = os.path.splitext(path)
          for _key, value in pairs:
              print(stem, _key, value)
good: def describe(path, pairs):
          stem, _ = os.path.splitext(path)
          for key, value in pairs:
              print(stem, key, value)
```

## Limits
Two positions meet on an unread binding: one removes a variable that is defined but not used, as likely a mistake; the other keeps an intentionally unused variable of an unpacked assignment under an underscore name. The separating condition is the binding's form: the removal check does not apply to bindings in unpacked assignments, the underscore check applies only to unpacked assignments, and an unused loop variable that is not intended to be kept, as one that facilitates destructuring of a tuple is, is removed entirely. The second half covers local variables in function scopes only; a module-level or class-level name with a single leading underscore is a weak internal-use indicator. A leading underscore is sometimes used to avoid shadowing another variable, a Python builtin or a keyword, and trailing underscores, such as `id_`, are recommended for this rather than leading underscores. The dummy-variable pattern is a project setting, `lint.dummy-variable-rgx`; where a project sets it, that pattern, not the leading underscore, marks an unused binding.

## Validator
Grep the hunk for tuple or list unpacking assignments, destructuring `for` targets and names with one leading underscore. For each unpacking position, search the binding's scope in the file for a read of that name; for each underscore-named local of a function, search the function for a read other than its own assignment, skipping `_` and dunder names. Read the project's `lint.dummy-variable-rgx` when it is set and use its pattern in place of the leading underscore. Validator question: **Does the hunk bind an unpacking or loop-destructuring position that the code never reads under a name without the underscore marker, or read a function local whose name marks it as unused?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-159`, severity minor, `file`, `symbol`, `code` = the unpacking target or the read of the underscore-named local verbatim from the diff, `fix` = the unread position renamed `_` or `_name`, or the read local renamed without the leading underscore, with a trailing underscore where it avoids shadowing, in Python, `rationale` = the unpacking binds every position so the unread one is marked rather than dropped, or the read contradicts the unused marker and may be the wrong variable).

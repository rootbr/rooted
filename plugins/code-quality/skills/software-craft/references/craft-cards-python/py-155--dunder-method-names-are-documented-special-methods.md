---
title: A Python method whose name begins and ends with underscores is a special method the language documents, never a misspelled or invented dunder
rule_id: PY-155
domain: code
step: [design, implement]
applies_to: [python, object-oriented]
triggers: ['def\s+__\w+__\s*\(', 'def\s+_[a-z]\w*[a-z0-9]_\s*\(', 'def\s+__[a-z]\w*[a-z0-9]_\s*\(']
scope: hunk
check_kind: mechanical
severity_default: major
---

# A Python method whose name begins and ends with underscores is a special method the language documents, never a misspelled or invented dunder

## Thesis
A Python method whose name begins and ends with an underscore, such as `__lenght__`, `__init_` or `_str_`, carries exactly the name of a special method that Python or its standard library defines, or a name the project lists as allowed in its linter configuration; a misspelled, invented or no longer supported name of that shape is renamed to the documented method it was meant to be, or to a plain name.

## Rationale
A class implements operations invoked by special syntax, such as arithmetic operations or subscripting and slicing, by defining methods with special names, so a method whose name misses the documented spelling, such as `__lenght__` for `__len__`, the method called to implement the built-in function `len()`, is not the method that operation uses. Misspelled or no longer supported dunder names may cause the code to not function as expected. The `__*__` names are system-defined: the interpreter and its implementation, including the standard library, define them, more will likely be defined in future versions of Python, and any use of a `__*__` name that does not follow explicitly documented use is subject to breakage without warning.

## Example
```python
bad:  class Inventory:
          def __lenght__(self):
              return len(self.items)
good: class Inventory:
          def __len__(self):
              return len(self.items)
```

## Limits
A method marked `@override`, and a name the project adds to the allowed list of the linter (`lint.pylint.allow-dunder-method-names` in the Ruff configuration), are outside the rule. The rule reaches methods, those starting and ending with at least one underscore; a module-level function is outside it.

## Validator
Grep the hunk for `def` of a method whose name begins and ends with an underscore. Compare the name with the special method names of the data model and the standard library (for instance `__init__`, `__repr__`, `__len__`, `__getitem__`, `__eq__`, `__hash__`, `__enter__`, `__exit__`, `__init_subclass__`, `__class_getitem__`, `__post_init__`); open the method's decorators for `@override` and the project's lint configuration for `lint.pylint.allow-dunder-method-names` (Ruff) or `good-dunder-names` (Pylint). Validator question: **Does the hunk define a method in a class whose name begins and ends with an underscore, is not a special method name that Python or its standard library documents, is not in the configured allowed list and is not marked `@override`?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-155`, severity major, `file`, `symbol`, `code` = the `def` line verbatim from the diff, `fix` = the method under the documented name it was meant to be, `def __len__(self):`, or under a plain name without the surrounding underscores, `rationale` = names that Python uses a special method only under its documented name, so the misspelled method is not the one the operation calls, and that undocumented `__*__` names are subject to breakage without warning).

## Source
- CPython Doc/reference/lexical_analysis.rst §Reserved classes of identifiers (https://raw.githubusercontent.com/python/cpython/main/Doc/reference/lexical_analysis.rst) — 'System-defined names, informally known as "dunder" names. These names are defined by the interpreter and its implementation (including the standard library).'; 'More will likely be defined in future versions of Python.'; '*Any* use of ``__*__`` names, in any context, that does not follow explicitly documented use, is subject to breakage without warning.' (fetched)
- CPython Doc/reference/datamodel.rst §Special method names and §Emulating container types (https://raw.githubusercontent.com/python/cpython/main/Doc/reference/datamodel.rst) — 'A class can implement certain operations that are invoked by special syntax (such as arithmetic operations or subscripting and slicing) by defining methods with special names.'; 'Called to implement the built-in function :func:`len`.' (fetched)
- Ruff PLW3201 bad-dunder-method-name (astral-sh/ruff crates/ruff_linter/src/rules/pylint/rules/bad_dunder_method_name.rs) — 'Misspelled or no longer supported dunder name methods may cause your code to not function as expected.'; 'This rule will detect all methods starting and ending with at least one underscore (e.g., `_str_`), but ignores known dunder methods (like `__init__`), as well as methods that are marked with [`@override`][override].'; 'Additional dunder methods names can be allowed via the [`lint.pylint.allow-dunder-method-names`] setting.' (fetched)
- Pylint bad-dunder-name (W3201) (pylint-dev/pylint pylint/extensions/dunder.py) — 'Used when a dunder method is misspelled or defined with a name not within the predefined list of dunder names.' (fetched)
- Caveat: neither linter runs the check by default; the Ruff rule is in preview (preview_since v0.0.285 in its source) and the Pylint checker ships as the optional extension pylint.extensions.dunder.

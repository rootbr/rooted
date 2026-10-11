---
title: A Python method that overrides a base method accepts every call the base accepts, including keyword calls by the base's parameter names
rule_id: PY-66
domain: design
step: [design, implement, review]
applies_to: [python, object-oriented, public-api]
triggers: ['^\s+def (?!__)\w+\(self', '@(typing[.]|typing_extensions[.])?override\b']
scope: file
check_kind: semantic
severity_default: major
---

# A Python method that overrides a base method accepts every call the base accepts, including keyword calls by the base's parameter names

## Thesis
A Python method that overrides a base-class method is callable with the same parameters as the method it overrides: it removes no parameter, even one with a default value; adds no parameter without a default value; removes no default value; reorders no parameters except keyword-only ones; removes no `*args` or `**kwargs`; and removes no way of providing a parameter, so a parameter that could be passed by keyword can still be passed by keyword under the same name.

## Rationale
A subclass instance may be used as an instance of its base class, so the override receives the calls written against the overridden method's parameters. A parameter of the default kind, positional-or-keyword, can be passed either positionally or as a keyword argument, which makes its name part of what callers may use: once an override renames it, the argument can no longer be passed by keyword. Renaming a positional-only parameter keeps the override compatible, and positional-only parameters were introduced in Python 3.8 to solve this problem. A type checker compares the two signatures: it checks that an override of a statically typed method has a compatible signature, reports an override that adds an argument without a default (`too many arguments`), and accepts one that adds an argument with a default because it accepts more than the base class method.

## Example
```python
bad:  class Orange(Fruit):
          def brew(self, flavor: str) -> None: ...
      fruit.brew(ingredient_name="thyme")  # TypeError when fruit is an Orange
good: class Orange(Fruit):
          def brew(self, ingredient_name: str) -> None: ...
      fruit.brew(ingredient_name="thyme")
      # or the base declares: def brew(self, ingredient_name: str, /) -> None
```

## Limits
An override stays compatible when it adds a parameter with a default value as long as the order of positional parameters does not change, places new positional parameters at the end, adds `*args` or `**kwargs`, adds or changes a default value, reorders keyword-only parameters, renames a positional-only parameter, or turns a keyword-only or positional-only parameter into a positional-or-keyword one without changing the order of positional parameters. Renaming alone is contested. One position reports a method parameter that has a different name than in the overridden method. The other position does not: renaming parameters in theory breaks keyword calls, but positional-only parameters were introduced in Python 3.8 and most programs will need to support older versions, so it raises no issue on renamed parameters while calling a rename suspicious and pointing to the base's name or a positional-only parameter. The supported Python range separates the cases: on code limited to Python 3.8 or later the base parameter can be declared positional-only, so a renamed keyword-passable parameter there is a finding; code that must also run before 3.8 is held only to the other changes the Thesis lists.

## Validator
Grep the hunk for a method `def` whose first parameter is `self` and for `@override`. Open the file at the class that holds it, find the base class that defines a method of the same name (follow the import when the base lives in another module), and set the two parameter lists side by side. Check in order: every base parameter is present; positional parameters keep their positions; a parameter that had a default keeps one; every added parameter has a default or is `*args` or `**kwargs`; the base's `*args` and `**kwargs` remain; every base parameter that is not before a `/` keeps its name. When a rename is the only change, read the project's `requires-python`: a range that admits versions before 3.8 clears it. Validator question: **Does the override reject a call the overridden method accepts — through a removed parameter, an added parameter without a default, a removed default, a changed positional order, a removed `*args` or `**kwargs`, or, on code limited to Python 3.8 or later, a keyword-passable parameter under a new name?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-66`, severity major, `file`, `symbol`, `code` = the override's `def` line quoted verbatim from the diff, `fix` = the override's Python signature restored to accept the base's calls — the base's parameter names and positional order, each added parameter with a default — or the base parameter declared positional-only with `/`, `rationale` = the call through the base type that the override rejects and the parameter it concerns).

## Source
- SonarSource python S2638 (SonarSource/sonar-python python-checks/src/main/resources/org/sonar/l10n/py/rules/python/S2638.html) — 'Because a subclass instance may be used as an instance of the superclass' ... 'an overriding method should be callable with the same parameters as the overriden one' ... 'Removing parameters, even when they have default values.' ... 'Adding mandatory parameters, i.e. without a default value.' ... 'Removing the default value of a parameter.' ... 'Reordering parameters, except when they are keyword-only parameters.' ... 'Removing a vararg parameter (*args).' ... 'Removing a keywords parameter (**kwargs).' ... 'If a parameter could be passed as keyword it should still be possible to pass it as keyword' ... 'Adding an optional parameter, i.e. with a default value, as long as they don’t change the order of positional parameters.' ... 'Renaming a positional-only parameter.' ... 'Reordering keyword-only parameters.' ... 'Adding a default value to an existing parameter.' ... 'Changing the default value of an existing parameter.' ... 'change a keyword-only or positional-only parameter to a keyword-or-positional parameter' ... 'New positional parameters should be placed at the end.' ... 'Adding a vararg parameter (*args).' ... 'Adding a keywords parameter (**kwargs).' ... 'No issue but this is suspicious. Rename this parameter as "param1" or use positional only arguments if possible.' ... 'In theory, renaming parameters also breaks Liskov Substitution Principle. Arguments can’t be passed via keyword arguments anymore.' ... '"Positional-Only Parameters" were introduced in Python 3.8 to solve this problem. As most programs will need to support older versions of Python, this rule won’t raise an issue on renamed parameters.' (fetched)
- Pylint arguments-renamed (W0237) (https://pylint.readthedocs.io/en/stable/user_guide/messages/warning/arguments-renamed.html) — 'Used when a method parameter has a different name than in the implemented interface or in an overridden method.' (fetched)
- CPython Doc/glossary.rst §parameter (https://raw.githubusercontent.com/python/cpython/main/Doc/glossary.rst) — 'specifies an argument that can be passed' ... 'This is the default kind of parameter' (fetched)
- mypy docs class_basics.rst §Overriding statically typed methods (https://raw.githubusercontent.com/python/mypy/master/docs/source/class_basics.rst) — 'When overriding a statically typed method, mypy checks that the override has a compatible signature' ... '# Error: too many arguments' ... '# OK: accepts more than the base' (fetched)
- Caveat: SonarSource S2638 considers instance methods only; class methods and static methods are ignored.

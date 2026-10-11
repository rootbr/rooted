---
title: On a project whose minimum Python is 3.12 or later, a generic class, function or type alias declares its type parameters in brackets rather than through a module-level TypeVar and a Generic base
rule_id: PY-27
domain: code
step: [implement, refactor]
applies_to: [python, static-types]
triggers: ['=\s*(typing[.])?(TypeVar|ParamSpec|TypeVarTuple)\(', '\bGeneric\[']
scope: file
check_kind: mechanical
severity_default: suggestion
---

# On a project whose minimum Python is 3.12 or later, a generic class, function or type alias declares its type parameters in brackets rather than through a module-level TypeVar and a Generic base

## Thesis
On a project whose minimum supported Python is 3.12 or later, a generic class, function or type alias declares its type parameters in brackets after its name (`class Box[T]:`, `def first[T](items: list[T]) -> T:`, `type Pair[T] = tuple[T, T]`) rather than through a module-level `TypeVar` or `ParamSpec` and a `Generic[T]` base, and a `type` statement takes no `TypeVar` allocated by a constructor call. A `TypeVar` declared `covariant` or `contravariant` is converted only after checking the variance the bracket form infers.

## Rationale
Type parameter syntax was introduced in Python 3.12 by PEP 695 for defining generic classes and functions; it is easier to read and gives cleaner support for generics. A traditional type variable is typically allocated within the global scope, but its meaning is valid only within the generic class, function or type alias that uses it, and the bracket syntax removes this confusion by declaring each type parameter at its point of use. The traditional form also needs imports of `TypeVar` and `Generic` and the explicit definition of a type variable in the global scope with a redundant name in quotes. A type alias expression is not allowed to use a traditional type variable allocated with an explicit `TypeVar` constructor call, and type checkers should report that as an error. The bracket syntax carries no `covariant` or `contravariant` keyword: type checkers infer the variance of a type parameter from its usage within the class, so replacing a `TypeVar` declared with those keywords by an inline type parameter may change its variance. A bound moves into the brackets (`class Box[T: str]:`), and a bound shared by several generics becomes a type alias used as the bound, which keeps both the bracket syntax and the reuse of the bound.

## Example
```python
bad:  from typing import Generic, TypeVar
      T = TypeVar("T")
      class Box(Generic[T]):
          item: T
good: class Box[T]:
          item: T
      def first[T](items: list[T]) -> T:
          return items[0]
```

## Limits
The separating condition is the project's minimum supported Python. The checks for this syntax raise an issue only when the analysed project's Python version is set to 3.12 or higher, and they rest on the syntax introduced in Python 3.12. Below 3.12 the module-level `TypeVar` or `ParamSpec` is the available form, and a type variable such as `TypeVar` and `ParamSpec` is a common way to use generics. A type parameter with the `default` argument introduced in PEP 696 and implemented in Python 3.13, and a generic class nested inside another function or class, are skipped by the automatic checks. A type checker that does not fully support PEP 695 may reject a valid conversion, so the converted file is type-checked before the finding closes. Where the project's Python version is not set to 3.12 or higher, the rule does not apply.

## Validator
Establish the project's minimum supported Python from `requires-python` in `pyproject.toml` or the `target-version` or `python_version` setting of Ruff or mypy; when it is below 3.12 or cannot be established, stop. Grep the file for `= TypeVar(`, `= ParamSpec(`, `= TypeVarTuple(` and `Generic[`. For each type variable, find the classes, functions and type aliases that use it, and note `covariant=`, `contravariant=`, `bound=` and `default=` in its constructor call. Validator question: **On a project whose minimum supported Python is 3.12 or later, does a generic class, function or type alias in the file take its type parameters from a module-level `TypeVar` or `ParamSpec` or a `Generic[...]` base rather than from brackets after its name?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-27`, severity suggestion, `file`, `symbol`, `code` = the `TypeVar` or `ParamSpec` assignment and the generic's header quoted verbatim, `fix` = the header with bracketed parameters, such as `class Box[T]:` or `def first[T](items: list[T]) -> T:`, with any bound moved into the brackets and a variance-declared `TypeVar` named for a hand check, `rationale` = PEP 695 type parameter syntax from Python 3.12 declares each parameter at its point of use and infers its variance).

## Source
- PEP 695 §Points of Confusion (https://raw.githubusercontent.com/python/peps/main/peps/pep-0695.rst) — 'Type variables are typically allocated within the global scope, but their semantic meaning is valid only when used within the context of a generic class, function, or type alias.' (fetched)
- PEP 695 §Type Alias Statement (https://raw.githubusercontent.com/python/peps/main/peps/pep-0695.rst) — 'Type alias expressions are not allowed to use traditional type variables (i.e. those allocated with an explicit ``TypeVar`` constructor call). Type checkers should generate an error in this case.' (fetched)
- PEP 695 §Variance Inference (https://raw.githubusercontent.com/python/peps/main/peps/pep-0695.rst) — 'type checkers will infer the variance of type parameters based on their usage within a class.' (fetched)
- Ruff UP046 non-pep695-generic-class (astral-sh/ruff crates/ruff_linter/src/rules/pyupgrade/rules/pep695/non_pep695_generic_class.rs) — 'Special type parameter syntax was introduced in Python 3.12 by [PEP 695] for defining generic classes. This syntax is easier to read and provides cleaner support for generics.' (fetched)
- Ruff UP046 non-pep695-generic-class (astral-sh/ruff crates/ruff_linter/src/rules/pyupgrade/rules/pep695/non_pep695_generic_class.rs) — 'by declaring type parameters at their point of use.' (fetched)
- Ruff UP046 non-pep695-generic-class (astral-sh/ruff crates/ruff_linter/src/rules/pyupgrade/rules/pep695/non_pep695_generic_class.rs) — 'Checks for use of standalone type variables and parameter specifications in generic classes.' (fetched)
- Ruff UP046 non-pep695-generic-class (astral-sh/ruff crates/ruff_linter/src/rules/pyupgrade/rules/pep695/non_pep695_generic_class.rs) — 'replacing a `TypeVar` variable with an inline type parameter may change its variance.' (fetched)
- Ruff UP046 non-pep695-generic-class (astral-sh/ruff crates/ruff_linter/src/rules/pyupgrade/rules/pep695/non_pep695_generic_class.rs) — 'You can instead extract the bound as a [type alias] to retain both the benefits of the PEP 695 syntax and the reuse of the bound' (fetched)
- Ruff UP046 non-pep695-generic-class (astral-sh/ruff crates/ruff_linter/src/rules/pyupgrade/rules/pep695/non_pep695_generic_class.rs) — 'It also skips type parameters with the `default` argument introduced in [PEP 696] and implemented in Python 3.13.' (fetched)
- Ruff UP046 non-pep695-generic-class (astral-sh/ruff crates/ruff_linter/src/rules/pyupgrade/rules/pep695/non_pep695_generic_class.rs) — 'The rule currently skips generic classes nested inside of other functions or classes.' (fetched)
- Ruff UP046 non-pep695-generic-class (astral-sh/ruff crates/ruff_linter/src/rules/pyupgrade/rules/pep695/non_pep695_generic_class.rs) — 'Not all type checkers fully support PEP 695 yet, so even valid fixes suggested by this rule may cause type checking to' (fetched)
- Ruff UP047 non-pep695-generic-function (astral-sh/ruff crates/ruff_linter/src/rules/pyupgrade/rules/pep695/non_pep695_generic_function.rs) — 'Special type parameter syntax was introduced in Python 3.12 by [PEP 695] for defining generic functions.' (fetched)
- SonarSource python S6792 (SonarSource/sonar-python python-checks/src/main/resources/org/sonar/l10n/py/rules/python/S6792.html) — 'It is therefore recommended to use the type parameter syntax when working with Python 3.12 and later.' (fetched)
- SonarSource python S6792 (SonarSource/sonar-python python-checks/src/main/resources/org/sonar/l10n/py/rules/python/S6792.html) — 'Using the former syntax requires importing TypeVar and Generic symbols from the typing module.' (fetched)
- SonarSource python S6792 (SonarSource/sonar-python python-checks/src/main/resources/org/sonar/l10n/py/rules/python/S6792.html) — 'It also requires the explicit definition of a type variable in the global scope, with a redundant name provided in quotes' (fetched)
- SonarSource python S6792 (SonarSource/sonar-python python-checks/src/main/resources/org/sonar/l10n/py/rules/python/S6792.html) — 'class ClassA[T: str]:' (fetched)
- SonarSource python S6792 (SonarSource/sonar-python python-checks/src/main/resources/org/sonar/l10n/py/rules/python/S6792.html) — 'This rule will only raise an issue when the Python version of the analyzed project is set to 3.12 or higher.' (fetched)
- SonarSource python S6795 (SonarSource/sonar-python python-checks/src/main/resources/org/sonar/l10n/py/rules/python/S6795.html) — 'Python is transitioning away from explicit TypeVar declaration from Python 3.12 onward.' (fetched)
- SonarSource python S6796 (SonarSource/sonar-python python-checks/src/main/resources/org/sonar/l10n/py/rules/python/S6796.html) — 'This rule will only raise an issue when the Python version of the analyzed project is set to 3.12 or higher.' (fetched)
- Google Python Style Guide §3.19.10 Type variables (https://raw.githubusercontent.com/google/styleguide/gh-pages/pyguide.md) — 'A type variable, such as `TypeVar` and `ParamSpec`, is a common way to use them.' (fetched)
- Caveat: the rule binds only where the project targets Python 3.12 or later; below that the style-guide position holds.

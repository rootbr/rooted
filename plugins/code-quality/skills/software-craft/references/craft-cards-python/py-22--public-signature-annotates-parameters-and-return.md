---
title: A public function or method that a change adds or modifies annotates each parameter other than self and cls and its return type, and a private one is annotated wherever the project's type-checker settings require it
rule_id: PY-22
domain: code
step: [implement, review]
applies_to: [python, static-types]
triggers: ['^\s*(async\s+)?def\s+\w+\s*(\(|\(.*[(,])\s*\*{0,2}(?!self\b|cls\b)[A-Za-z_]\w*\s*(=[^,)]*)?\s*[,)]', '^\s*(async\s+)?def\s+\w+\s*\(.*\)\s*:']
scope: hunk
check_kind: mechanical
severity_default: minor
---

# A public function or method that a change adds or modifies annotates each parameter other than self and cls and its return type, and a private one is annotated wherever the project's type-checker settings require it

## Thesis
A public function or method, one whose name has no leading underscore and that belongs to the module's public API, that a change adds or modifies annotates every parameter other than `self` and `cls`, `*args` and `**kwargs` included, and its return type; `__init__` may leave out `-> None` when at least one of its parameters is annotated. A private function or method, one whose name starts with an underscore, carries the same annotations wherever the project's type checking requires them, as mypy's `--disallow-untyped-defs` or Ruff's flake8-annotations rules such as ANN202 do when enabled.

## Rationale
Mypy considers a function without type annotations dynamically typed and by default does not type check it, so, with a few exceptions, it reports no errors in unannotated code, even when the function is misused; such a call fails when the program runs. Annotated parameters and return types document the function's contract and, alongside a type checker, help catch bugs by ensuring that the types of the arguments callers provide and of the values the function returns match expectation. Under `--disallow-untyped-defs` mypy reports any function definition without type annotations or with incomplete ones, so a partly annotated signature is reported too.

## Example
```python
bad:  def load_user(user_id, *, cache=None):
          return (cache or default_cache()).get(user_id)
good: def load_user(user_id: int, *, cache: Cache | None = None) -> User:
          return (cache or default_cache()).get(user_id)
```

## Limits
How far annotation reaches is contested, and the separating condition is whether the function is public API and how the project's checker is configured. Ruff's flake8-annotations rules, when the project selects them, flag every function or method, public or private, whose parameters or return type lack annotations (ANN202 checks that private functions and methods have return type annotations), and one position holds that applying type hints consistently makes the code easier to read and understand. Another position requires type annotations when public APIs are added or modified, holds that not every function of a module has to be annotated and leaves the rest to judgment between safety and flexibility. Mypy leaves unannotated functions unchecked by default and reports every one under `--disallow-untyped-defs`. So a public function that a change adds or modifies is annotated, a private one is annotated where the project enables such a flag or rule, and an unannotated private function elsewhere is a judgment call this rule does not flag. Functions the change leaves untouched are outside the rule; annotating `self` or `cls` is generally not necessary.

## Validator
Grep the hunk for the `def` and `async def` lines it adds or changes. For each, list its parameters other than `self` and `cls`, `*args` and `**kwargs` included, and its return annotation; accept a missing `-> None` on `__init__` when one of its parameters is annotated. A name without a leading underscore is public: check every parameter and the return. For a name with a leading underscore, open the project's checker configuration (`pyproject.toml`, `setup.cfg`, `mypy.ini`, `ruff.toml`) and check the definition only when `disallow_untyped_defs` covers its module or Ruff selects the ANN rules. Validator question: **Does a def that the hunk adds or modifies, public or held to annotation by the project's checker settings, leave a parameter other than self and cls, or its return type, without an annotation?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-22`, severity minor, `file`, `symbol`, `code` = the `def` line as the diff writes it, `fix` = the same signature with each parameter and the return annotated, in Python, `rationale` = names the parameters or the return left unannotated and whether the function is public or held to annotation by the project's checker setting).

## Source
- Ruff ANN001 missing-type-function-argument (astral-sh/ruff crates/ruff_linter/src/rules/flake8_annotations/rules/definition.rs) — "Type annotations are a good way to document the types of function arguments. They also help catch bugs, when used alongside a type checker, by ensuring that the types of any provided arguments match expectation." (fetched)
- Ruff ANN002 missing-type-args (astral-sh/ruff crates/ruff_linter/src/rules/flake8_annotations/rules/definition.rs) — "Checks that function `*args` arguments have type annotations." (fetched)
- Ruff ANN003 missing-type-kwargs (astral-sh/ruff crates/ruff_linter/src/rules/flake8_annotations/rules/definition.rs) — "Checks that function `**kwargs` arguments have type annotations." (fetched)
- Ruff ANN201 missing-return-type-undocumented-public-function (astral-sh/ruff crates/ruff_linter/src/rules/flake8_annotations/rules/definition.rs) — "Type annotations are a good way to document the return types of functions. They also help catch bugs, when used alongside a type checker, by ensuring that the types of any returned values, and the types expected by callers, match expectation." (fetched)
- Ruff ANN202 missing-return-type-private-function (astral-sh/ruff crates/ruff_linter/src/rules/flake8_annotations/rules/definition.rs) — "Checks that private functions and methods have return type annotations." (fetched)
- Ruff ANN204 missing-return-type-special-method (astral-sh/ruff crates/ruff_linter/src/rules/flake8_annotations/rules/definition.rs) — "Note that type checkers often allow you to omit the return type annotation for `__init__` methods, as long as at least one argument has a type annotation." (fetched)
- Ruff ANN205 missing-return-type-static-method (astral-sh/ruff crates/ruff_linter/src/rules/flake8_annotations/rules/definition.rs) — "Checks that static methods have return type annotations." (fetched)
- Ruff ANN206 missing-return-type-class-method (astral-sh/ruff crates/ruff_linter/src/rules/flake8_annotations/rules/definition.rs) — "Checks that class methods have return type annotations." (fetched)
- SonarSource python S6538 (SonarSource/sonar-python python-checks/src/main/resources/org/sonar/l10n/py/rules/python/S6538.html) — "Type hints can be used to clarify the expected return type of a function, enabling developers to better document its contract. Applying them consistently makes the code easier to read and understand." (fetched)
- SonarSource python S6540 (SonarSource/sonar-python python-checks/src/main/resources/org/sonar/l10n/py/rules/python/S6540.html) — "Type hints can be used to clarify the expected parameters of a function, enabling developers to better document its contract." (fetched)
- mypy docs §Dynamic vs static typing (python/mypy docs/source/getting_started.rst) — "By default, mypy will **not** type check dynamically typed functions. This means that with a few exceptions, mypy will not report any errors with regular unannotated Python." (fetched)
- mypy docs §Dynamic vs static typing (python/mypy docs/source/getting_started.rst) — "This is the case even if you misuse the function!" (fetched)
- mypy docs §Dynamic vs static typing (python/mypy docs/source/getting_started.rst) — "A function without type annotations is considered to be *dynamically typed* by mypy" (fetched)
- mypy docs §Dynamic vs static typing (python/mypy docs/source/getting_started.rst) — "These calls will fail when the program runs, but mypy does not report an error" (fetched)
- mypy docs §--disallow-untyped-defs (python/mypy docs/source/command_line.rst) — "This flag reports an error whenever it encounters a function definition without type annotations or with incomplete type annotations." (fetched)
- Google Python Style Guide §2.21.4 Decision (google/styleguide pyguide.md) — "When adding or modifying public APIs, include type annotations and enable checking via pytype in the build system." (fetched)
- Google Python Style Guide §3.19.1 General Rules (google/styleguide pyguide.md) — "Similarly, don't feel compelled to annotate the return value of `__init__` (where `None` is the only valid option)." (fetched)
- Google Python Style Guide §3.19.1 General Rules (google/styleguide pyguide.md) — "You are not required to annotate all the functions in a module." (fetched)
- Google Python Style Guide §3.19.1 General Rules (google/styleguide pyguide.md) — "At least annotate your public APIs." (fetched)
- Google Python Style Guide §3.19.1 General Rules (google/styleguide pyguide.md) — "Use judgment to get to a good balance between safety and clarity on the one hand, and flexibility on the other." (fetched)
- Google Python Style Guide §3.19.1 General Rules (google/styleguide pyguide.md) — "Annotating `self` or `cls` is generally not necessary." (fetched)

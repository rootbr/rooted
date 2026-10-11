---
title: A Python 3.15 lazy import is not used by code that runs while its module loads, and an import such code needs is a plain import
rule_id: PY-169
domain: design
step: [implement, review]
applies_to: [python]
triggers: ['^lazy\s+import\s+\w', '^lazy\s+from\s+\S+\s+import\s', '^__lazy_modules__\s*=']
scope: file
check_kind: semantic
severity_default: minor
---

# A Python 3.15 lazy import is not used by code that runs while its module loads, and an import such code needs is a plain import

## Thesis
A name bound by `lazy import` or `lazy from ... import` (Python 3.15), or by an import that a literal `__lazy_modules__` declaration makes lazy, is used only by code that runs after its module has loaded; an import that a module global or a top-level class definition uses is written as a plain import.

## Rationale
A lazy import does not load the module at the import statement: a lazy proxy object is created and bound to the name, and the actual module is loaded on first use of that name; with `lazy from ... import`, the first access to any of the imported names triggers loading of the entire module. When a lazily imported name is used at module load time, the import is resolved eagerly, defeating the purpose of marking it lazy. The common causes are a module global and a top-level class definition that use the lazily imported module, and a decorator that evaluates annotations, such as `@dataclasses.dataclass`, can immediately resolve a lazy import used in a field annotation. Where lazy imports are meant to untangle an import cycle, they might help only if the circular reference is not accessed during module initialization; if either module accesses the other during import time, the error still comes.

## Example
```python
bad:  __lazy_modules__ = ["schemas"]
      import schemas
      lazy import plugins
      lazy from loaders import Loader
      class Handler(Loader, schemas.Base, plugins.Mixin): ...
good: import plugins
      import schemas
      from loaders import Loader
      class Handler(Loader, schemas.Base, plugins.Mixin): ...
```

## Limits
A function or method body that runs only when called after the module has loaded may use a lazy name: the access happens later, when the function is called. Writing the import plain changes when the imported module is executed, which can change runtime behaviour if that module has import-time side effects; moving the load-time use into a function keeps the import lazy. On Python versions before 3.15, `__lazy_modules__` is simply ignored and the imports it names proceed eagerly as normal. An import that the project's `lint.flake8-tidy-imports.require-lazy` setting requires to be lazy is outside the rule.

## Validator
Grep the file for `lazy import`, `lazy from ... import` and a literal `__lazy_modules__` assignment, and for the last collect the plain imports of the modules it lists. Trace each lazily bound name to every use in code that runs while the module executes: module-level statements and global initializers; the bases, keywords, decorators and body of a top-level class; the decorators and default argument values of a top-level function; a function the module calls at load time; a field annotation of a class whose decorator evaluates annotations, such as `@dataclasses.dataclass`. A use inside a function or method body that nothing calls during the import does not count. Validator question: **Is a lazily imported name used by code that runs while its own module is being imported?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-169`, severity minor, `file`, `symbol`, `code` = the lazy import line and the module-level line that uses its name, `fix` = the import written as a plain `import`, or the use moved into a function body, `rationale` = that a use at module load resolves the lazy import eagerly, defeating the purpose of marking it lazy).

## Source
- Ruff TID255 lazy-import-immediately-resolved (astral-sh/ruff crates/ruff_linter/src/rules/flake8_tidy_imports/rules/lazy_import_immediately_resolved.rs) — 'When a lazily imported name is used immediately at module load time, the import is resolved eagerly, defeating the purpose of marking the import as lazy. This is commonly caused by using a lazily imported module in a module global or in a top-level class definition.' (fetched)
- Ruff TID255 lazy-import-immediately-resolved (astral-sh/ruff crates/ruff_linter/src/rules/flake8_tidy_imports/rules/lazy_import_immediately_resolved.rs) — 'The rule also recognizes imports made lazy by a literal `__lazy_modules__` declaration, even when the target version is older than Python 3.15.' (fetched)
- Ruff TID255 lazy-import-immediately-resolved (astral-sh/ruff crates/ruff_linter/src/rules/flake8_tidy_imports/rules/lazy_import_immediately_resolved.rs) — 'Ruff does not detect all cases where decorators evaluate annotations. For example, `@dataclasses.dataclass` can immediately resolve lazy imports used in field annotations without triggering this rule.' (fetched)
- Ruff TID255 lazy-import-immediately-resolved (astral-sh/ruff crates/ruff_linter/src/rules/flake8_tidy_imports/rules/lazy_import_immediately_resolved.rs) — 'converting a lazy import to an eager import changes when the imported module is executed, which can change runtime behavior if the module has import-time side effects.' (fetched)
- Ruff TID255 lazy-import-immediately-resolved (astral-sh/ruff crates/ruff_linter/src/rules/flake8_tidy_imports/rules/lazy_import_immediately_resolved.rs) — 'The rule ignores imports required to be lazy by the following setting:' (fetched)
- PEP 810 §Semantics (https://raw.githubusercontent.com/python/peps/main/peps/pep-0810.rst) — 'The module is not loaded immediately at the import statement; instead, a lazy proxy object is created and bound to the name. The actual module is loaded on first use of that name.' (fetched)
- PEP 810 §Semantics (https://raw.githubusercontent.com/python/peps/main/peps/pep-0810.rst) — 'The first access to **any** of these names triggers loading of the entire module' (fetched)
- PEP 810 §Do lazy imports work with circular imports? (https://raw.githubusercontent.com/python/peps/main/peps/pep-0810.rst) — 'making the imports lazy might help **only if** the circular reference isn’t accessed during module initialization. However, if either module accesses the other during import time, you’ll still get an error.' (fetched)
- PEP 810 §Do lazy imports work with circular imports? (https://raw.githubusercontent.com/python/peps/main/peps/pep-0810.rst) — 'This works because neither module accesses the other at module level … the access happens later when ``get_posts()`` is called.' (fetched)
- PEP 810 §What about forwards compatibility with older Python versions? (https://raw.githubusercontent.com/python/peps/main/peps/pep-0810.rst) — 'On Python versions before 3.15 that don’t support lazy imports, the `__lazy_modules__` attribute is simply ignored and imports proceed eagerly as normal.' (fetched)
- Caveat: PEP 810 is Final with Python-Version 3.15; TID255 is off by default.

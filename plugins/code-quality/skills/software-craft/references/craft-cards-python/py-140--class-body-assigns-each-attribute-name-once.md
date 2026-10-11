---
title: A Python class body assigns each class attribute or field name once
rule_id: PY-140
domain: design
step: [implement, review]
applies_to: [python, object-oriented]
triggers: ['^ {4}[A-Za-z_]\w*\s*(?::[^=]+)?=[^=]', '^ {4}[A-Za-z_]\w*\s*:\s*[^=]+$']
scope: file
check_kind: mechanical
severity_default: minor
---

# A Python class body assigns each class attribute or field name once

## Thesis
Within one Python class body each class attribute or field name is assigned once, and a repeated assignment is resolved by deciding which value was intended rather than by deleting one of them mechanically.

## Rationale
A class body is executed in a new execution frame with a newly created local namespace, and the class object is created with that saved namespace as its attribute dictionary. A name that is already bound is rebound by a second assignment, so a repeated assignment in the class body replaces the first value and only the last one reaches the class. Defining a field multiple times in a class body is redundant and likely a mistake, and which assignment was intended cannot be known for certain.

## Example
```python
bad:  class Person:
          name = 'Tom'
          age = 30
          name = 'Ben'
good: class Person:
          name = 'Tom'
          age = 30
```

## Limits
A reassignment whose value reads the same name, such as `count = count + 1`, is an unrolled augmented assignment and not a duplicate. The rule reaches assignment statements whose target is a single name, annotated or not; a tuple target and a repeated method definition fall outside it. In an `Enum` body two members with the same name are invalid and class creation raises `TypeError`, so that duplicate already fails when the class is created.

## Validator
For each assignment or annotation the hunk adds or changes directly in a class body, collect every name assigned or annotated directly in that same class body — the whole class, not only the hunk — and skip a reassignment whose value reads the same name. Validator question: **Is a class attribute or field name assigned or annotated more than once directly in the same class body, other than by a reassignment that reads its own earlier value?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-140`, severity minor, `file`, `symbol`, `code` = both assignments of the name, `fix` = one assignment of the name holding the value that was intended, `rationale` = the name, the value the later assignment silently discards and the value that reaches the class).

## Source
- Ruff PIE794 duplicate-class-field-definition (astral-sh/ruff crates/ruff_linter/src/rules/flake8_pie/rules/duplicate_class_field_definition.rs) — 'Defining a field multiple times in a class body is redundant and likely a mistake.' ; 'This fix is always marked as unsafe since we cannot know for certain which assignment was intended.' (fetched)
- Source of crates/ruff_linter/src/rules/flake8_pie/rules/duplicate_class_field_definition.rs §duplicate_class_field_definition (astral-sh/ruff crates/ruff_linter/src/rules/flake8_pie/rules/duplicate_class_field_definition.rs) — 'If this is an unrolled augmented assignment (e.g., `x = x + 1`), skip it.' ; 'let [Expr::Name(target)] = targets.as_slice() else {' ; 'Stmt::AnnAssign(ast::StmtAnnAssign { target, value, .. }) => {' ; '_ => continue,' (fetched)
- CPython Doc/reference/compound_stmts.rst §Class definitions (python/cpython Doc/reference/compound_stmts.rst) — 'The class's suite is then executed in a new execution frame' ; 'using a newly created local namespace and the original global namespace.' ; 'the saved local namespace for the attribute dictionary.' (fetched)
- CPython Doc/reference/simple_stmts.rst §Assignment statements (python/cpython Doc/reference/simple_stmts.rst) — 'The name is rebound if it was already bound.' (fetched)
- CPython Doc/howto/enum.rst §Duplicating enum members and values (python/cpython Doc/howto/enum.rst) — 'Having two enum members with the same name is invalid' ; 'TypeError: 'SQUARE' already defined as 2' (fetched)

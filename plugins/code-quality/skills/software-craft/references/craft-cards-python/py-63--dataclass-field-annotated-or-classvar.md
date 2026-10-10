---
title: Every attribute meant as a field of a Python dataclass carries a type annotation, and an attribute meant to be shared in it is annotated ClassVar
rule_id: PY-63
domain: design
step: [implement, review]
applies_to: [python, object-oriented]
triggers: ['@(dataclasses[.])?dataclass\b']
scope: file
check_kind: mechanical
severity_default: major
---

# Every attribute meant as a field of a Python dataclass carries a type annotation, and an attribute meant to be shared in it is annotated ClassVar

## Thesis
In a Python dataclass body, every attribute meant as a per-instance field carries a type annotation, as in `timeout: int = 30`, and an attribute intentionally shared across all instances is annotated `ClassVar[...]`.

## Rationale
The `@dataclass` decorator takes as fields only class variables that have a type annotation. An attribute assigned without one is silently excluded from dataclass processing and stays a regular class variable, shared between all instances: it is not included in the generated `__init__`, it is not part of `__repr__` or `__eq__`, and passing it to the constructor raises `TypeError`. The class appears to work normally while the attribute takes part in none of the generated methods. A `ClassVar[...]` annotation makes a deliberate class variable explicit, and the decorator excludes it from consideration as a field.

## Example
```python
bad:  @dataclass
      class Config:
          timeout = 30
good: @dataclass
      class Config:
          timeout: int = 30
          instances: ClassVar[int] = 0
```

## Limits
An unannotated attribute that is deliberately shared by all instances is still a finding until it carries `ClassVar`, because the annotation is what states the intent. The rule reads attributes assigned a value in a dataclass body; a method, a property or a nested class is not such an assignment.

## Validator
Grep the hunk for `@dataclass` or `@dataclasses.dataclass`. Open the decorated class in the file and list every assignment directly in its body that has no annotation; skip dunder names such as `__slots__` and `__match_args__`, and `def`, `class` and decorated definitions. For each remaining name, check whether it is passed to the constructor, read or set per instance, or expected in `repr` or equality anywhere in the file, which marks it as a field, or whether it is a shared value missing its `ClassVar` annotation. Validator question: **Does a dataclass body assign an attribute with a plain `name = value` statement that carries neither a type annotation nor `ClassVar`?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-63`, severity major, `file`, `symbol`, `code` = the unannotated assignment quoted verbatim from the diff, `fix` = the annotated field such as `timeout: int = 30`, or `<name>: ClassVar[<type>] = <value>` for a deliberate class variable, `rationale` = the generated `__init__`, `__repr__` and `__eq__` that leave the attribute out and the `TypeError` a constructor call passing it raises).

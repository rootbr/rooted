---
title: A Python Enum subclass is never decorated with dataclass
rule_id: PY-131
domain: design
step: [design, implement, review]
applies_to: [python, object-oriented]
triggers: ['^\s*@(?:dataclasses[.])?dataclass\b', '^\s*class\s+\w+\((?:[^)]*,\s*)?(?:enum[.])?(?:Enum|IntEnum|StrEnum|Flag|IntFlag)\s*[,)]']
scope: hunk
check_kind: mechanical
severity_default: major
---

# A Python Enum subclass is never decorated with dataclass

## Thesis
A Python class that derives from enum.Enum or from one of its subclasses is defined without the dataclasses.dataclass decorator, because adding the decorator to Enum and its subclasses is not supported.

## Rationale
Nothing rejects the combination: the decorated enum class raises no error, and the defect shows at runtime as very strange results, such as members that compare equal to each other. With RED = 1 and BLUE = 2 in the body, Color.RED is Color.BLUE is False while Color.RED == Color.BLUE is True. The decorator generates an __eq__ that compares two instances by comparing each field in order, and a field is a class variable that has a type annotation; members written as RED = 1 carry no annotation, so the generated comparison has no field that tells two members apart. Every test of the form status == Status.APPROVED then answers True for any member of the enum.

## Example
```python
bad:  @dataclass
      class Status(Enum):
          PENDING = 1
          APPROVED = 2
good: class Status(Enum):
          PENDING = 1
          APPROVED = 2
```

## Limits
A dataclass used as a mixin base of an enum is a documented combination and is outside the rule: a @dataclass class CreatureDataMixin with fields size and legs, and class Creature(CreatureDataMixin, Enum) with members such as DOG = 'medium', 4, gives each member structured data without decorating the enum itself. The rule concerns the standard-library dataclasses.dataclass decorator.

## Validator
Grep the hunk for a @dataclass or @dataclasses.dataclass decorator line, with or without arguments, and for a class statement whose bases name Enum, IntEnum, StrEnum, Flag, IntFlag or another enum class. Open the decorated class statement and trace each base through its definition or import until it reaches enum.Enum or ends without it. Skip a class that only inherits from a dataclass mixin and carries no dataclass decorator itself. Validator question: **Does a class that derives from enum.Enum, directly or through another enum class, carry the dataclasses.dataclass decorator?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-131`, severity major, `file`, `symbol`, `code` = the decorator line and the class statement it decorates, `fix` = the same enum without the decorator, with any per-member fields moved into a `@dataclass` mixin base as in `class Status(StatusData, Enum)`, `rationale` = that the generated `__eq__` makes distinct members compare equal while the class is created without error).

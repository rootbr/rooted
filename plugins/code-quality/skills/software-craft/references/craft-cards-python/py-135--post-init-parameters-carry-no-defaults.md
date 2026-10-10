---
title: A Python dataclass's __post_init__ gives its parameters no defaults, and an init-only parameter with a default is an InitVar field
rule_id: PY-135
domain: design
step: [implement, review]
applies_to: [python, object-oriented]
triggers: ['def\s+__post_init__\s*\([^)]*=', 'def\s+__post_init__\s*\(']
scope: hunk
check_kind: mechanical
severity_default: major
---

# A Python dataclass's __post_init__ gives its parameters no defaults, and an init-only parameter with a default is an InitVar field

## Thesis
A __post_init__ method of a Python dataclass declares its parameters without default values; an init-only parameter that needs a default is declared as an InitVar field with that default in the class body.

## Rationale
Init-only fields, the InitVar fields of the class body, are added as parameters to the generated __init__ and are passed on to __post_init__ in the order they were defined in the class; they are not otherwise used by dataclasses. A default written on a __post_init__ parameter has no impact on whether the parameter has a default in the generated __init__. With bar: InitVar[int] = 0 in the class body and def __post_init__(self, bar: int = 1, baz: int = 2), Foo() prints 0 and 2: the InitVar's default 0 reaches __post_init__ in place of the 1 written there, and baz, which has no InitVar field, always takes 2. Declaring bar and baz as InitVar fields with defaults 1 and 2 makes Foo() print 1 and 2.

## Example
```python
bad:  @dataclass
      class Foo:
          bar: InitVar[int] = 0
          def __post_init__(self, bar: int = 1, baz: int = 2): ...
good: @dataclass
      class Foo:
          bar: InitVar[int] = 1
          baz: InitVar[int] = 2
          def __post_init__(self, bar: int, baz: int): ...
```

## Limits
Moving the default onto an InitVar field is usually the right fix; it is the wrong one when the parameter is not meant to be part of the public API or when the value is meant to be shared across all instances, and there the fix is not an InitVar field. The rule concerns classes decorated with the standard-library dataclasses.dataclass.

## Validator
Grep the hunk for a def __post_init__ line and read its full parameter list, across lines when it wraps. Open the enclosing class and confirm that it carries the dataclasses.dataclass decorator. For each parameter after self that has a default, look up the InitVar field of the same name in the class body, to show in the fix whether that default is overridden or unreachable from the constructor. Validator question: **Does a __post_init__ method of a dataclass declare a default value for any of its parameters?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-135`, severity major, `file`, `symbol`, `code` = the `def __post_init__` line with its defaulted parameters, `fix` = the defaults moved onto `InitVar` fields of the class body, such as `baz: InitVar[int] = 2`, and the `__post_init__` parameters left without defaults, `rationale` = that the generated `__init__` ignores a default written on `__post_init__`: an `InitVar` default replaces it, and a parameter with no `InitVar` field cannot be passed to the constructor).

---
title: A Python class body does not assign a mutable object or a per-instance value such as a timestamp as an attribute default unless the attribute is annotated ClassVar
rule_id: PY-61
domain: design
step: [design, implement, review]
applies_to: [python, object-oriented]
triggers: ['^\s+\w+\s*(:\s*[^=]+)?=\s*(\[|\{|set\(|list\(|dict\(|defaultdict\()', '^\s+\w+\s*:\s*[^=]+=\s*(datetime[.](datetime[.])?now|datetime[.](datetime[.])?utcnow|uuid[.]uuid4|uuid4|time[.]time|date[.]today)\(', '^\s+\w+\s*:\s*[^=]+=\s*field\(\s*default\s*=\s*(\[|\{|set\(|list\(|dict\()']
scope: file
check_kind: mechanical
severity_default: major
---

# A Python class body does not assign a mutable object or a per-instance value such as a timestamp as an attribute default unless the attribute is annotated ClassVar

## Thesis
In a Python class body, an attribute whose default is a mutable object such as a list, dict or set, or a value meant to differ per instance such as `datetime.now()` or `uuid.uuid4()`, is created per instance instead: a plain class assigns it in `__init__`, a dataclass field takes `field(default_factory=...)`, and an attribute meant to be one object shared by all instances is annotated `ClassVar`.

## Rationale
Python stores default member values written in a class body in class attributes, shared by all instances of the class, and evaluates them once, when the class is defined, not each time an instance is created. A mutable default is therefore shared state: when the attribute is changed through one instance, the change shows in all other instances, as when two dogs adding tricks to one class-level list each see both tricks. Dataclasses use normal Python class creation and share this behavior, and a function call in a field default is performed once, at definition time, with the returned value reused by every instance, so attributes meant to be unique per instance, such as UUIDs or timestamps, become identical across all instances. There is no general way for dataclasses to detect this condition: the decorator raises `ValueError` only when it detects an unhashable default, a partial solution that lets a computed default such as `datetime.now()` through. `field(default_factory=...)` takes a callable with no arguments, invoked each time a new instance is created, so each instance receives a fresh value; a `ClassVar` annotation excludes the attribute from the dataclass fields.

## Example
```python
bad:  class Dog:
          tricks = []
      @dataclass
      class Event:
          created_at: datetime = datetime.now()
good: class Dog:
          def __init__(self) -> None: self.tricks: list[str] = []
      @dataclass
      class Event:
          created_at: datetime = field(default_factory=datetime.now)
```

## Limits
An attribute deliberately shared by all instances, such as a registry, is correct in the class body once it is annotated `ClassVar`, as in `registry: ClassVar[dict[str, type]] = {}`. An immutable default meant to be the same for every instance, such as a number, a string or a tuple, stays in the class body: switching a list default to an immutable data type such as a tuple is itself a fix. In a dataclass, a default the decorator detects as unhashable, such as `[]` or `{}`, already fails at class creation with `ValueError`, so the shared defaults that reach run time there are function-call results and other values that check lets through.

## Validator
Grep the hunk for a class-body assignment whose value is a list, dict or set display or a `list()`, `dict()`, `set()` or `defaultdict()` call; for an annotated attribute whose default calls `datetime.now`, `datetime.utcnow`, `uuid.uuid4`, `time.time` or `date.today`; and for `field(default=...)` with a mutable value. Open the enclosing class in the file: confirm the assignment sits directly in the class body, not inside a method, and read its annotation. Skip an attribute annotated `ClassVar[...]` and a default that is immutable and meant to be the same for every instance. For a plain class, check whether a method mutates the attribute through `self` or callers expect each instance to hold its own value. Validator question: **Does a class body give an attribute that is not annotated `ClassVar` a default that is a mutable object or a value meant to differ per instance?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-61`, severity major, `file`, `symbol`, `code` = the class-body assignment quoted verbatim from the diff, `fix` = the Python that creates the value per instance — `self.<name> = []` in `__init__` for a plain class, `<name>: <type> = field(default_factory=<callable>)` for a dataclass field — or the `ClassVar[...]` annotation where one shared object is meant, `rationale` = the one object every instance shares, or the per-instance value fixed at class-definition time).

## Source
- CPython Doc/tutorial/classes.rst §Class and Instance Variables (https://raw.githubusercontent.com/python/cpython/main/Doc/tutorial/classes.rst) — 'the *tricks* list in the following code should not be used as a class variable because just a single list would be shared by all *Dog* instances' ... 'Correct design of the class should use an instance variable instead' (fetched)
- CPython Doc/library/dataclasses.rst §Mutable default values (https://raw.githubusercontent.com/python/cpython/main/Doc/library/dataclasses.rst) — 'Python stores default member variable values in class attributes.' ... 'Because dataclasses just use normal Python class creation they also share this behavior.  There is no general way for Data Classes to detect this condition.' ... 'if it detects an unhashable default parameter.  The assumption is that if a value is unhashable, it is mutable.  This is a partial solution' (fetched)
- CPython Doc/library/dataclasses.rst §Class variables (https://raw.githubusercontent.com/python/cpython/main/Doc/library/dataclasses.rst) — 'it is excluded from consideration as a field and is ignored by the dataclass mechanisms' (fetched)
- Ruff RUF012 mutable-class-default (astral-sh/ruff crates/ruff_linter/src/rules/ruff/rules/mutable_class_default.rs) — 'This can lead to bugs when the attributes are changed in one instance, as those changes will unexpectedly affect all other instances.' ... 'to indicate that it is intended to be shared across all instances' ... 'Using an immutable data type (e.g. a tuple instead of a list)' (fetched)
- Ruff RUF008 mutable-dataclass-default (astral-sh/ruff crates/ruff_linter/src/rules/ruff/rules/mutable_dataclass_default.rs) — 'Instead of sharing mutable defaults, use the `field(default_factory=...)` pattern.' (fetched)
- Ruff RUF009 function-call-in-dataclass-default-argument (astral-sh/ruff crates/ruff_linter/src/rules/ruff/rules/function_call_in_dataclass_default.rs) — 'Function calls are only performed once, at definition time. The returned value is then reused by all instances of the dataclass.' (fetched)
- SonarSource python S8685 (SonarSource/sonar-python python-checks/src/main/resources/org/sonar/l10n/py/rules/python/S8685.html) — 'Default values for dataclass attributes are evaluated once when the class is defined, not each time an instance is created. This is a fundamental aspect of how Python evaluates default values.' ... 'attributes meant to be unique per instance, such as UUIDs or timestamps, become identical across all instances' ... 'invoked each time a new instance is created, so each instance receives a fresh value' ... 'expects a callable with no arguments' (fetched)

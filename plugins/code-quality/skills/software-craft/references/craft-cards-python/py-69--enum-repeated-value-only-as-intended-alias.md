---
title: A Python Enum member repeats the value of an earlier member only as an intended alias, and an enumeration whose members must stay distinct is decorated with enum.unique
rule_id: PY-69
domain: design
step: [implement, review]
applies_to: [python]
triggers: ['^class \w+\(.*\b(Enum|IntEnum|StrEnum|Flag|IntFlag)\)', '^\s+[A-Z][A-Z0-9_]*\s*=\s*\S']
scope: file
check_kind: mechanical
severity_default: minor
---

# A Python Enum member repeats the value of an earlier member only as an intended alias, and an enumeration whose members must stay distinct is decorated with enum.unique

## Thesis
A Python `Enum` member takes the value of an earlier member only when it is meant as an alias of that member; a member meant to be distinct gets a value no other member has, and an enumeration whose values must stay distinct can say so with `enum.unique`, which raises `ValueError` when it finds an alias.

## Rationale
By default, enumerations allow multiple names as aliases for the same value: given two entries `A` and `B` with the same value and `A` defined first, `B` is an alias for the member `A`, by-value lookup of that value returns `A`, and by-name lookup of `B` also returns `A`. Iterating over the members of an enum does not provide the aliases. A value repeated by mistake therefore raises no error: the new name is the earlier member, and no loop over the enumeration reaches it under its own name. `enum.unique` searches the enumeration's `__members__`, gathering any aliases it finds, and raises `ValueError` with the details if any are found.

## Example
```python
bad:  class Status(Enum):
          ACTIVE = 2
          CLOSED = 2  # Status.CLOSED is Status.ACTIVE
good: @enum.unique
      class Status(Enum):
          ACTIVE = 2
          CLOSED = 3
```

## Limits
Whether a repeated value is a finding is contested. One position reports every enumeration with duplicate values: enum values should be unique, and non-unique values are redundant and likely a mistake. The other position treats aliases as supported: an enum member can have other names associated with it, and `@unique` is for when that behavior isn't desired. Intent separates the cases: a repeated value that the class or a comment marks as an intended alias stays, and a repeated value with no such mark is a finding.

## Validator
Grep the hunk for a `class` line with an `Enum`, `IntEnum`, `StrEnum`, `Flag` or `IntFlag` base and for upper-case member assignments. Open the file at the enumeration's class body, collect each member's value as written, and compare the values in order; values from `auto()` or computed expressions are compared only when they can be read off the source. Read the decorators above the class (`@unique`, `@enum.unique`, `@verify(UNIQUE)`) and the comment or docstring at a repeated member. Validator question: **Does an enumeration give a member a value equal to an earlier member's value with no comment or docstring marking that name as an intended alias?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-69`, severity minor, `file`, `symbol`, `code` = the two member assignment lines that share the value, quoted verbatim from the diff, `fix` = a distinct value for the new member with `@enum.unique` above the class, or a comment marking the name as an intended alias, in Python, `rationale` = the earlier member the new name aliases and the iteration that omits it).

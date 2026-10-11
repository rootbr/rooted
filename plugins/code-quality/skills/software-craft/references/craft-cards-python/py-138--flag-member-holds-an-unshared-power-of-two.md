---
title: A Python Flag member meant as a flag of its own holds a power of two that no other member shares
rule_id: PY-138
domain: design
step: [implement, review]
applies_to: [python]
triggers: ['^\s*class\s+\w+\((?:[^)]*,\s*)?(?:enum[.])?(?:Int)?Flag\s*[,)]', '^\s+[A-Z][A-Z0-9_]*\s*=\s*(?:0[xXbBoO][0-9a-fA-F_]+|\d[\d_]*)\s*(?:#.*)?$']
scope: file
check_kind: mechanical
severity_default: major
---

# A Python Flag member meant as a flag of its own holds a power of two that no other member shares

## Thesis
In a subclass of `enum.Flag` or `enum.IntFlag`, each member meant as a flag of its own holds a single power-of-two value whose bit no other member's value shares, and a member meant to combine others is written as the `|` of the members it combines.

## Rationale
To be canonical, the value of a flag needs to be a power-of-two value and not a duplicate name; a flag with no value (`0`) or with more than one power-of-two value, such as `3`, is considered an alias. Since Python 3.11, `Flag` considers only primary values (power of two) canonical, while composite values such as `3`, `6` and `10` are considered aliases. Only canonical flags are returned during iteration, and multi-bit flags, which are aliases, can be returned from operations, so with `READ = 1`, `WRITE = 2` and `EXECUTE = 3`, iterating over the class leaves `EXECUTE` out and `READ | WRITE` gives `EXECUTE`.

## Example
```python
bad:  class FilePermissions(IntFlag):
          READ = 1
          WRITE = 2
          EXECUTE = 3  # an alias of READ | WRITE
good: class FilePermissions(IntFlag):
          READ = 1
          WRITE = 2
          EXECUTE = 4
          READ_WRITE = READ | WRITE
```

## Limits
A member meant as a named combination is an intended alias, written as the `|` of its members: with `YELLOW = RED | GREEN`, `Color(3)` returns the named combination `Color.YELLOW`. A zero-valued member, such as `NONE = 0`, is an alias by definition and does not show up when the class is iterated over; the rule does not reach it. A plain `Enum` subclass is outside the rule, since the expanded view of aliasing belongs to flags.

## Validator
For each `Flag` or `IntFlag` subclass the hunk adds or changes, write the value of each member assigned an integer literal in binary, and expand each member assigned the `|` of other members into the bits it combines. Check every literal member for exactly one set bit that no other literal member holds, and read how an overlapping member is used in the file — iterated over, tested with `in`, or combined as a flag of its own. Validator question: **Does a member assigned an integer literal in a `Flag` or `IntFlag` body hold more than one set bit, or a bit another literal member already holds, while nothing in its name or its uses marks it as a named combination?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-138`, severity major, `file`, `symbol`, `code` = the member assignment whose value overlaps, `fix` = the member given the next free power of two, such as `EXECUTE = 4`, or written as the `|` of the members it combines, `rationale` = the bits the value shares and with which members, and that the member is an alias left out of iteration and returned by combining them).

## Source
- CPython Doc/howto/enum.rst §Flag Classes (python/cpython Doc/howto/enum.rst) — 'to be canonical, the value of a flag needs to be a power-of-two value, and not a duplicate name.' ; 'a flag with no value (a.k.a. ``0``) or with more than one power-of-two value (e.g. ``3``) is considered an alias.' ; §Flag and IntFlag minutia — 'single-bit flags are canonical' ; 'multi-bit and zero-bit flags are aliases' ; 'only canonical flags are returned during iteration' ; 'multi-bit flags, aka aliases, can be returned from operations' ; §Flag Members — '(Note that ``BLACK``, ``PURPLE``, and ``WHITE`` do not show up.)' ; §Flag Classes — 'Flags have an expanded view of aliasing' (fetched)
- CPython Doc/howto/enum.rst §Combining members of Flag (python/cpython Doc/howto/enum.rst) — 'Color(3)  # named combination' ; '<Color.YELLOW: 3>' (fetched)
- CPython Doc/whatsnew/3.11.rst §enum (python/cpython Doc/whatsnew/3.11.rst) — 'to only consider primary values (power of two) canonical while composite values (``3``, ``6``, ``10``, etc.) are considered aliases' (fetched)
- Pylint implicit-flag-alias (W0213) (pylint-dev/pylint pylint/checkers/classes/class_checker.py) — 'Used when multiple integer values declared within an enum.IntFlag class share a common bit position.' (fetched)
- Pylint implicit-flag-alias (W0213) (pylint-dev/pylint doc/data/messages/i/implicit-flag-alias/bad.py) — 'EXECUTE = 3  # [implicit-flag-alias]' (fetched)
- Caveat: the message names `enum.IntFlag`; the canonical-value rule of the documentation covers `Flag` and `IntFlag` alike.

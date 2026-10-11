---
title: The result of an in-place mutating method of a Python list, dict or set is never assigned, returned or passed on, because such methods return None
rule_id: PY-53
domain: performance
step: [implement, review]
applies_to: [python]
triggers: ['[^=!<>]=\s*[\w.\[\]]+[.](sort|reverse|append|extend|insert|update|add|clear|discard)\(', '\breturn\s+[\w.\[\]]+[.](sort|reverse|append|extend|insert|update|add|clear|discard)\(', '\b(print|len|list|sorted|tuple)\(\s*[\w.\[\]]+[.](sort|reverse|append|extend|update)\(']
scope: hunk
check_kind: mechanical
severity_default: major
---

# The result of an in-place mutating method of a Python list, dict or set is never assigned, returned or passed on, because such methods return None

## Thesis
Python code calls an in-place method of a built-in list, dict or set — such as `list.sort`, `list.reverse`, `list.append`, `list.extend`, `list.insert`, `dict.update`, `set.add` or `set.discard` — as a statement of its own and then uses the mutated object, or calls a copying form such as `sorted()` where a new collection is wanted; it assigns, returns or passes on the result of no such call, because these methods return `None`, not the collection.

## Rationale
In Python's mutable collection classes, the methods that add, subtract or rearrange their members in place, and don't return a specific item, never return the collection instance itself but `None`. `list.sort()` modifies the list in place for economy of space when sorting a large sequence and, to remind users that it operates by side effect, does not return the sorted sequence; `sorted()` explicitly requests a new sorted list. This way a caller is not fooled into accidentally overwriting a list when a sorted copy is needed and the unsorted version must also be kept. Since such a method returns nothing, it makes no sense to use its output: passing it to another function or assigning its result to a variable is probably a bug. Whatever receives that output — a name, a callee, or the caller of a `return` — receives `None`, not the collection.

## Example
```python
bad:  ranked = scores.sort(reverse=True)
      print(names.reverse())
      return items.append(item)
good: ranked = sorted(scores, reverse=True)
      names.reverse()
      print(names)
      items.append(item)
      return items
```

## Limits
A method that returns a specific item, such as `list.pop()` or `dict.pop()`, is outside the rule; its result is the item. The rule covers the mutable collection classes of the built-in types; a method of the same name on another type, such as a builder or query object whose `update()` or `add()` returns a value, is outside it, since the defect is using the output of a call that returns nothing.

## Validator
Grep the hunk for an assignment, a `return` statement or a call argument whose value is a call to `sort`, `reverse`, `append`, `extend`, `insert`, `update`, `add`, `clear` or `discard`. Trace the receiver to its definition in the hunk or the enclosing function: a list, dict or set display or comprehension, `list()`, `dict()`, `set()`, `defaultdict`, `Counter`, `OrderedDict`, or a parameter annotated with one of these makes it a built-in collection. Validator question: **Is the `None` result of an in-place method of a built-in list, dict or set assigned, returned or passed to another call?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-53`, severity major, `file`, `symbol`, `code` = the statement that uses the method call's result, `fix` = the method called as its own statement with the collection used after it, or the copying form such as `sorted(scores)`, `rationale` = in-place methods of list, dict and set return `None`, so the name or callee receives `None` instead of the collection).

## Source
- CPython Doc/builtins/stdtypes.rst §Built-in Types (https://raw.githubusercontent.com/python/cpython/main/Doc/builtins/stdtypes.rst) — 'Some collection classes are mutable.  The methods that add, subtract, or rearrange their members in place, and don't return a specific item, never return the collection instance itself but ``None``.' (fetched)
- CPython Doc/builtins/stdtypes.rst §Lists, list.sort (https://raw.githubusercontent.com/python/cpython/main/Doc/builtins/stdtypes.rst) — 'This method modifies the sequence in place for economy of space when sorting a large sequence.  To remind users that it operates by side effect, it does not return the sorted sequence (use :func:`sorted` to explicitly request a new sorted list instance).' (fetched)
- CPython Doc/faq/design.rst §Why doesn't list.sort() return the sorted list? (https://raw.githubusercontent.com/python/cpython/main/Doc/faq/design.rst) — 'This way, you won't be fooled into accidentally overwriting a list when you need a sorted copy but also need to keep the unsorted version around.' (fetched)
- SonarSource python S3699 (SonarSource/sonar-python python-checks/src/main/resources/org/sonar/l10n/py/rules/python/S3699.html) — 'If a function does not return anything, it makes no sense to use its output. Specifically, passing it to another function, or assigning its "result" to a variable is probably a bug because such functions return nothing, which is probably not what was intended.' (fetched)
- SonarSource python S3699 (SonarSource/sonar-python python-checks/src/main/resources/org/sonar/l10n/py/rules/python/S3699.html) — 'This rule raises an issue when a function call result is used, even though the function does not return anything.' (fetched)

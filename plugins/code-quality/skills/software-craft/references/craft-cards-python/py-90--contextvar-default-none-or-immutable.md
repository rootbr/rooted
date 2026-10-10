---
title: A contextvars.ContextVar is declared with None or an immutable default, never a mutable literal or a call that builds a mutable object, since the default is evaluated once and get() returns that same object wherever the context has no value
rule_id: PY-90
domain: errors
step: [design, implement, review]
applies_to: [python]
triggers: ['ContextVar\(.*\bdefault\s*=\s*(?:\[|\{|(?:set|list|dict|defaultdict|deque|OrderedDict|Counter)\()', 'ContextVar\(.*\bdefault\s*=\s*[\w.]+\(']
scope: hunk
check_kind: mechanical
severity_default: major
---

# A contextvars.ContextVar is declared with None or an immutable default, never a mutable literal or a call that builds a mutable object, since the default is evaluated once and get() returns that same object wherever the context has no value

## Thesis
A Python `contextvars.ContextVar` takes `None` or an immutable value as its `default=`, never a mutable literal such as `[]`, `{}` or a set, nor a function call that builds a mutable object. A variable that needs a mutable value takes `None` as its default, and the code initializes a new mutable object with the `set()` method.

## Rationale
The `ContextVar` default is evaluated once, when the `ContextVar` is defined, and `ContextVar.get()` returns it whenever no value for the variable is found in the current context. The same mutable object is then shared across the `get()` calls that fall back to it, and a modification of that object persists across those calls, which can lead to unexpected behavior. Context managers that have state should use context variables instead of `threading.local` to prevent their state from bleeding to other code unexpectedly when used in concurrent code, and a mutable default hands one object to every context that has not set a value of its own. With `None` as the default, `set()` sets the new object as the value of the variable in the current context.

## Example
```python
bad:  request_tags: ContextVar[list[str]] = ContextVar("request_tags", default=[])
      seen_ids: ContextVar[set[int]] = ContextVar("seen_ids", default=set())
      def add_tag(tag):
          request_tags.get().append(tag)
good: request_tags: ContextVar[list[str] | None] = ContextVar("request_tags", default=None)
      seen_ids: ContextVar[frozenset[int]] = ContextVar("seen_ids", default=frozenset())
      def start_request():
          request_tags.set([])
      def add_tag(tag):
          request_tags.get().append(tag)
```

## Limits
A call to a type outside the standard library that the project marks as immutable through the linter option `lint.flake8-bugbear.extend-immutable-calls` is a documented tolerance: the linters ignore the calls listed there. The rule reaches the `default=` given when the `ContextVar` is defined; a mutable object stored with `set()` is the value of the variable in the context that set it and is outside the rule.

## Validator
Grep the hunk for `ContextVar(` calls with a `default=` keyword. Read the default expression: a list, dict or set literal or comprehension, or a call to `list`, `dict`, `set`, `collections.defaultdict`, `deque`, `OrderedDict`, `Counter` or a mutable class of the project, builds a mutable object; `None`, a number, a string, `bytes`, a tuple, a `frozenset` or a call listed in the project's `extend-immutable-calls` does not. For a call to a project function, open its definition and read what it returns. Validator question: **Does a `ContextVar` in the hunk take as its `default=` a mutable literal or a call that builds a mutable object?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-90`, severity major, `file`, `symbol`, `code` = the `ContextVar(...)` declaration with its `default=` verbatim, `fix` = the declaration with `default=None` and a `var.set([])` that gives each context a new object where the value is first needed, `rationale` = that the default is evaluated once and every `get()` that finds no value in the current context returns that same mutable object).

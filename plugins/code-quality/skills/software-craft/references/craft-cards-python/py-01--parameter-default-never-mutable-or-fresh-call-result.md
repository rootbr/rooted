---
title: A Python parameter default is never a mutable object or a function call whose result later calls need fresh, because Python evaluates the default once when def runs
rule_id: PY-01
domain: code
step: [implement, review]
applies_to: [python]
triggers: ['def\s+\w+\(.*=\s*(\[|\{|set\(|list\(|dict\(|defaultdict\(|deque\()', 'def\s+\w+\(.*=\s*[\w.]+\(', 'lambda[^:]*=\s*(\[|\{|[\w.]+\()']
scope: hunk
check_kind: mechanical
severity_default: major
---

# A Python parameter default is never a mutable object or a function call whose result later calls need fresh, because Python evaluates the default once when def runs

## Thesis
A Python parameter default is None or an immutable value, never a list, dict, set or other mutable object and never a function call whose returned object is mutable or should differ between calls, and a function that needs a fresh object creates it in the body on each call that omits the argument.

## Rationale
Python evaluates a default value only once, when the def statement defines the function, and that one object is then shared across all calls that omit the argument. When the object is mutable, such as a list, a dictionary or an instance of most classes, a change made in one call persists across calls: a list default that the body appends to accumulates the arguments passed on subsequent calls. A function call used as a default is performed only once, at definition time, and all calls reuse its returned value. A None default, or an immutable data structure, with a new mutable object initialized inside the body gives each call its own object.

## Example
```python
bad:  def log_event(event, sink=[], at=time.time()):
          sink.append((at, event))
          return sink
good: def log_event(event, sink=None, at=None):
          sink = [] if sink is None else sink
          at = time.time() if at is None else at
          sink.append((at, event))
          return sink
```

## Limits
A parameter with an immutable type annotation is outside the check, and so is a default that is a NewType call whose original type is immutable. Where one shared result of a call is intended, the call is assigned to a module-level variable and that variable is the default. A mutable default used on purpose to cache computation results cannot be replaced by None or an immutable data structure; the preferred form for such a cache is the functools.lru_cache decorator. The sources differ on a mutable default the function never modifies: one position forbids a mutable argument default outright, the other raises its issue only when the default value of a parameter is mutated.

## Validator
Grep the hunk for def and lambda parameter lists whose default is a list, dict or set display, a call that builds a container such as list(), dict(), set(), defaultdict() or deque(), or any other call. For a call default, open the called function or class where the hunk or its imports show it and decide whether the returned object is mutable or should differ between calls, as a timestamp or a fresh identifier does. Read the parameter's annotation for an immutable type. Validator question: **Does a def or lambda in the hunk give a parameter a default that is a mutable object or a call whose result is mutable or should differ between calls, with no immutable type annotation on that parameter?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-01`, severity major, `file`, `symbol`, `code` = the def or lambda line that carries the default, `fix` = the parameter defaulting to `None` with `if sink is None: sink = []` at the top of the body, a module-level name for a call result meant to be shared, or `@functools.lru_cache` for a default used as a cache, `rationale` = the default is evaluated once when def runs, so its one object is shared by every call that omits the argument).

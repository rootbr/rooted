---
title: A regular Python method is not decorated with functools.cache or lru_cache with maxsize None unless its instances are meant to live as long as the process
rule_id: PY-64
domain: design
step: [implement, review]
applies_to: [python, object-oriented, garbage-collected]
triggers: ['@(functools[.])?cache\s*$', '@(functools[.])?lru_cache\(\s*maxsize\s*=\s*None']
scope: file
check_kind: mechanical
severity_default: major
---

# A regular Python method is not decorated with functools.cache or lru_cache with maxsize None unless its instances are meant to live as long as the process

## Thesis
A regular Python method carries an unbounded functools cache, `functools.cache` or `functools.lru_cache(maxsize=None)`, only when its instances never need to be garbage collected, such as singletons or enum members; otherwise the cached computation moves to a module-level function of the values it needs, to `functools.cached_property` for a method without arguments, or to an `lru_cache` with a `maxsize`.

## Rationale
`functools.lru_cache` and `functools.cache` keep references to the arguments and return values until they age out of the cache or until the cache is cleared, and when a method is cached the `self` instance argument is included in the cache. The cache lives at the class level, in one process-wide table keyed by the arguments, so it keeps a strong reference to every instance used as a receiver, and those instances and anything they reference cannot be garbage collected while the entry lives. `functools.cache` returns the same as `lru_cache(maxsize=None)`: the LRU feature is disabled and the cache can grow without bound, so every receiver is linked to the function and never garbage collected, and memory use grows with the number of distinct instances. `functools.cached_property` stores the result at the instance level and creates no reference to the instance, so the result is kept only as long as the instance is alive; an `lru_cache` with a `maxsize` is bounded, and its receivers stay alive until they age out of the cache.

## Example
```python
bad:  class Number:
          @functools.lru_cache(maxsize=None)
          def squared(self) -> int: return self.value * self.value
good: @functools.cache
      def square(value: int) -> int: return value * value
      class Number:
          def squared(self) -> int: return square(self.value)
          @functools.cached_property
          def cubed(self) -> int: return self.value ** 3
```

## Limits
Methods of `enum.Enum` subclasses are exempt: enum members are singletons, so retaining them is intentional and bounded. A `@staticmethod` or `@classmethod` retains no per-instance `self`. `functools.cached_property` only works with methods that take no arguments, cannot detect changes to mutable instance attributes, lets results accumulate as instances accumulate, and requires a mutable `__dict__` on each instance. The positions differ on a bounded cache. One position reports `lru_cache` or `cache` on a method whatever its `maxsize`, because the cache retains a reference to the instance. The other position reports only `lru_cache(maxsize=None)` and `cache`, lists adding a `maxsize` as a fix, and names `lru_cache` with a `maxsize` as one of the two principal tools for caching methods, with instances kept alive until they age out. The condition that separates them is whether the cache is bounded: an unbounded cache keeps every receiver for the life of the process and is a finding; a cache with a `maxsize`, including a bare `@lru_cache` whose default `maxsize` is 128, keeps receivers until they age out and is a finding only where the project adopts the wider position.

## Validator
Grep the hunk for `@functools.cache`, `@cache`, `@functools.lru_cache(maxsize=None)` or `@lru_cache(maxsize=None)`. Open the enclosing class in the file: confirm the decorated function is a regular method taking `self`, not a `@staticmethod` or `@classmethod`, and that the class is not an `enum.Enum` subclass. Check how its instances are made: a module-level singleton or a fixed set created once lives as long as the process; instances created per request, per record or in a loop are meant to be collected. Validator question: **Does a regular method of a class whose instances are created and dropped while the process runs carry `functools.cache` or `lru_cache(maxsize=None)`?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-64`, severity major, `file`, `symbol`, `code` = the decorator line and the `def` line quoted verbatim from the diff, `fix` = a module-level `@functools.cache` function of the values the method needs that the method calls, `@functools.cached_property` for a method without arguments, or `@functools.lru_cache(maxsize=<n>)` where the project accepts a bounded method cache, `rationale` = the unbounded cache that keeps every receiver alive and the place where instances are created and dropped).

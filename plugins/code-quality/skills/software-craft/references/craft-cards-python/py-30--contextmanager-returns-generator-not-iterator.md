---
title: A generator decorated with contextlib.contextmanager or asynccontextmanager is annotated to return Generator or AsyncGenerator, never Iterator or AsyncIterator
rule_id: PY-30
domain: code
step: [implement, review]
applies_to: [python, static-types]
triggers: ['^\s*@(contextlib[.])?(async)?contextmanager\b', '->\s*(typing[.]|collections[.]abc[.])?(Async)?Iterator\[']
scope: hunk
check_kind: mechanical
severity_default: minor
---

# A generator decorated with contextlib.contextmanager or asynccontextmanager is annotated to return Generator or AsyncGenerator, never Iterator or AsyncIterator

## Thesis
A generator function decorated with `@contextlib.contextmanager` is annotated to return `Generator[T, None, None]`, and one decorated with `@contextlib.asynccontextmanager` to return `AsyncGenerator[T, None]`, rather than `Iterator[T]` or `AsyncIterator[T]`; on Python 3.13 and later the default type arguments may be omitted, as in `Generator[T]` and `AsyncGenerator[T]`.

## Rationale
`contextlib.contextmanager` requires the decorated function to return a generator-iterator when called, and an unhandled exception in the `with` block is re-raised inside the generator at the point where the `yield` occurred; `contextlib.asynccontextmanager` must be applied to an asynchronous generator function. Generators support methods such as `throw` that the iterator protocols do not guarantee, and the iterator overloads of these decorators are deprecated in typeshed. A generator is annotated with `Generator[YieldType, SendType, ReturnType]`, whose `SendType` and `ReturnType` parameters default to `None`, and an asynchronous generator with `AsyncGenerator[YieldType, SendType]`, whose `SendType` defaults to `None`.

## Example
```python
bad:  @contextmanager
      def opened(path: str) -> Iterator[TextIO]:
          with open(path) as handle:
              yield handle
good: @contextmanager
      def opened(path: str) -> Generator[TextIO, None, None]:
          with open(path) as handle:
              yield handle
```

## Limits
A simple generator that only yields values and is not passed to these decorators may be annotated `Iterator[YieldType]` or `Iterable[YieldType]`. A generator that returns a value states that type as its `ReturnType`; the automatic rewrite uses `object` there to accommodate any return value. The rule reaches functions whose innermost decorator is a contextlib context manager and whose bodies contain a `yield` or `yield from`.

## Validator
Grep the hunk for `@contextmanager`, `@asynccontextmanager` or their `contextlib.` forms. Open the decorated function, confirm that this decorator is its innermost one and that its body contains `yield` or `yield from`, and read its return annotation. Validator question: **Is a function whose innermost decorator is `contextlib.contextmanager` or `contextlib.asynccontextmanager` annotated to return `Iterator[...]` or `AsyncIterator[...]`?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-30`, severity minor, `file`, `symbol`, `code` = the decorator and the `def` line with its return annotation quoted verbatim, `fix` = the annotation as `Generator[T, None, None]` or `AsyncGenerator[T, None]`, or `Generator[T]` and `AsyncGenerator[T]` on Python 3.13 and later, `rationale` = these decorators require generators, which support `throw`, and typeshed deprecates their iterator overloads).

## Source
- Ruff UP052 context-manager-iterator (astral-sh/ruff crates/ruff_linter/src/rules/pyupgrade/rules/context_manager_iterator.rs) — '`contextlib.contextmanager` and `contextlib.asynccontextmanager` require generators, which support methods such as `throw` that are not guaranteed by the iterator protocols.' (fetched)
- Ruff UP052 context-manager-iterator (astral-sh/ruff crates/ruff_linter/src/rules/pyupgrade/rules/context_manager_iterator.rs) — 'The iterator overloads of these decorators are deprecated in' (fetched)
- Ruff UP052 context-manager-iterator (astral-sh/ruff crates/ruff_linter/src/rules/pyupgrade/rules/context_manager_iterator.rs) — 'On Python 3.13 and later, the fix omits the default type arguments and uses `Generator[int]` or `AsyncGenerator[int]`.' (fetched)
- Ruff UP052 context-manager-iterator (astral-sh/ruff crates/ruff_linter/src/rules/pyupgrade/rules/context_manager_iterator.rs) — 'For a generator that returns a value, the fix uses `object` as the return type to accommodate any return value.' (fetched)
- Ruff UP052 context-manager-iterator (astral-sh/ruff crates/ruff_linter/src/rules/pyupgrade/rules/context_manager_iterator.rs) — 'The rule checks functions whose innermost decorator is a contextlib context manager and whose bodies contain a `yield` or `yield from`.' (fetched)
- CPython Doc/library/contextlib.rst §contextlib.contextmanager (https://raw.githubusercontent.com/python/cpython/main/Doc/library/contextlib.rst) — 'The function being decorated must return a :term:`generator`-iterator when called.' (fetched)
- CPython Doc/library/contextlib.rst §contextlib.contextmanager (https://raw.githubusercontent.com/python/cpython/main/Doc/library/contextlib.rst) — 'If an unhandled exception occurs in the block, it is reraised inside the generator at the point where the yield occurred.' (fetched)
- CPython Doc/library/contextlib.rst §contextlib.asynccontextmanager (https://raw.githubusercontent.com/python/cpython/main/Doc/library/contextlib.rst) — 'It must be applied to an :term:`asynchronous generator` function.' (fetched)
- CPython Doc/library/typing.rst §Annotating generators and coroutines (https://raw.githubusercontent.com/python/cpython/main/Doc/library/typing.rst) — 'A generator can be annotated using the generic type :class:`Generator[YieldType, SendType, ReturnType] <collections.abc.Generator>`.' (fetched)
- CPython Doc/library/typing.rst §Annotating generators and coroutines (https://raw.githubusercontent.com/python/cpython/main/Doc/library/typing.rst) — 'The ``SendType`` and ``ReturnType`` parameters default to :const:`!None`' (fetched)
- CPython Doc/library/typing.rst §Annotating generators and coroutines (https://raw.githubusercontent.com/python/cpython/main/Doc/library/typing.rst) — ':class:`AsyncGenerator[YieldType, SendType] <collections.abc.AsyncGenerator>`' (fetched)
- CPython Doc/library/typing.rst §Annotating generators and coroutines (https://raw.githubusercontent.com/python/cpython/main/Doc/library/typing.rst) — 'Simple generators that only ever yield values can also be annotated as having a return type of either' (fetched)
- Caveat: Ruff UP052 is a preview rule.

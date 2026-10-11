---
title: An async generator yields inside a with or async with block only when it is an @asynccontextmanager that yields once or its consumers close it through contextlib.aclosing, since otherwise the block's cleanup may be delayed until the generator is closed
rule_id: PY-91
domain: errors
step: [implement, review]
applies_to: [python]
triggers: ['^\s*(?:\w+\s*=\s*)?yield\b', '^\s*async\s+with\b']
scope: file
check_kind: semantic
severity_default: major
---

# An async generator yields inside a with or async with block only when it is an @asynccontextmanager that yields once or its consumers close it through contextlib.aclosing, since otherwise the block's cleanup may be delayed until the generator is closed

## Thesis
In a Python `async def` that yields, a `yield` inside a `with` or `async with` block appears only in a function decorated with `@contextlib.asynccontextmanager` that yields once and acts as a context manager, or in an async generator that yields many values and whose consumers close it through `async with contextlib.aclosing(...)`; otherwise the generator holds no context manager open across a yield.

## Rationale
Yielding inside a context manager in an async generator is unsafe because the cleanup of the context manager may be delayed until the generator is closed, at which point `await` is no longer allowed, which can lead to resource leaks or other bugs. An async generator can perform cleanup only under the supervision of the appropriate coroutine runner; `__del__` has no access to the coroutine runner, and the runner might be garbage collected before the generator object. When an async generator is about to be garbage collected, it calls the finalizer it stored at its first iteration, and that finalizer is assumed to schedule an `aclose()` call with the loop that was active when the iteration started. `contextlib.aclosing` returns an async context manager that calls `aclose()` upon completion of the block: it supports deterministic cleanup of async generators that exit early by `break` or an exception, and runs the generator's async exit code in the same context as its iterations, so that exceptions and context variables work as expected and the exit code is not run after the lifetime of some task it depends on.

## Example
```python
bad:  async def open_connection(dsn):
          async with connect(dsn) as conn:
              yield conn
good: @contextlib.asynccontextmanager
      async def open_connection(dsn):
          async with connect(dsn) as conn:
              yield conn
      async def consume(conn):
          async with contextlib.aclosing(stream_rows(conn)) as rows:
              async for row in rows: handle(row)
```

## Limits
Functions decorated with `@pytest.fixture`, `@pytest_asyncio.fixture` or `@trio.as_safe_channel` handle async generator cleanup safely, and a yield inside a context manager in them is correct. For async generators that yield multiple values, `@asynccontextmanager` is not appropriate; for them the fix is `contextlib.aclosing` at the consumers or a body that holds no context manager open across a yield. Using `contextlib.aclosing` around all call sites of an async generator is a valid way to guarantee timely cleanup, but a check cannot verify that all callers use it, so it may flag a generator that is always consumed safely.

## Validator
Open each `async def` in the file whose own body contains `yield`, leaving nested functions aside, and find each `yield` that sits inside a `with` or `async with` block of that function. Read its decorators: `@asynccontextmanager` imported from `contextlib`, `@pytest.fixture`, `@pytest_asyncio.fixture` and `@trio.as_safe_channel` settle it. For a function without them, search the file for its call sites: a consumer that iterates it inside `async with contextlib.aclosing(...)` closes it deterministically. Validator question: **Does an `async def` in the file yield inside a `with` or `async with` block without one of the decorators `@asynccontextmanager`, `@pytest.fixture`, `@pytest_asyncio.fixture` or `@trio.as_safe_channel`, while no call site in the file shows every consumer entering it through `contextlib.aclosing`?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-91`, severity major, `file`, `symbol`, `code` = the `with` or `async with` header and the `yield` inside it, `fix` = the function under `@contextlib.asynccontextmanager` when it yields once, or `async with contextlib.aclosing(gen(...)) as rows:` with `async for row in rows:` at the consumer when it yields many values, `rationale` = that the context manager's cleanup may be delayed until the generator is closed, when `await` is no longer allowed).

## Source
- Ruff ASYNC119 yield-in-context-manager-in-async-generator (astral-sh/ruff crates/ruff_linter/src/rules/flake8_async/rules/yield_in_context_manager_in_async_generator.rs) — 'Yielding inside a context manager in an async generator is unsafe because the cleanup of the context manager may be delayed until the generator is closed, at which point `await` is no longer allowed. This can lead to resource leaks or other bugs.' (fetched)
- Ruff ASYNC119 yield-in-context-manager-in-async-generator (astral-sh/ruff crates/ruff_linter/src/rules/flake8_async/rules/yield_in_context_manager_in_async_generator.rs) — 'If the function is intended to yield only once and act as a context manager, use `@asynccontextmanager`.' (fetched)
- Ruff ASYNC119 yield-in-context-manager-in-async-generator (astral-sh/ruff crates/ruff_linter/src/rules/flake8_async/rules/yield_in_context_manager_in_async_generator.rs) — 'that yields multiple values, consumers should use `contextlib.aclosing` to ensure timely cleanup, or the generator should be refactored to avoid holding context managers open across yields.' (fetched)
- Ruff ASYNC119 yield-in-context-manager-in-async-generator (astral-sh/ruff crates/ruff_linter/src/rules/flake8_async/rules/yield_in_context_manager_in_async_generator.rs) — 'The rule also suppresses diagnostics for functions decorated with `@pytest.fixture`, `@pytest_asyncio.fixture`, or `@trio.as_safe_channel`, as these handle async generator cleanup safely.' (fetched)
- Ruff ASYNC119 yield-in-context-manager-in-async-generator (astral-sh/ruff crates/ruff_linter/src/rules/flake8_async/rules/yield_in_context_manager_in_async_generator.rs) — 'For async generators that yield multiple values, `@asynccontextmanager` is not appropriate.' (fetched)
- Ruff ASYNC119 yield-in-context-manager-in-async-generator (astral-sh/ruff crates/ruff_linter/src/rules/flake8_async/rules/yield_in_context_manager_in_async_generator.rs) — 'Using `contextlib.aclosing` around all call sites of an async generator is a valid way to guarantee timely cleanup, but this rule cannot verify that all callers use `aclosing`. As a result, it may flag generators that are always consumed safely.' (fetched)
- CPython Doc/library/contextlib.rst §Utilities, aclosing (https://raw.githubusercontent.com/python/cpython/main/Doc/library/contextlib.rst) — 'Return an async context manager that calls the ``aclose()`` method of *thing* upon completion of the block.' (fetched)
- CPython Doc/library/contextlib.rst §Utilities, aclosing (https://raw.githubusercontent.com/python/cpython/main/Doc/library/contextlib.rst) — 'Significantly, ``aclosing()`` supports deterministic cleanup of async generators when they happen to exit early by :keyword:`break` or an exception.' (fetched)
- CPython Doc/library/contextlib.rst §Utilities, aclosing (https://raw.githubusercontent.com/python/cpython/main/Doc/library/contextlib.rst) — 'This pattern ensures that the generator's async exit code is executed in the same context as its iterations (so that exceptions and context variables work as expected, and the exit code isn't run after the lifetime of some task it depends on).' (fetched)
- PEP 533 §Background and motivation (https://raw.githubusercontent.com/python/peps/main/peps/pep-0533.rst) — 'can only perform cleanup under the supervision of the appropriate coroutine runner. ``__del__`` doesn't have access to the coroutine runner; indeed, the coroutine runner might be garbage collected before the generator object.' (fetched)
- PEP 525 §Finalization (https://raw.githubusercontent.com/python/peps/main/peps/pep-0525.rst) — 'When an asynchronous generator is iterated for the first time, it stores a reference to the current *finalizer*.' (fetched)
- PEP 525 §Finalization (https://raw.githubusercontent.com/python/peps/main/peps/pep-0525.rst) — 'When an asynchronous generator is about to be garbage collected, it calls its cached *finalizer*.  The assumption is that the finalizer will schedule an ``aclose()`` call with the loop that was active when the iteration started.' (fetched)
- Caveat: PEP 533 has Status Deferred; it is cited for its account of async generator cleanup, not for the mechanism it proposes.

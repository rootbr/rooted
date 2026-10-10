---
title: A call to a coroutine function in Python is awaited, returned to an awaiting caller, or handed to asyncio.run, asyncio.create_task, a TaskGroup or asyncio.gather, since simply calling a coroutine does not schedule it to be executed
rule_id: PY-87
domain: errors
step: [implement, review]
applies_to: [python]
triggers: ['^\s*(?:asyncio|trio|anyio)[.](?:sleep|wait_for|wait)\(', '^\s*(?:trio|anyio)[.](?:open_\w+|run_process|lowlevel[.]checkpoint)\(', '^\s*[\w.]+[.](?:aclose|asend|athrow)\(']
scope: file
check_kind: semantic
severity_default: major
---

# A call to a coroutine function in Python is awaited, returned to an awaiting caller, or handed to asyncio.run, asyncio.create_task, a TaskGroup or asyncio.gather, since simply calling a coroutine does not schedule it to be executed

## Thesis
In Python, every call to an `async def` function — a library coroutine function such as `asyncio.sleep` or `trio.sleep`, or one of the project's own — is awaited, where it is made or by the caller it is returned to, or handed to `asyncio.run`, `asyncio.create_task`, `asyncio.TaskGroup.create_task`, `asyncio.gather` or another function that takes an awaitable, such as `asyncio.wait_for`, `asyncio.shield`, `asyncio.ensure_future` or `loop.create_task`, rather than left as a bare statement or bound to a name that is never awaited.

## Rationale
Calling an `async def` function returns a coroutine object, and simply calling a coroutine will not schedule it to be executed: in the asyncio documentation, `main()` evaluates to a `<coroutine object main ...>`. To actually run a coroutine, asyncio provides the mechanisms of `asyncio.run` for the top-level entry point, awaiting the coroutine, `asyncio.create_task`, and `asyncio.TaskGroup` as the more modern alternative to `create_task`; `asyncio.gather` automatically schedules any coroutine it is given as a Task. When a coroutine function is called but not awaited, or the coroutine is not scheduled with `asyncio.create_task`, asyncio emits a `RuntimeWarning`, and the coroutine itself is not scheduled to be executed. Many of the functions trio exposes are asynchronous and must be awaited to take effect; calling one without an `await` can lead to `RuntimeWarning` diagnostics and unexpected behaviour.

## Example
```python
bad:  async def reconnect(client, backoff):
          while not await client.connect():
              asyncio.sleep(backoff)
good: async def reconnect(client, backoff):
          while not await client.connect():
              await asyncio.sleep(backoff)
```

## Limits
A coroutine object that is made now and awaited or scheduled later meets the rule, such as a list of coroutines passed to `asyncio.gather`, or a coroutine returned to a caller that awaits it. `asyncio.run` is the mechanism for running the top-level entry point `main()`, so that coroutine is handed to `asyncio.run` rather than awaited. Telling a coroutine function from a plain function takes the callee's definition: the triggers name library coroutine functions, and a project coroutine function is reached only when the finder resolves the callee.

## Validator
Grep the file for the triggers' library coroutine calls at the start of a statement, then read each `async def` body for calls of the project's own `async def` functions, resolving each callee to its definition. The `aclose()`, `asend()` and `athrow()` methods of an async generator return awaitables and are treated the same way. For each coroutine call, follow the coroutine object: it is used when an `await` applies to it, when it is passed to `asyncio.run`, `asyncio.create_task`, a TaskGroup's `create_task`, `asyncio.gather` or another function that takes an awaitable (`asyncio.wait_for`, `asyncio.shield`, `asyncio.ensure_future`, `loop.create_task`), or when it is returned; it is dropped when it stands as a bare statement or is bound to a name that no later statement awaits or schedules. Validator question: **Is a call to a coroutine function in the file dropped, that is, neither awaited, nor handed to asyncio.run, create_task, a TaskGroup, gather or another awaitable-taking function, nor returned to a caller?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-87`, severity major, `file`, `symbol`, `code` = the coroutine call that is never awaited, quoted verbatim from the diff, `fix` = the call prefixed with `await`, or the coroutine passed to `asyncio.create_task` or `tg.create_task`, `rationale` = simply calling a coroutine does not schedule it to be executed, so the call's body never runs and asyncio only emits a RuntimeWarning).

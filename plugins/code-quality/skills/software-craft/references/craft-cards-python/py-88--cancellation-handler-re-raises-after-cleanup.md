---
title: A handler that catches asyncio.CancelledError, trio.Cancelled or anyio's cancellation exception re-raises it once its cleanup is done, and code that truly means to suppress an asyncio cancellation also calls uncancel()
rule_id: PY-88
domain: errors
step: [handle-errors, review]
applies_to: [python, exceptions]
triggers: ['except\b.*\bCancelledError\b', 'except\b.*\btrio[.]Cancelled\b', 'except\b.*get_cancelled_exc_class\(\)']
scope: file
check_kind: mechanical
severity_default: major
---

# A handler that catches asyncio.CancelledError, trio.Cancelled or anyio's cancellation exception re-raises it once its cleanup is done, and code that truly means to suppress an asyncio cancellation also calls uncancel()

## Thesis
In Python, a handler that catches `asyncio.CancelledError`, `trio.Cancelled` or the class `anyio.get_cancelled_exc_class()` returns does its brief clean-up and then re-raises the exception, rather than passing, only logging, returning normally or raising a different exception in its place; asyncio code for which suppressing `asyncio.CancelledError` is truly desired also calls `uncancel()` to completely remove the cancellation state.

## Rationale
asyncio, Trio and AnyIO signal cancellation with special exceptions that the framework typically injects into the cancelled task; they are directives for the task to terminate its execution prematurely and perform necessary clean-up, and the task is expected to catch the exception, perform urgent and brief clean-up, and re-raise it. A handler that catches the exception and does not re-raise it swallows the cancellation signal: the framework and any calling code cannot know that the task has acknowledged the cancellation and is stopping, and the task might even continue running parts of its code after the except block. Tasks ignoring cancellation may run indefinitely and leave the application unresponsive to shutdown signals, may leave files, connections or locks unreleased, and break timeouts and task groups. In asyncio, an explicitly caught `CancelledError` should generally be propagated when clean-up is complete; the components that enable structured concurrency, such as `asyncio.TaskGroup` and `asyncio.timeout`, are implemented using cancellation internally and might misbehave if a coroutine swallows `asyncio.CancelledError`.

## Example
```python
bad:  async def run_worker(conn):
          try: await serve(conn)
          except asyncio.CancelledError:
              logger.info("worker stopped")
good: async def run_worker(conn):
          try: await serve(conn)
          except asyncio.CancelledError:
              await conn.close()
              raise
```

## Limits
`try`/`finally` blocks are the recommended form of robust clean-up in asyncio, and since `asyncio.CancelledError` directly subclasses `BaseException`, most code will not need to be aware of it. User code should not generally call `uncancel()`; only in cases when suppressing `asyncio.CancelledError` is truly desired is it necessary to also call `uncancel()` to completely remove the cancellation state. A specific handler for the cancellation exception, placed before a general exception handler, meets the rule when it re-raises. Asynchronous clean-up in an `except CancelledError` or `finally` block can itself be interrupted by cancellation; `asyncio.shield()` or a library equivalent can protect critical clean-up code, used sparingly as it may delay shutdown.

## Validator
Grep the file for `except` clauses that name `asyncio.CancelledError`, `trio.Cancelled` or `anyio.get_cancelled_exc_class()`, alone or in a tuple. Open each handler body and trace every path out of it: a bare `raise`, or a `raise` of the caught exception object, re-raises; `pass`, a log call that falls through, `return`, `break` or `continue` out of an enclosing loop, or a `raise` of another exception swallows it. For an asyncio handler that does not re-raise, look for an `uncancel()` call on the current task within the handler. Validator question: **Does a handler in the file that catches asyncio.CancelledError, trio.Cancelled or AnyIO's cancellation exception leave on some path without re-raising it, and, for asyncio, without calling uncancel()?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-88`, severity major, `file`, `symbol`, `code` = the `except` line and the handler statement that ends it without re-raising, quoted verbatim from the diff, `fix` = the handler's clean-up followed by a bare `raise`, or a `try`/`finally` that runs the clean-up and lets the cancellation propagate, `rationale` = a swallowed cancellation keeps the cancelled task running and breaks timeouts and task groups built on cancellation).

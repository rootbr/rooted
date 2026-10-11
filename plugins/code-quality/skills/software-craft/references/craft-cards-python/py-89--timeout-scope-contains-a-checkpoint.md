---
title: A block under asyncio.timeout, a trio or anyio fail_after or move_on_after, or a cancel scope contains at least one await, async for, async with or yield, since without such a checkpoint the timeout never takes effect
rule_id: PY-89
domain: errors
step: [implement, handle-errors, review]
applies_to: [python]
triggers: ['async\s+with\s+asyncio[.]timeout(?:_at)?\(', 'with\s+(?:trio|anyio)[.](?:fail_after|fail_at|move_on_after|move_on_at)\(', 'with\s+(?:trio|anyio)[.]CancelScope\(']
scope: file
check_kind: mechanical
severity_default: major
---

# A block under asyncio.timeout, a trio or anyio fail_after or move_on_after, or a cancel scope contains at least one await, async for, async with or yield, since without such a checkpoint the timeout never takes effect

## Thesis
In Python, the body of `async with asyncio.timeout(...)` or `asyncio.timeout_at(...)`, of `with trio.fail_after(...)`, `trio.move_on_after(...)`, `trio.fail_at(...)` or `trio.move_on_at(...)`, of AnyIO's `fail_after` or `move_on_after`, or of a Trio or AnyIO `CancelScope` contains at least one checkpoint: an `await`, an `async for`, an `async with`, or a `yield`.

## Rationale
When an asyncio task is cancelled, `asyncio.CancelledError` will be raised in the task at the next opportunity, and `asyncio.timeout` works through that cancellation: when the block overruns, the context manager will cancel the current task and transform the resulting `CancelledError` into a `TimeoutError`; `asyncio.timeout_at` is the same with an absolute time to stop waiting. Trio and AnyIO cancellation scopes likewise only work when there are checkpoints within the scope where cancellation can occur, a checkpoint being a point in the code where cancellation can be detected and acted upon. Such context managers have no effect unless they contain a checkpoint: without any, the timeout will never be triggered, resources might be held longer than intended, and the application might become unresponsive or hang, so a scope without an `await`, `async with` or `async for` statement is likely a mistake. A `yield` statement is among the common checkpoints, and the lint check counts it because checkpoints may occur in the caller to which the block yields.

## Example
```python
bad:  async def load_report(blob):
          async with asyncio.timeout(5):
              return parse_report(blob)
good: async def load_report(url):
          async with asyncio.timeout(5):
              blob = await fetch_report(url)
          return parse_report(blob)
```

## Limits
A checkpoint added inside the scope after its synchronous work meets the rule, as in the reference fixes; asyncio has no direct checkpoint method, and `await asyncio.sleep(0)` serves as the workaround, while Trio and AnyIO offer `trio.lowlevel.checkpoint()` and `anyio.lowlevel.checkpoint()`. The rule asks for at least one checkpoint and does not measure the synchronous work around it.

## Validator
Grep the file for `async with asyncio.timeout(` or `asyncio.timeout_at(`, and for a `with` of Trio or AnyIO `fail_after`, `fail_at`, `move_on_after`, `move_on_at` or `CancelScope`. Open each block's body and look for an `await` expression, an `async for`, an `async with` or a `yield`; one inside a nested `def` or `lambda` does not run in the block and does not count. Validator question: **Does the body of an asyncio.timeout, Trio or AnyIO fail_after or move_on_after, or CancelScope block in the file contain no await, async for, async with or yield?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-89`, severity major, `file`, `symbol`, `code` = the timeout or cancel-scope `with` line and its body, quoted verbatim from the diff, `fix` = the scope moved around the awaited call it should bound, such as `async with asyncio.timeout(5): blob = await fetch_report(url)`, with the synchronous work after it, or a checkpoint such as `await asyncio.sleep(0)` added inside the scope, `rationale` = without a checkpoint inside the scope the timeout is never triggered and the context manager has no effect).

## Source
- Ruff ASYNC100 cancel-scope-no-checkpoint (astral-sh/ruff crates/ruff_linter/src/rules/flake8_async/rules/cancel_scope_no_checkpoint.rs) — 'Some asynchronous context managers, such as `asyncio.timeout` and `trio.move_on_after`, have no effect unless they contain a checkpoint. The use of such context managers without an `await`, `async with` or `async for` statement is likely a mistake.'; 'For the purposes of this check, `yield` is considered a checkpoint, since checkpoints may occur in the caller to which we yield.' (fetched)
- SonarSource python S7490 (SonarSource/sonar-python python-checks/src/main/resources/org/sonar/l10n/py/rules/python/S7490.html) — 'these mechanisms only work when there are checkpoints within the scope where cancellation can occur. Without any checkpoints, the timeout will never be triggered, making it ineffective.'; 'A checkpoint is a point in the code where cancellation can be detected and acted upon.'; 'Resources might be held longer than intended'; 'The application might become unresponsive or hang'; 'There is no direct checkpoint method in asyncio, but you can use await asyncio.sleep(0) as a workaround'; 'Common checkpoints include: Explicit calls to the checkpoint method of the used framework' (fetched)
- CPython Doc/library/asyncio-task.rst §Task cancellation (https://raw.githubusercontent.com/python/cpython/main/Doc/library/asyncio-task.rst) — 'will be raised in the task at the next opportunity' (fetched)
- CPython Doc/library/asyncio-task.rst §Timeouts (https://raw.githubusercontent.com/python/cpython/main/Doc/library/asyncio-task.rst) — 'the context manager will cancel the current task and handle the resulting :exc:`asyncio.CancelledError` internally, transforming it into a :exc:`TimeoutError` which can be caught and handled.'; 'except *when* is the absolute time to stop waiting' (fetched)
- Caveat: the Trio and AnyIO side, fail_after and CancelScope included, rests on the lint texts, which name trio.move_on_after and trio or anyio cancellation scopes.

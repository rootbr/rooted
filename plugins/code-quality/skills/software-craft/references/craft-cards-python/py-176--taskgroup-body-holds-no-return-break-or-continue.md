---
title: The body of an asyncio TaskGroup or a trio or anyio nursery holds no return, break or continue, because such an exit waits for every task in the group to finish
rule_id: PY-176
domain: errors
step: [implement, review]
applies_to: [python]
triggers: ['async\s+with\s+.*TaskGroup\(', 'open_nursery\(', 'create_task_group\(']
scope: file
check_kind: mechanical
severity_default: major
---

# The body of an asyncio TaskGroup or a trio or anyio nursery holds no return, break or continue, because such an exit waits for every task in the group to finish

## Thesis
Inside `async with asyncio.TaskGroup()`, `async with trio.open_nursery()` or `async with anyio.create_task_group()`, the body holds no `return`, `break` or `continue` that leaves the block: the control-flow statement moves outside the block, and where the exit is meant to come early the body records the result in a variable and uses the cancellation mechanism before exiting the block — `task.cancel()` on the asyncio tasks still running, `tg.cancel()` on an `asyncio.TaskGroup` from Python 3.15, `nursery.cancel_scope.cancel()` in trio, `tg.cancel_scope.cancel()` in anyio.

## Rationale
Python's `async with` is semantically equivalent to a `try` statement whose `finally` clause runs `await aexit(None, None, None)` when the suite raised nothing, so a `return`, `break` or `continue` in the suite awaits the manager's exit before it takes effect; after a non-exception exit, execution proceeds at the normal location for the kind of exit that was taken. The exit of `asyncio.TaskGroup` waits for all tasks in the group to finish, and a trio nursery block does not exit until all of its tasks have completed, so a control-flow statement in an asyncio TaskGroup does not take immediate effect: it waits for all tasks in the group to complete before executing. The costs are unexpected delays when tasks run longer than anticipated, code that appears to exit early but actually continues running, and potential infinite loops if background tasks never complete. In trio and anyio nurseries a return value can also be lost when another task in the nursery raises an exception: the nursery's exception handling takes precedence over the return value, a silent data loss that is difficult to debug.

## Example
```python
bad:  async with asyncio.TaskGroup() as tg:
          tg.create_task(background_job())
          return await first_result()
good: async with asyncio.TaskGroup() as tg:
          task = tg.create_task(background_job())
          result = await first_result()
          task.cancel()
      return result
```

## Limits
The rule reaches a `return`, `break` or `continue` used inside one of the three task-group managers `asyncio.TaskGroup`, `trio.open_nursery` and `anyio.create_task_group`. A `return` inside a function or class defined within the body, and a `break` or `continue` of a loop that lies wholly inside the body, do not exit the block's suite, so the manager's exit does not run for them. Leaving the block by an exception is outside the rule.

## Validator
Grep the hunk for `async with` headers that call `asyncio.TaskGroup(`, `TaskGroup(`, `trio.open_nursery(`, `open_nursery(`, `anyio.create_task_group(` or `create_task_group(`. For each, open the whole block and list every `return`, `break` and `continue` in its body; drop a `return` inside a nested `def`, `async def` or `class`, and a `break` or `continue` whose loop starts inside the body. Validator question: **Does a return, break or continue in the body of an asyncio TaskGroup, trio nursery or anyio task group block leave that block?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-176`, severity major, `file`, `symbol`, `code` = the `async with` header and the control-flow statement quoted verbatim from the diff, `fix` = the result stored in a variable, the remaining tasks cancelled inside the block with `task.cancel()`, `tg.cancel()`, `nursery.cancel_scope.cancel()` or `tg.cancel_scope.cancel()`, and the `return`, `break` or `continue` placed after the block, `rationale` = the exit waits for every task in the group, and in a trio or anyio nursery another task's exception discards the return value).

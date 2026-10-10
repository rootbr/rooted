---
title: The task returned by asyncio.create_task or asyncio.ensure_future stays referenced from a variable, a collection or a TaskGroup until it is done, since the event loop keeps only weak references to tasks
rule_id: PY-85
domain: errors
step: [implement, review]
applies_to: [python]
triggers: ['^\s*asyncio[.](?:create_task|ensure_future)\(', '^\s*\w*loop[.]create_task\(']
scope: hunk
check_kind: mechanical
severity_default: major
---

# The task returned by asyncio.create_task or asyncio.ensure_future stays referenced from a variable, a collection or a TaskGroup until it is done, since the event loop keeps only weak references to tasks

## Thesis
In Python, the task returned by a call to `asyncio.create_task()` or `asyncio.ensure_future()` stays referenced until it is done: it is bound to a name that outlives the task, added to a collection from which a done callback removes it on completion, or created through `asyncio.TaskGroup.create_task` inside the group's `async with` block, rather than left as a bare expression statement that discards the returned task.

## Rationale
The asyncio event loop only keeps weak references to tasks, so a task that is not referenced elsewhere may get garbage collected at any time, even before it is done, and disappear mid-execution. Such tasks may or may not run to completion, which can lead to unexpected and inconsistent behaviour. Adding the task to a set creates a strong reference, and a done callback that discards the task from the set keeps the set from holding references to finished tasks forever. That set never awaits its tasks, so if a task fails its exception is never retrieved and asyncio logs a "Task exception was never retrieved" message when the task is garbage collected; `asyncio.TaskGroup` keeps a strong reference to each task, awaits the tasks and propagates their exceptions.

## Example
```python
bad:  async def handle(event, loop):
          asyncio.create_task(send_metrics(event))
          loop.create_task(write_audit(event))
good: background_tasks = set()
      async def handle(event, loop):
          for task in (asyncio.create_task(send_metrics(event)),
                       loop.create_task(write_audit(event))):
              background_tasks.add(task)
              task.add_done_callback(background_tasks.discard)
```

## Limits
A task bound to a name and later awaited, passed to `asyncio.gather()` or `asyncio.wait()`, or otherwise referenced until it is done meets the rule. `asyncio.TaskGroup` is available from Python 3.11 and fits tasks that should be awaited as part of the current operation; reliable fire-and-forget background tasks go into a collection instead. A task held in a set with no done callback keeps its strong reference and is outside the rule, which covers the reference that keeps a task alive.

## Validator
Grep the hunk for `asyncio.create_task(`, `asyncio.ensure_future(` and an event loop's `create_task(`, which also returns a Task. For each call, read the statement that holds it: a bare expression statement drops the task; an assignment to a local name counts only when that name is awaited, returned, added to a collection or stored on an attribute before the enclosing function returns; `tg.create_task(...)` inside `async with asyncio.TaskGroup() as tg` is held by the group. Open the enclosing function when the assigned name's later use lies outside the hunk. Validator question: **Does a create_task or ensure_future call in the hunk leave its task with no strong reference that lasts until the task is done?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-85`, severity major, `file`, `symbol`, `code` = the `create_task` or `ensure_future` statement whose task is dropped, quoted verbatim from the diff, `fix` = the task added to a module-level set with `task.add_done_callback(background_tasks.discard)`, or created by `tg.create_task(...)` inside `async with asyncio.TaskGroup() as tg`, `rationale` = the event loop keeps only weak references to tasks, so a task referenced nowhere else may be garbage collected before it is done).

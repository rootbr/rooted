---
title: An async function that waits for a condition another task of the program changes awaits an asyncio, trio or anyio Event that the changing code sets, not a while loop around an async sleep
rule_id: PY-92
domain: errors
step: [implement, refactor, review]
applies_to: [python]
triggers: ['^\s*await\s+(?:asyncio|trio|anyio)[.]sleep\(', '^\s*while\s+not\s+[\w.()]+\s*:']
scope: hunk
check_kind: semantic
severity_default: minor
---

# An async function that waits for a condition another task of the program changes awaits an asyncio, trio or anyio Event that the changing code sets, not a while loop around an async sleep

## Thesis
In Python async code, a `while` loop whose body awaits `asyncio.sleep`, `trio.sleep` or `anyio.sleep` to recheck a condition that another part of the program changes is replaced by an `asyncio.Event`, `trio.Event` or `anyio.Event`: the waiting task awaits `event.wait()`, and the code that changes the condition calls `event.set()`.

## Rationale
Busy-waiting for a condition in a loop forces a tradeoff between efficiency and latency: shorter sleep times improve responsiveness but waste more CPU cycles, while longer sleep times reduce CPU usage but delay reaction to state changes. The task only notices the condition change after the sleep interval expires, so if the condition becomes true just after the task starts sleeping, the reaction is delayed. A task that awaits `event.wait()` pauses until another part of the program signals the event with `event.set()`, consumes almost no resources while paused and reacts immediately when the event is set, which eliminates the tradeoff. An asyncio event can be used to notify multiple asyncio tasks that some event has happened: its `wait()` method blocks until its internal flag is set to true by `set()`.

## Example
```python
bad:  async def wait_until_ready(self):
          while not self.ready:
              await asyncio.sleep(0.05)
good: def __init__(self):
          self.ready = asyncio.Event()
      async def wait_until_ready(self):
          await self.ready.wait()
      def on_connected(self):
          self.ready.set()
```

## Limits
`asyncio.Event` is not thread-safe, so a condition that another thread changes is outside this rule. A loop that sleeps between rounds of periodic work, or rechecks a state that no part of the program signals, has no code that would call `event.set()`, and the rule does not reach it.

## Validator
Grep the hunk for `await asyncio.sleep(`, `await trio.sleep(` or `await anyio.sleep(` inside a `while` loop. Read the loop's condition and the checks in its body to name the flag or state it waits on, then search the file and its package for the code that changes that state. Count the loop a busy-wait when that code is a task, callback or handler of the same program running on the same event loop. Validator question: **Does a `while` loop in the hunk await `asyncio.sleep`, `trio.sleep` or `anyio.sleep` to recheck a condition that another task or callback of the same program changes?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-92`, severity minor, `file`, `symbol`, `code` = the `while` header and the awaited sleep inside it, `fix` = an `asyncio.Event` (or `trio.Event`, `anyio.Event`) created once, `await event.wait()` in place of the loop and `event.set()` where the condition changes, `rationale` = that a sleep-polling loop trades wasted CPU cycles against delayed reaction, while a task waiting on an event reacts immediately when it is set).

---
title: An async def whose own body has no await, async for or async with is a plain def, unless an inherited, framework or test contract requires a coroutine
rule_id: PY-177
domain: errors
step: [design, implement, refactor, review]
applies_to: [python]
triggers: ['^\s*async\s+def\s+\w+\s*\(', '^\s*async\s+def\s+\w+\s*\[']
scope: file
check_kind: semantic
severity_default: minor
---

# An async def whose own body has no await, async for or async with is a plain def, unless an inherited, framework or test contract requires a coroutine

## Thesis
A Python function declared `async def` whose own body — the bodies of nested functions and classes aside — contains no `await`, `async for` or `async with` is declared with `def`, unless being a coroutine is the point: an async test or callback that must run in an async execution context, an abstract method, an async special method such as `__aenter__`, `__aexit__` or `__anext__`, a decorated function such as a framework route handler or an `asynccontextmanager` function, a method overriding an async method, or a stub whose body is only `pass`, `...` or `raise` statements.

## Rationale
Functions defined with `async def` are always coroutine functions, even if they do not contain `await` or `async` keywords, and simply calling a coroutine does not schedule it to be executed: callers must use `await`, or schedule it as a task, to execute the coroutine and get its result. When none of the asynchronous mechanisms is used in the body, the `async` declaration is superfluous and artificially limits the contexts where the function may be called. It also misleads readers into thinking the function performs asynchronous operations, and each call creates a coroutine object, more overhead than a direct synchronous function call. Declaring a function `async` when it is not is usually a mistake.

## Example
```python
bad:  async def merge_settings(defaults, overrides):
          return {**defaults, **overrides}
      settings = await merge_settings(base, local)
good: def merge_settings(defaults, overrides):
          return {**defaults, **overrides}
      settings = merge_settings(base, local)
```

## Limits
An async test or callback may need to run in an async execution context even if it only uses a `ContextVar`, and some frameworks require callbacks to be coroutines, such as `httpx.AsyncClient` event hooks; where the async context is intentional, the function gains an actual await expression such as `await asyncio.sleep(0)` or a suppression of the rule for that function. A decorated function, such as a framework route handler or a function under `contextlib.asynccontextmanager`, is outside the rule, as decorators may change the function's behaviour in ways that make the `async` keyword meaningful. A `yield` expression in an `async def` body makes the function an asynchronous generator function, whose call returns an asynchronous iterator, while the same body under `def` makes a generator function, so the rule reaches coroutine functions without `yield`. Methods are a split case: one position excludes class methods, as they often have to be async for other reasons; the other flags a method unless it is abstract, an async special method or an override of an async method, and makes an inherited contract explicit by inheriting from the relevant base class or protocol and marking the method as an override.

## Validator
Grep the hunk for `async def` lines; open the file and read each such function's own body, skipping the bodies of nested `def`, `async def` and `class`. Look for `await`, `async for`, `async with` and `yield`. Skip the function when it carries a decorator, when its body is only `pass`, `...` or `raise` statements, when it is an async special method or an `@abstractmethod`, when it overrides an async method of a base class or protocol (open the base), when it is a test the project's async test plugin runs, and when it is passed where a coroutine is required, such as a framework event hook or callback registration. Validator question: **Is the function an async def whose own body has no await, async for, async with or yield, with none of those coroutine contracts applying?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-177`, severity minor, `file`, `symbol`, `code` = the `async def` line quoted verbatim from the diff, `fix` = the same function declared with `def` and its callers calling it without `await`, `rationale` = the body uses no await, async for or async with, so the async declaration is superfluous and forces every caller to await the function or schedule it as a task).

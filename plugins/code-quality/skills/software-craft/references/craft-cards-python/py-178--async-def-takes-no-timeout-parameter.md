---
title: An async def takes no timeout parameter, leaving the deadline to the caller's asyncio.timeout on Python 3.11 or later or trio or anyio timeout scope
rule_id: PY-178
domain: errors
step: [design, review]
applies_to: [python]
triggers: ['async\s+def\s+\w+\s*\(.*\btimeout\b', '^\s+timeout\s*:\s*\w']
scope: file
check_kind: mechanical
severity_default: minor
---

# An async def takes no timeout parameter, leaving the deadline to the caller's asyncio.timeout on Python 3.11 or later or trio or anyio timeout scope

## Thesis
A Python `async def` declares no `timeout` parameter: under structured concurrency the caller of an asynchronous function, not the callee, should be responsible for managing timeouts and cancellation, so the caller wraps the `await` in `async with asyncio.timeout(...)` or in a `with` scope from trio's or anyio's `fail_after` or `move_on_after`. For asyncio the rule holds on Python 3.11 and later, where `asyncio.timeout` exists, and a method decorated with `@typing.override` keeps the parameter its base declares.

## Rationale
`asyncio.timeout` returns an asynchronous context manager that can be used to limit the amount of time spent waiting on something, timeout context managers can be safely nested, and the asyncio components that enable structured concurrency, like `asyncio.TaskGroup` and `asyncio.timeout`, are implemented using cancellation internally. That design lets an `async` function stay oblivious to timeouts and leaves the logic to the caller's context manager. A `timeout` parameter makes the function dictate how the timeout is handled internally rather than letting the caller decide, and preempts the caller's control, since the caller might want to enforce a different timeout duration or coordinate timeouts across several concurrent operations. Combining functions that manage their own timeouts can lead to complex and unpredictable behaviour, especially when nesting calls or running tasks concurrently under a shared deadline.

## Example
```python
bad:  async def fetch_page(url, timeout):
          return await asyncio.wait_for(client.get(url), timeout)
      async def main(url):
          return await fetch_page(url, 5)
good: async def fetch_page(url):
          return await client.get(url)
      async def main(url):
          async with asyncio.timeout(5):
              return await fetch_page(url)
```

## Limits
`asyncio.timeout` was added in Python 3.11, so for asyncio code whose supported floor is below Python 3.11 the rule does not apply. A method decorated with `@typing.override` is exempt: removing a parameter from a subclass method may make type checkers report a violation of the Liskov Substitution Principle when the method then incompatibly overrides a method defined on a superclass. A function written to wrap `asyncio.timeout`, `trio.fail_after` or `anyio.move_on_after` is a false positive of the parameter-name check, which a different parameter name avoids. The rule is highly opinionated: it enforces one design pattern, structured concurrency, and reaches asynchronous functions only.

## Validator
Grep the hunk for `async def` signatures with a parameter named `timeout`, including a multi-line signature whose parameter line reads `timeout: ...` or `timeout=...`. Read the file's imports: with no `trio` or `anyio` import the framework is asyncio, and then read `requires-python` in `pyproject.toml` or Ruff's `target-version`, skipping the function when the floor is below 3.11. Skip a method decorated with `@override` or `@typing.override`, and a helper whose purpose is to apply `asyncio.timeout`, `trio.fail_after` or `anyio.move_on_after` to an awaitable it receives. Validator question: **Does an async def in the hunk declare a parameter named timeout outside those exemptions?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-178`, severity minor, `file`, `symbol`, `code` = the `async def` signature with its `timeout` parameter quoted verbatim from the diff, `fix` = the signature without `timeout` and the caller's `async with asyncio.timeout(...)`, or trio's or anyio's `with fail_after(...)` or `with move_on_after(...)`, around the `await`, `rationale` = the caller owns the deadline under structured concurrency, and functions that manage their own timeouts compose unpredictably when calls nest or tasks share a deadline).

## Source
- SonarSource python rule S7483 (SonarSource/sonar-python python-checks/src/main/resources/org/sonar/l10n/py/rules/python/S7483.html) — 'the caller of an asynchronous function should be responsible for managing timeouts and cancellation, not the callee.' (fetched)
- SonarSource python rule S7483 (SonarSource/sonar-python python-checks/src/main/resources/org/sonar/l10n/py/rules/python/S7483.html) — 'The function dictates how the timeout is handled internally, rather than letting the caller decide.' and 'The caller might want to enforce a different timeout duration or coordinate timeouts across several concurrent operations.' (fetched)
- SonarSource python rule S7483 (SonarSource/sonar-python python-checks/src/main/resources/org/sonar/l10n/py/rules/python/S7483.html) — 'Combining functions that manage their own timeouts can lead to complex and unpredictable behavior, especially when nesting calls or running tasks concurrently under a shared deadline.' (fetched)
- Ruff ASYNC109 async-function-with-timeout (astral-sh/ruff crates/ruff_linter/src/rules/flake8_async/rules/async_function_with_timeout.rs) — 'This rule is highly opinionated to enforce a design pattern called ["structured concurrency"] that allows for `async` functions to be oblivious to timeouts, instead letting callers to handle the logic with a context manager.' (fetched)
- Ruff ASYNC109 async-function-with-timeout (astral-sh/ruff crates/ruff_linter/src/rules/flake8_async/rules/async_function_with_timeout.rs) — 'prefer built-in timeout functionality, such as `asyncio.timeout`, `trio.fail_after`, or `anyio.move_on_after`, among others', '`asyncio.timeout` was added in Python 3.11' and 'This rule exempts methods decorated with [`@typing.override`][override].' (fetched)
- Ruff ASYNC109 async-function-with-timeout (astral-sh/ruff crates/ruff_linter/src/rules/flake8_async/rules/async_function_with_timeout.rs) — 'Removing a parameter from a subclass method may cause type checkers to complain about a violation of the Liskov Substitution Principle' and 'false positives from this rule can be avoided by using a different parameter name' (fetched)
- flake8-async ASYNC109 async-function-with-timeout (python-trio/flake8-async docs/rules.rst) — 'In structured concurrency the caller should instead use :ref:`timeout context managers <timeout_context>`.' (fetched)
- CPython Doc/library/asyncio-task.rst §Timeouts (https://raw.githubusercontent.com/python/cpython/main/Doc/library/asyncio-task.rst) — 'that can be used to limit the amount of time spent waiting on something' and 'Timeout context managers can be safely nested.' (fetched)
- CPython Doc/library/asyncio-task.rst §Task cancellation (https://raw.githubusercontent.com/python/cpython/main/Doc/library/asyncio-task.rst) — 'are implemented using cancellation internally' (fetched)
- Caveat: trio's and anyio's `fail_after` and `move_on_after` are named from the tool texts; their own documentation was not fetched.

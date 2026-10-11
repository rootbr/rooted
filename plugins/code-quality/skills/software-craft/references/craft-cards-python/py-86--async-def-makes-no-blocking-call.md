---
title: An async def function makes no blocking call such as time.sleep, a synchronous file open, a blocking os.path or pathlib call, a synchronous subprocess run or wait, input() or a synchronous HTTP request, and awaits an async equivalent or runs the call in a thread
rule_id: PY-86
domain: errors
step: [implement, review]
applies_to: [python]
triggers: ['\btime[.]sleep\(', '\brequests[.](?:get|post|put|patch|delete|head|request)\(', '\bsubprocess[.](?:run|call|check_call|check_output|Popen)\(', '\burlopen\(|\bhttpx[.]Client\(', '\bwith\s+open\(|\bos[.]path[.](?:exists|isfile|isdir|getsize)\(', '\binput\(']
scope: file
check_kind: mechanical
severity_default: major
---

# An async def function makes no blocking call such as time.sleep, a synchronous file open, a blocking os.path or pathlib call, a synchronous subprocess run or wait, input() or a synchronous HTTP request, and awaits an async equivalent or runs the call in a thread

## Thesis
In Python, code in an `async def` function calls no function that blocks its thread — `time.sleep`, `open()` and other synchronous file operations, the `os.path` functions and `pathlib.Path` methods that block, `subprocess.run`, `subprocess.Popen`, `os.popen`, `os.wait` or `os.waitpid`, `input()`, or an HTTP request through `requests`, `urllib`, `urllib3` or `httpx.Client` — and instead awaits the async library's equivalent or runs the call in another thread through `asyncio.to_thread` or `loop.run_in_executor`.

## Rationale
An asyncio, Trio or AnyIO program relies on a single-threaded event loop to manage multiple tasks concurrently, and the loop manages them by having them yield control during time-consuming operations, so that other tasks run. A synchronous call such as `time.sleep()` halts the current thread and so blocks the entire event loop: the loop cannot switch between tasks, process I/O events or respond to other operations, and all other concurrent tasks are paused until the call completes. The asyncio documentation states the cost with a CPU-bound example: if a function performs a CPU-intensive calculation for 1 second, all concurrent asyncio Tasks and IO operations would be delayed by 1 second. An asynchronous web server that sleeps this way in a request handler cannot process any other incoming request until the call completes, and in server applications a blocked loop can cause timeouts or failures for other concurrent requests. The async libraries provide separate non-blocking APIs that give control back to the event loop — `asyncio.sleep` for `time.sleep`, `httpx.AsyncClient` or `aiohttp` for HTTP, `asyncio.create_subprocess_exec`, `trio.run_process` or `anyio.run_process` for subprocesses, `anyio.Path`, `trio.Path` or `aiofiles.os.path` for path operations — and since the standard library's asyncio package provides no built-in asynchronous file I/O, file access goes through `aiofiles`, `trio.open_file` or `anyio.open_file`. An executor runs the call in a different thread, interpreter or process to avoid blocking the OS thread with the event loop, and `asyncio.to_thread` asynchronously runs a function in a separate thread.

## Example
```python
bad:  async def poll_status(url, retry_delay):
          while requests.get(url).status_code != 200:
              time.sleep(retry_delay)
          subprocess.run(["notify", url])
good: async def poll_status(url, retry_delay):
          async with httpx.AsyncClient() as client:
              while (await client.get(url)).status_code != 200:
                  await asyncio.sleep(retry_delay)
          await asyncio.to_thread(subprocess.run, ["notify", url])
```

## Limits
Purely computational path operations, such as `os.path.join()` and `pathlib.Path.with_suffix()`, are outside the rule; the lint check for path methods leaves them unflagged. A blocking call inside a plain `def` function that the coroutine runs through `asyncio.to_thread` or `loop.run_in_executor` is the remedy the rule asks for. On Python versions before 3.9, `loop.run_in_executor()` takes the place of `asyncio.to_thread`. Long CPU-bound code in a coroutine also blocks the loop and, per the asyncio documentation, should not be called directly either; the rule's call list names blocking calls and does not reach such code.

## Validator
Grep the file for the trigger calls. For each hit, find the innermost enclosing function: the hit is in scope when that function is an `async def`, and out of scope inside a nested plain `def` that the coroutine hands to `asyncio.to_thread` or `run_in_executor`. For an `os.path` or `pathlib.Path` hit, check that the call reaches the file system (`exists`, `isfile`, `getsize`, `read_text`) rather than only computing a path. Read the rest of each `async def` body for listed calls the triggers do not match, such as `Path.read_text()`, `Popen(...).wait()`, `os.waitpid()` or a `urllib3` request. Validator question: **Does an `async def` function in the file call one of the listed blocking functions directly, instead of awaiting an async equivalent or running it through `asyncio.to_thread` or `loop.run_in_executor`?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-86`, severity major, `file`, `symbol`, `code` = the blocking call quoted verbatim from the diff together with its enclosing `async def` line, `fix` = the awaited async equivalent, such as `await asyncio.sleep(...)`, `await client.get(...)` on an `httpx.AsyncClient`, `await asyncio.create_subprocess_exec(...)` or `anyio.open_file(...)`, or `await asyncio.to_thread(func, *args)`, `rationale` = the synchronous call blocks the entire event loop, so no other task or I/O operation runs until it returns).

## Source
- CPython Doc/library/asyncio-dev.rst §Running Blocking Code (https://raw.githubusercontent.com/python/cpython/main/Doc/library/asyncio-dev.rst) — 'Blocking (CPU-bound) code should not be called directly.  For example, if a function performs a CPU-intensive calculation for 1 second, all concurrent asyncio Tasks and IO operations would be delayed by 1 second.'; 'An executor can be used to run a task in a different thread, including in a different interpreter, or even in a different process to avoid blocking the OS thread with the event loop.' (fetched)
- CPython Doc/library/asyncio-task.rst §Running in threads (https://raw.githubusercontent.com/python/cpython/main/Doc/library/asyncio-task.rst) — 'Asynchronously run function *func* in a separate thread.' (fetched)
- Ruff ASYNC251 blocking-sleep-in-async-function (astral-sh/ruff crates/ruff_linter/src/rules/flake8_async/rules/blocking_sleep.rs) — 'Blocking an async function via a `time.sleep` call will block the entire event loop'; 'Instead of `time.sleep`, use `asyncio.sleep`.' (fetched)
- Ruff ASYNC210 blocking-http-call-in-async-function (astral-sh/ruff crates/ruff_linter/src/rules/flake8_async/rules/blocking_http_call.rs) — 'Blocking an async function via a blocking HTTP call will block the entire event loop'; 'use an asynchronous HTTP client library such as `aiohttp` or `httpx`' (fetched)
- Ruff ASYNC212 blocking-http-call-httpx-in-async-function (astral-sh/ruff crates/ruff_linter/src/rules/flake8_async/rules/blocking_http_call_httpx.rs) — 'Instead of using the blocking `httpx` client, use the asynchronous client.' (fetched)
- Ruff ASYNC220 create-subprocess-in-async-function (astral-sh/ruff crates/ruff_linter/src/rules/flake8_async/rules/blocking_process_invocation.rs) — 'Blocking an async function via a blocking call will block the entire event loop, preventing it from executing other tasks while waiting for the call to complete' (fetched)
- Ruff ASYNC221 run-process-in-async-function (astral-sh/ruff crates/ruff_linter/src/rules/flake8_async/rules/blocking_process_invocation.rs) — 'Checks that async functions do not run processes with blocking methods.' (fetched)
- Ruff ASYNC222 wait-for-process-in-async-function (astral-sh/ruff crates/ruff_linter/src/rules/flake8_async/rules/blocking_process_invocation.rs) — 'Checks that async functions do not wait on processes with blocking methods.' (fetched)
- Ruff ASYNC230 blocking-open-call-in-async-function (astral-sh/ruff crates/ruff_linter/src/rules/flake8_async/rules/blocking_open_call.rs) — 'Checks that async functions do not open files with blocking methods like `open`.' (fetched)
- Ruff ASYNC240 blocking-path-method-in-async-function (astral-sh/ruff crates/ruff_linter/src/rules/flake8_async/rules/blocking_path_methods.rs) — 'Calling some `os.path` functions or `pathlib.Path` methods in an async function will block the entire event loop'; 'or use an API that provides asynchronous path operations, such as `aiofiles.os.path`, `anyio.Path`, or `trio.Path`'; 'Purely computational path operations, such as `os.path.join()` and `pathlib.Path.with_suffix()`, are not flagged.'; 'On earlier Python versions, use `loop.run_in_executor()`.' (fetched)
- Ruff ASYNC250 blocking-input-in-async-function (astral-sh/ruff crates/ruff_linter/src/rules/flake8_async/rules/blocking_input.rs) — 'wrap the input call in an executor to execute the blocking call on another thread' (fetched)
- SonarSource python S7488 (SonarSource/sonar-python python-checks/src/main/resources/org/sonar/l10n/py/rules/python/S7488.html) — 'In an asynchronous context, which relies on a single-threaded event loop to manage multiple tasks concurrently, calling time.sleep() blocks this entire event loop.'; 'it cannot switch between tasks, process I/O events, or respond to other operations'; 'all other concurrent asynchronous tasks are paused until the time.sleep() call completes'; 'it won’t be able to process any other incoming requests until the sleep call completes'; 'These functions give control back to the event loop' (fetched)
- SonarSource python S7487 (SonarSource/sonar-python python-checks/src/main/resources/org/sonar/l10n/py/rules/python/S7487.html) — 'Using synchronous subprocess calls like subprocess.Popen or similar functions in asynchronous code blocks the entire event loop.'; 'In server applications, this can cause timeouts or failures for other concurrent requests'; 'Instead, async libraries provide dedicated APIs for running subprocesses in a non-blocking way' (fetched)
- SonarSource python S7489 (SonarSource/sonar-python python-checks/src/main/resources/org/sonar/l10n/py/rules/python/S7489.html) — 'Using synchronous operating system calls like os.wait(), os.waitpid(), or similar functions in asynchronous code blocks the entire event loop.' (fetched)
- SonarSource python S7493 (SonarSource/sonar-python python-checks/src/main/resources/org/sonar/l10n/py/rules/python/S7493.html) — 'Using synchronous file operations like open() in asynchronous code blocks the entire event loop.'; 'package doesn’t provide built-in asynchronous file I/O operations'; 'async libraries provide mechanisms to handle file operations asynchronously' (fetched)
- SonarSource python S7499 (SonarSource/sonar-python python-checks/src/main/resources/org/sonar/l10n/py/rules/python/S7499.html) — 'Using synchronous HTTP clients like urllib3, requests, or httpx.Client in asynchronous code blocks the entire event loop.' (fetched)
- SonarSource python S7501 (SonarSource/sonar-python python-checks/src/main/resources/org/sonar/l10n/py/rules/python/S7501.html) — 'an event loop manages concurrent tasks by having them yield control during time-consuming operations, enabling other tasks to run'; 'when called from a coroutine, it blocks the entire event loop' (fetched)
- Caveat: the asyncio documentation states the cost with a CPU-bound example; the blocking I/O calls are named by the lint rules.

---
title: A with statement that takes a threading lock enters a lock object created once outside it and shared by the threads it guards, never a threading.Lock or similar lock constructed in the with header
rule_id: PY-93
domain: errors
step: [implement, review]
applies_to: [python]
triggers: ['\bwith\s+threading[.](?:Lock|RLock|Semaphore|BoundedSemaphore|Condition)\(', '\bwith\s+(?:Lock|RLock|Semaphore|BoundedSemaphore|Condition)\(']
scope: hunk
check_kind: mechanical
severity_default: major
---

# A with statement that takes a threading lock enters a lock object created once outside it and shared by the threads it guards, never a threading.Lock or similar lock constructed in the with header

## Thesis
In Python, a `with` statement that takes a `threading` lock enters an existing lock instance, assigned to a variable outside the `with` statement and shared by the threads that touch the state it guards, never a `threading.Lock()` or similar lock constructed in the `with` header.

## Rationale
Every `threading` object with `acquire` and `release` methods can be used as a context manager for a `with` statement: `acquire` is called when the block is entered, and `release` is called when the block is exited. A `with` header that calls `threading.Lock()` creates a new lock instance, and creating a lock (via `threading.Lock` or similar) in a `with` statement has no effect, as locks are only relevant when shared between threads. A lock shared between threads excludes them from each other: when its state is locked, `acquire()` blocks until a call to `release()` in another thread changes it to unlocked.

## Example
```python
bad:  def increment(self):
          with threading.Lock():
              self.count += 1
      def reset(self):
          with Lock(): self.count = 0
good: def __init__(self):
          self.lock = threading.Lock()
      def increment(self):
          with self.lock:
              self.count += 1
```

## Limits
The rule reaches lock objects that are created and immediately discarded in `with` statements; a `with` statement that enters an existing instance, such as a module-level lock or an attribute assigned once, is the form the rule asks for. Whether every thread that touches the state takes that same lock is a question of concurrency design that this rule does not reach.

## Validator
Grep the hunk for a `with` header that calls `threading.Lock(`, `threading.RLock(`, `threading.Semaphore(`, `threading.BoundedSemaphore(` or `threading.Condition(`, or one of those names imported from `threading`; open the file's imports to confirm where a bare `Lock(` or `Condition(` comes from. Validator question: **Does a `with` statement in the hunk construct a `threading` lock, semaphore or condition in its header instead of entering an existing instance shared between threads?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-93`, severity major, `file`, `symbol`, `code` = the `with` header that constructs the lock, `fix` = the lock assigned once outside the `with` statement, as `self._lock = threading.Lock()` in `__init__` or a module-level `lock = threading.Lock()`, and `with self._lock:` at the guarded block, `rationale` = that a lock created in the `with` statement is not shared between threads and has no effect).

## Source
- Ruff PLW2101 useless-with-lock (astral-sh/ruff crates/ruff_linter/src/rules/pylint/rules/useless_with_lock.rs) — 'Creating a lock (via `threading.Lock` or similar) in a `with` statement has no effect, as locks are only relevant when shared between threads.' (fetched)
- Ruff PLW2101 useless-with-lock (astral-sh/ruff crates/ruff_linter/src/rules/pylint/rules/useless_with_lock.rs) — 'Instead, assign the lock to a variable outside the `with` statement, and share that variable between threads.' (fetched)
- Ruff PLW2101 useless-with-lock (astral-sh/ruff crates/ruff_linter/src/rules/pylint/rules/useless_with_lock.rs) — 'Checks for lock objects that are created and immediately discarded in `with` statements.' (fetched)
- Pylint useless-with-lock (W2101) (pylint-dev/pylint doc/data/messages/u/useless-with-lock/bad.py) — 'Used when a new lock instance is created by using with statement which has no effect. Instead, an existing instance should be used to acquire lock.' (fetched)
- CPython Doc/library/threading.rst §Using locks, conditions, and semaphores in the with statement (https://raw.githubusercontent.com/python/cpython/main/Doc/library/threading.rst) — 'All of the objects provided by this module that have ``acquire`` and ``release`` methods can be used as context managers for a :keyword:`with` statement.  The ``acquire`` method will be called when the block is entered, and ``release`` will be called when the block is exited.' (fetched)
- CPython Doc/library/threading.rst §Lock objects (https://raw.githubusercontent.com/python/cpython/main/Doc/library/threading.rst) — 'When the state is locked, :meth:`~Lock.acquire` blocks until a call to :meth:`~Lock.release` in another thread changes it to unlocked' (fetched)

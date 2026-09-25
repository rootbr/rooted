---
title: A ThreadLocal set on a pooled thread is removed in a finally block, and set(null) is not a removal
rule_id: REL-03
domain: reliability
triggers: ['ThreadLocal', '\b[A-Z][A-Z0-9_]*[.]set\(', '[.]set\(null\)', 'MDC[.]put\(', 'RequestContextHolder', 'InheritableThreadLocal']
scope: file
check_kind: mechanical
severity_default: major
---

# A ThreadLocal set on a pooled thread is removed in a finally block, and set(null) is not a removal

## Thesis
Every `ThreadLocal.set` executed on a thread that returns to a pool — a servlet or filter thread, an executor worker, a `CompletableFuture` stage — is paired with `remove()` in a `finally` block on the same thread, so the value cannot outlive the unit of work; `set(null)` leaves the entry in place and is not the pairing.

## Rationale
Each thread holds an implicit reference to its copy of a thread-local variable as long as the thread is alive and the `ThreadLocal` instance is accessible. A pooled thread stays alive across requests, so a value set for one request and not removed is still there when the thread serves the next: a user id, a tenant, a transaction context read by code that did not set it, and a reference that keeps the value's object graph reachable for the life of the pool. `remove()` deletes the thread's entry, after which the next `get()` reinitializes from `initialValue()`. `set(null)` writes `null` into the existing entry; the entry, and with it the thread-local key, remains in the thread's map.

## Example
```java
bad:  CURRENT.set(user);
      handle(request);
      CURRENT.set(null);
good: CURRENT.set(user);
      try { handle(request); } finally { CURRENT.remove(); }
```

## Limits
Applies to a thread the code does not own for the value's lifetime: pooled, borrowed, or a virtual thread with a per-task lifetime shorter than the value. A `ThreadLocal` set once on a dedicated long-lived thread the class starts and stops, or one whose value is immutable configuration read for the thread's whole life, is out of scope. A `set` inside a framework callback that documents its own cleanup — a filter whose `finally` the framework supplies — is correct when the diff shows that cleanup. `ScopedValue` bindings need no removal; their scope ends with the `run` or `call` block.

## Validator
On the triggered hunk find each `ThreadLocal.set`, `MDC.put`, or context-holder `set` call. Open the file: locate the `remove()` (or `MDC.remove`/`clear`) for the same key and check that it sits in a `finally` whose `try` begins at or before the `set`, on the same thread, covering every exit including exceptions. Treat `set(null)` as absent cleanup. Validator question: **is there an exit from this unit of work on which the pooled thread keeps the value?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: REL-03`, severity major, `file`, `symbol`, `code` = the `set` call and the cleanup line, or its absence, quoted verbatim from the diff, `fix` = the `try`/`finally` with `remove()`, `rationale` naming the value that leaks to the next unit of work on the pooled thread).

## Source
`java.lang.ThreadLocal` Javadoc, Java SE 21 — class: "Each thread holds an implicit reference to its copy of a thread-local variable as long as the thread is alive and the ThreadLocal instance is accessible"; `#remove` — "Removes the current thread's value for this thread-local variable. If this thread-local variable is subsequently read by the current thread, its value will be reinitialized by invoking its initialValue method"; `#set` — "Sets the current thread's copy of this thread-local variable to the specified value"; that `set(null)` keeps the entry is read from the class source (`set` writes through `ThreadLocalMap.set(this, value)`, `remove` calls `ThreadLocalMap.remove(this)`), not from the `#set` Javadoc. `java.lang.ScopedValue` class Javadoc, Java SE 21 (preview API) — a value is bound "for the bounded period of execution of a method" and "reverts to being unbound when the original method completes normally or with an exception", for a `Runnable.run`, `Callable.call` or `Supplier.get`. SEI CERT Oracle Coding Standard for Java, TPS04-J "Ensure ThreadLocal variables are reinitialized when using thread pools".

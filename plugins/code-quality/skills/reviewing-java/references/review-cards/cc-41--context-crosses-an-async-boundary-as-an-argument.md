---
title: Context a CompletableFuture stage or a submitted task needs travels as an explicit argument or captured value, never through a ThreadLocal set on the submitting thread
rule_id: CC-41
domain: concurrency
triggers: ['ThreadLocal', 'MDC[.]', 'ContextHolder', 'supplyAsync\(', 'runAsync\(', 'then(Apply|Accept|Compose|Run|Combine)(Async)?\(']
scope: file
check_kind: semantic
severity_default: major
---

# Context a CompletableFuture stage or a submitted task needs travels as an explicit argument or captured value, never through a ThreadLocal set on the submitting thread

## Thesis
A value that a task or a dependent stage reads — a user id, a tenant, a trace id, a security context — is read on the submitting thread and passed into the lambda as a captured variable or a parameter, or carried by an executor wrapper that copies it into the task; the task does not call `ThreadLocal.get()`, `MDC.get()` or a context holder expecting the submitter's value.

## Rationale
A thread-local variable is per thread: each thread that accesses it has its own independently initialized copy. A stage of a `CompletableFuture` chain may run on the thread that completes the previous stage, on any caller of a completion method, or — for the async variants — on a common-pool or executor thread; a submitted task runs on a pool worker. None of these is the submitting thread, so `get()` inside the task returns that thread's own copy: empty, or the value a previous task left on the same pooled worker, which then authorizes, tags or bills the wrong user. `InheritableThreadLocal` does not help: a child receives values when the thread is created, and pooled workers were created long before this task. A captured local or a parameter is copied into the task object at submission and is the same value on whatever thread runs it; an executor decorator that reads the context at submission and re-installs it around the task achieves the same for frameworks that insist on thread-locals.

## Example
```java
bad:  CURRENT_USER.set(user);
      CompletableFuture.supplyAsync(() -> audit.load(CURRENT_USER.get()), pool);   // the pool thread's own copy
good: User u = CURRENT_USER.get();
      CompletableFuture.supplyAsync(() -> audit.load(u), pool);
```

## Limits
Applies to a `ThreadLocal`, `MDC` or context-holder read inside a task or stage that can run on a thread other than the one that set it. A `thenApply` a framework guarantees to run on the completing thread that also set the value is correct only when the file shows both. An executor wrapper — a task decorator, a context-propagating `Executor` — that copies the value into each task, shown in the file or named in the project context, makes the read valid. A `ScopedValue` bound around a `StructuredTaskScope` is inherited by the forked subtasks by design.

## Validator
On the triggered hunk find each task body or stage lambda and each `ThreadLocal.get`, `MDC.get` or holder `get` inside it, or inside a method it calls in the file. Locate where that value is set: on the submitting thread before submission, outside the lambda. Check for a propagating executor or decorator. Validator question: **does code that may run on another thread read a thread-local value that was set on the submitting thread, with nothing copying it across?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: CC-41`, severity major, `file`, `symbol`, `code` = the thread-local read inside the task and the set outside it quoted verbatim from the diff, `fix` = the value read before submission and captured or passed in, or the propagating executor, `rationale` naming the other thread's own copy, empty or stale from a previous task).

## Source
`java.lang.ThreadLocal` class Javadoc, Java SE 21 — "each thread that accesses one (via its get or set method) has its own, independently initialized copy of the variable"; `java.lang.InheritableThreadLocal` — "when a child thread is created, the child receives initial values for all inheritable thread-local variables for which the parent has values"; `java.util.concurrent.CompletableFuture` class Javadoc — "Actions supplied for dependent completions of non-async methods may be performed by the thread that completes the current CompletableFuture, or by any other caller of a completion method"; "All async methods without an explicit Executor argument are performed using the ForkJoinPool.commonPool()".

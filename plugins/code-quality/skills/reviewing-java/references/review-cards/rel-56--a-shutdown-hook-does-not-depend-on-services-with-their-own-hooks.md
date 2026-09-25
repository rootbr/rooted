---
title: A JVM shutdown hook is short, thread-safe, and does not rely on a service — logging, a pool, an executor — that has registered its own shutdown hook
rule_id: REL-56
domain: reliability
triggers: ['addShutdownHook\(', 'removeShutdownHook\(', 'Runtime[.]getRuntime\(\)']
scope: file
check_kind: mechanical
severity_default: minor
---

# A JVM shutdown hook is short, thread-safe, and does not rely on a service — logging, a pool, an executor — that has registered its own shutdown hook

## Thesis
A thread registered with `Runtime.addShutdownHook` does bounded work that uses only what it owns: it does not log through a framework that stops itself in its own hook, does not submit to an executor or borrow from a pool that another hook shuts down, and does not wait on another thread's completion; and application code running in a managed container registers the cleanup as a container lifecycle callback instead of a hook.

## Rationale
All registered hooks start concurrently and in no defined order when the virtual machine begins to shut down. A hook that logs may find the logging framework already stopped by its own hook and lose the message, or block on a stopped appender; a hook that submits to an executor may hit `RejectedExecutionException` from a pool another hook shut down; two hooks waiting on each other deadlock the exit. The platform's guidance is direct: hooks "should be coded defensively. They should, in particular, be written to be thread-safe and to avoid deadlocks insofar as possible. They should also not rely blindly upon services that may have registered their own shutdown hooks and therefore may themselves be in the process of shutting down"; and they "should also finish their work quickly", since the operating system "may only allow a limited amount of time in which to shut down". A container's destroy callbacks run in a defined order before the context closes, which a hook cannot rely on.

## Example
```java
bad:  Runtime.getRuntime().addShutdownHook(new Thread(() -> { log.info("stopping"); pool.close(); executor.submit(this::flush).get(); }));
good: @PreDestroy void stop() { flush(); pool.close(); }           // container-ordered, before the context closes
      // or a hook that only flushes its own buffer to a file it opened itself, without logging or executors
```

## Limits
A hook in a plain `main`-based program with no container is the only available cleanup point; it is correct when it touches only resources it owns and does not log through a framework with its own hook. A hook that sets a flag and returns is fine. A project context naming a logging framework configured without a shutdown hook rejects the logging half.

## Validator
On the triggered hunk find each `addShutdownHook` and read the hook body: logging calls, executor submissions, pool borrows, waits on other threads, long work. Check whether the class is a container-managed bean where a destroy callback would serve. Validator question: **does this hook depend on a service that may be shutting itself down at the same time, wait on another thread, or do work a destroy callback should own?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: REL-56`, severity minor, `file`, `symbol`, `code` = the hook registration and body quoted verbatim from the diff, `fix` = a container destroy callback, or a hook limited to resources it owns, `rationale` naming the concurrent hook it depends on).

## Source
`java.lang.Runtime#addShutdownHook(Thread)` Javadoc, Java SE 21 — "Shutdown hooks run at a delicate time in the life cycle of a virtual machine and should therefore be coded defensively. They should, in particular, be written to be thread-safe and to avoid deadlocks insofar as possible. They should also not rely blindly upon services that may have registered their own shutdown hooks and therefore may themselves be in the process of shutting down. Attempts to use other thread-based services such as the AWT event-dispatch thread, for example, may lead to deadlocks"; "Shutdown hooks should also finish their work quickly ... It is therefore inadvisable to attempt any user interaction or to perform a long-running computation in a shutdown hook". Spring Framework reference, "Customizing the Nature of a Bean" — "Destruction Callbacks": `DisposableBean`, `@PreDestroy` or `destroyMethod` lets "a bean get a callback when the container that contains it is destroyed"; `Lifecycle` beans "receive an early stop signal before the destroy methods of any singleton beans are called"; "Shutting Down the Spring IoC Container Gracefully in Non-Web Applications" — "This section applies only to non-web applications": there, `registerShutdownHook()` makes the container "call the relevant destroy methods on your singleton beans" (the container-callback clause).

---
title: A bean that opens a closeable resource or registers a listener in a field declares a destroy callback that closes or deregisters it
rule_id: REL-28
domain: reliability
triggers: ['@PostConstruct', '@Component', '@Service', '@Bean', 'addListener\(', 'addShutdownHook\(', 'subscribe\(', 'new .*Client\(', 'newBuilder\(\)[.]build\(\)', 'forAddress\(|forTarget\(', '@PreDestroy', 'DisposableBean']
scope: file
check_kind: semantic
severity_default: major
---

# A bean that opens a closeable resource or registers a listener in a field declares a destroy callback that closes or deregisters it

## Thesis
A container-managed bean that keeps in a field a resource it opened itself — an HTTP or gRPC client with its own connection pool, a file channel, a socket, a message consumer, a scheduled timer, a registration on a long-lived subject — declares `@PreDestroy` (or implements `DisposableBean`, or names a `destroyMethod`) that closes or deregisters it, so the resource is released when the context shuts down or the bean is discarded.

## Rationale
The container calls a bean's destroy callback when the context closes; without one, the resource outlives its owner. In a process that is exiting this leaks nothing visible, but a context that is refreshed, a test suite that starts many contexts, a devtools restart, or a bean created and discarded per tenant then accumulates open sockets, threads and file descriptors until the limit is hit, and a listener that was never deregistered keeps the whole bean graph reachable and receives events for a bean that no longer exists. `@PreDestroy` is the callback "typically used to release resources that it has been holding"; Spring also infers a destroy method from a public `close` or `shutdown` on `@Bean`-created objects, so a bean that implements `AutoCloseable` and is created by a `@Bean` method is closed automatically.

## Example
```java
bad:  @Service class Feed { private final KafkaConsumer<K, V> consumer = new KafkaConsumer<>(props); ... }
good: @Service class Feed {
          private final KafkaConsumer<K, V> consumer = new KafkaConsumer<>(props);
          @PreDestroy void close() { consumer.wakeup(); consumer.close(); }
      }
```

## Limits
A resource injected from another bean is closed by that bean's callback, not this one. An `ExecutorService` or thread pool has its own lifecycle rules and is out of scope here. A `@Bean` method returning an `AutoCloseable`, or a bean whose `close`/`shutdown` method Spring infers, is already covered. A project context stating that beans are created once per process and the process never refreshes its context lowers the severity to minor.

## Validator
On the triggered hunk find each field initialized or assigned with an object that owns a socket, file, thread, subscription or listener registration, in a class the container manages. Open the file and check for `@PreDestroy`, `DisposableBean.destroy`, a `destroyMethod` on the `@Bean` definition, or an `AutoCloseable` implementation Spring infers. Validator question: **does this bean hold a resource it opened, with no callback that releases it when the bean is destroyed?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: REL-28`, severity major, `file`, `symbol`, `code` = the field initialization quoted verbatim from the diff, `fix` = a `@PreDestroy` method that closes or deregisters the resource, `rationale` naming the socket, thread or listener that outlives the bean).

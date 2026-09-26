---
title: On shutdown, message consumers, listeners and schedulers stop and finish in-flight work before the connection pools and clients they use close
rule_id: REL-55
domain: reliability
triggers: ['@PreDestroy', 'SmartLifecycle', 'getPhase\(\)', 'DisposableBean', 'destroyMethod', '@KafkaListener', '@JmsListener', '@Scheduled', '@RabbitListener', 'addShutdownHook\(', 'DEFAULT_PHASE', '@PostConstruct', 'new Thread\(']
scope: file
check_kind: semantic
severity_default: major
---

# On shutdown, message consumers, listeners and schedulers stop and finish in-flight work before the connection pools and clients they use close

## Thesis
A component that pulls work — a message listener container, a scheduler, a polling loop — is stopped through a lifecycle stop (`SmartLifecycle.stop`, the container's own `stop`) or a dependency-ordered destroy callback that runs before the destroy callbacks of the data source, HTTP client or producer it writes to; a polling thread started in `@PostConstruct` with no lifecycle stop, or a shutdown hook that closes a shared pool while a consumer can still be handling a message, is not that order.

## Rationale
The container destroys singletons in reverse dependency order and stops `Lifecycle` beans first: `Lifecycle` beans "receive an early stop signal before the destroy methods of any singleton beans are called", `SmartLifecycle` adds "a time-bound stop step where the container will wait for all such stop processing to complete before moving on to destroy methods", and when stopping "the reverse order is followed" by phase — highest phase stops first. Graceful shutdown of the web server "is performed in the earliest phase of stopping SmartLifecycle beans". A thread the code starts itself is outside that sequence until its bean implements `Lifecycle`: no stop signal reaches it, so it runs on through the destroy phase and finds its pool closed. A consumer whose pool closes under it fails the message mid-handling: the record is neither acknowledged nor rejected cleanly, the write it was making is half done, and the failure looks like a database outage in the logs. A `@PreDestroy` on a bean the consumer does not depend on through injection has no ordering guarantee against the consumer; a `Runtime` shutdown hook runs concurrently with the context's own close.

## Example
```java
bad:  @PostConstruct void start() { new Thread(() -> { while (true) poll(dataSource); }).start(); }   // nothing stops it; the pool closes under it
good: class Poller implements SmartLifecycle { volatile boolean running; Thread t;
          public void start() { running = true; t = new Thread(() -> { while (running) poll(dataSource); }); t.start(); }
          public void stop() { running = false; try { t.join(); } catch (InterruptedException e) { Thread.currentThread().interrupt(); } }
          public boolean isRunning() { return running; } }   // stop() runs in the lifecycle stop step, before any destroy method
```

## Limits
A consumer that is injected with the pool it uses, and a pool created by a `@Bean` method with inferred `close`, are destroyed in dependency order by the container without extra code; open the wiring before flagging. Spring's own listener containers implement `SmartLifecycle` and stop before any destroy method runs, so a destroy callback that closes a pool used only by container-managed listeners is correctly ordered and is not flagged. A project context that names the shutdown sequence as configured elsewhere (a mesh preStop, a framework-managed order) rejects the finding.

## Validator
On the triggered hunk find each destroy callback, lifecycle bean or shutdown hook that closes a pool, client or producer, and each consumer, listener, scheduler or self-started thread that uses one. Open the file and the wiring: is the consumer stopped by a `Lifecycle` stop or a container-managed dependency before the resource's destroy, or can the resource close while the consumer is mid-message? Validator question: **can a consumer, listener or scheduled task still be running when the pool or client it needs is closed?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: REL-55`, severity major, `file`, `symbol`, `code` = the destroy callback, hook or unstopped start quoted verbatim from the diff, `fix` = a `SmartLifecycle` whose `stop()` ends the consumer (highest phase stops first) before the destroy phase closes the pool, or a `depends-on` from consumer to pool, `rationale` naming the message that fails mid-handling).

## Source
Spring Framework reference, "Customizing the Nature of a Bean" — "For extended shutdown phases, you may implement the Lifecycle interface and receive an early stop signal before the destroy methods of any singleton beans are called. You may also implement SmartLifecycle for a time-bound stop step where the container will wait for all such stop processing to complete before moving on to destroy methods"; "If a 'depends-on' relationship exists between any two objects, the dependent side starts after its dependency, and it stops before its dependency"; "When starting, the objects with the lowest phase start first. When stopping, the reverse order is followed". Spring Boot reference, "Graceful Shutdown" — graceful shutdown "occurs as part of closing the application context and is performed in the earliest phase of stopping SmartLifecycle beans". Spring Kafka `org.springframework.kafka.config.KafkaListenerEndpointRegistry` (`spring-kafka`) — `implements ListenerContainerRegistry, DisposableBean, SmartLifecycle`, `DEFAULT_PHASE = Integer.MAX_VALUE - 100` (the container clause in the Limits).

---
title: No class overrides finalize; native or external cleanup is released eagerly through AutoCloseable and registered with a Cleaner as the safety net
rule_id: JAVA-126
domain: performance
step: [design, handle-errors]
applies_to: [java, garbage-collected]
triggers: ['void finalize\(', 'finalize\(\)', 'super[.]finalize', 'Cleaner', 'PhantomReference']
scope: hunk
check_kind: mechanical
severity_default: minor
---

# No class overrides finalize; native or external cleanup is released eagerly through AutoCloseable and registered with a Cleaner as the safety net

## Thesis
A class that owns a native handle, an off-heap block or another resource the garbage collector does not know about implements `AutoCloseable` with an explicit `close()` and, as a safety net, registers a cleaning action with `java.lang.ref.Cleaner` in a static nested class that holds no reference to the owner; it does not override `Object.finalize()`.

## Rationale
Finalization is deprecated for removal: its use can lead to problems with security, performance and reliability. An object whose class overrides `finalize` is not reclaimed when it first becomes unreachable: the finalizer runs on a thread the language does not specify, and only after it has run and the collector has again determined that the object is unreachable can the memory be freed — so the object and everything it references survive at least one extra collection cycle. A `Cleaner` runs its action at most once after the object has become phantom reachable, on the cleaner's own thread, and the most efficient use is to invoke the `Cleanable` explicitly from `close()`, so the resource is released at the end of the try-with-resources block and the collector never has to do it.

## Example
```java
bad:  @Override protected void finalize() { freeNative(ptr); }
good: private static final Cleaner CLEANER = Cleaner.create();
      private final Cleaner.Cleanable cleanable;
      Handle(long ptr) { this.cleanable = CLEANER.register(this, new Free(ptr)); }
      @Override public void close() { cleanable.clean(); }
      record Free(long ptr) implements Runnable { public void run() { freeNative(ptr); } }
```

## Limits
An empty `finalize` override (an older idiom to block subclass finalizers) is harmless and may be deleted rather than flagged. Code on a JDK without `Cleaner` (before 9) is out of scope. Whether `close()` is called on every path is a resource-lifetime concern outside this rule.

## Validator
On the triggered hunk find each `finalize()` override and each `Cleaner.register` whose action references the registered object (an inner class, a lambda capturing `this`). Validator question: **does this class rely on finalize, or on a cleaning action that keeps its owner reachable, to release a resource?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: JAVA-126`, severity minor, `file`, `symbol`, `code` = the `finalize` override or the self-referencing cleaning action quoted verbatim from the diff, `fix` = the `Cleaner` registration with a static nested action and an explicit `close()`, `rationale` naming the extra collection cycle and the unspecified finalizer thread).

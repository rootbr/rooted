---
title: The body of a hot loop allocates no per-iteration helper object; a value-capturing lambda, an Optional wrapper or a temporary collection is hoisted or replaced
rule_id: PF-26
domain: performance
triggers: ['->', 'Optional[.](of|ofNullable|empty)\(', 'computeIfAbsent\(', 'forEach\(', 'new (ArrayList|HashMap|HashSet|StringBuilder)<?>?\(\)']
scope: hunk
check_kind: semantic
severity_default: minor
---

# The body of a hot loop allocates no per-iteration helper object; a value-capturing lambda, an Optional wrapper or a temporary collection is hoisted or replaced

## Thesis
Inside a loop that runs per element of a large input or per message, the body creates no object whose only purpose is to carry a value through the iteration: a lambda that captures a local of the enclosing frame (allocated afresh on each evaluation), an `Optional` wrapped around a value that is unwrapped at once, a `StringBuilder` or collection created and discarded per iteration, or an iterator from a for-each over a custom `Iterable`. The lambda is made non-capturing (its instance is then a constant) or hoisted before the loop; the `Optional` is replaced by a null check or a sentinel; the collection is allocated once outside the loop and cleared.

## Rationale
The linkage of a lambda expression depends on what it captures: a non-capturing lambda is linked to a single pre-computed instance, so evaluating it allocates nothing, while a capturing lambda is linked to its class's constructor, so every evaluation allocates a new object holding the captured values. `Optional.of` allocates a wrapper per call and `Optional.empty()` is not guaranteed to be a singleton; a `StringBuilder` starts with a fresh buffer; a for-each over an `Iterable` calls `iterator()` per loop entry. Each is small, but per iteration over a large input they set the allocation rate that drives young-generation collections, and the just-in-time compiler removes such an allocation only when the object provably does not escape after inlining — which a lambda passed to a library method, or a collection stored anywhere, defeats.

## Example
```java
bad:  for (Item it : items) {                         // millions of items
          cache.computeIfAbsent(it.key(), k -> new Entry(k, ctx));   // captures ctx
          Optional.ofNullable(it.tag()).ifPresent(sink::add);
      }
good: Function<Key, Entry> mk = k -> new Entry(k, ctx);            // one instance
      for (Item it : items) {
          cache.computeIfAbsent(it.key(), mk);
          if (it.tag() != null) sink.add(it.tag());
      }
```

## Limits
Applies to loops on a hot path over large inputs. A lambda that must capture the loop variable itself (a task submitted per element) is a necessary allocation; the finding is downgraded to a note when the object's lifetime genuinely spans the iteration. `Optional` as a method return type is its intended use and is not flagged at the call site; the loop that wraps and unwraps its own value is. Escape analysis may remove an allocation when the whole chain inlines; a tolerance in the project context — "this pipeline is not allocation-sensitive" — rejects the finding.

## Validator
On the triggered hunk find each loop body (or per-element callback) that evaluates a lambda capturing a local or a field of the enclosing frame, calls `Optional.of`, `ofNullable` or `empty` on its own value, or constructs a collection or `StringBuilder` it discards at the end of the iteration. Confirm the loop runs over a large input or per message. Validator question: **does this hot loop allocate a helper object on every iteration that a hoisted constant, a null check or a reused instance would replace?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PF-26`, severity minor, `file`, `symbol`, `code` = the allocating expression inside the loop quoted verbatim from the diff, `fix` = the hoisted lambda, the null check or the reused instance, `rationale` naming the per-iteration allocation).

## Source
`java.lang.invoke.InnerClassLambdaMetafactory#buildCallSite`, Java SE 21 source — "In the case of a non-capturing lambda, we optimize linkage by pre-computing a single instance" behind a `ConstantCallSite`, while a capturing lambda's call site is bound to the lambda class's constructor (an implementation detail of the reference implementation). `java.util.Optional#empty` Javadoc, Java SE 21 — "There is no guarantee that it is a singleton"; class API note — `Optional` "is primarily intended for use as a method return type". JLS §15.27.4 — evaluation of a lambda either allocates a new instance or references an existing one — not fetched from the authoring environment. JMH benchmark `ionutbalosin/jvm-performance-benchmarks`, `.../compiler/ScalarReplacementBenchmark.java` — the escape states `NoEscape`, `ArgEscape` and `GlobalEscape`, and which allocations the compiler removes.

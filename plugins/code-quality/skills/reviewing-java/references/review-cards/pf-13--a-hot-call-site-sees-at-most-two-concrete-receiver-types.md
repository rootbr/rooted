---
title: A virtual or interface call on a hot path sees at most two concrete receiver types, so the just-in-time compiler can inline it
rule_id: PF-13
domain: performance
triggers: ['implements \w+', 'interface \w+', 'new \w+\(\)\s*\{', 'for \([^)]*\) .*[.]\w+\(']
scope: callers
check_kind: semantic
severity_default: minor
---

# A virtual or interface call on a hot path sees at most two concrete receiver types, so the just-in-time compiler can inline it

## Thesis
A call whose receiver is an interface or abstract type and that runs per element of a hot loop or per request is reached by at most two concrete implementations at that site. When a third implementation is added, the hot site is split — one loop or branch per concrete type, a pattern `switch` in front of the call — or the design keeps the polymorphic dispatch outside the loop.

## Rationale
The just-in-time compiler profiles each call site and records up to two receiver types (`TypeProfileWidth`, default 2); with one or two recorded types it inlines the callee behind a type check — monomorphic and bimorphic inlining — which then lets it eliminate allocations, hoist loop invariants and vectorize across the call. Once a third type shows up the profile is megamorphic: the site falls back to a virtual-table or interface-table dispatch, nothing behind it is inlined, and every optimization that needed to see through the call is lost — unless one receiver accounts for at least 90 % of the profiled calls (`TypeProfileMajorReceiverPercent`, default 90), in which case that receiver is still inlined behind a type guard and only the remainder goes through the table. A benchmark that dispatches one interface call over one to six receiver types, against the same call devirtualized by splitting the loop per type, is the reference measurement. The cost is invisible in a unit test that exercises one implementation at a time.

## Example
```java
bad:  for (Shape s : shapes) area += s.area();   // Circle, Square, Triangle, … at one site
good: for (Circle c : circles) area += c.area();
      for (Square q : squares) area += q.area();
      // or: switch (s) { case Circle c -> …; case Square q -> …; default -> s.area(); }
```

## Limits
Applies to a site on a hot path: a loop over many elements, a per-request handler, a per-message codec. A site called rarely, a site with two implementations, and a site behind a plugin architecture where the polymorphism is the point (with the cost accepted in the project context) are out of scope. A hot site at which one receiver accounts for at least 90 % of the profiled calls keeps that receiver inlined behind a guard and is not flagged. A lambda is its own class, so a `Function` or `Consumer` call site fed with three or more distinct lambdas is the same defect. The profile is per call site, so splitting the loop restores inlining although the interface keeps all its implementations.

## Validator
On the triggered hunk find (a) an interface or abstract call inside a loop or on a per-request path and (b) a new `implements`, `extends` or anonymous class that adds an implementation to an existing type. For (a) grep the repository for the implementations of the receiver type; for (b) grep for hot call sites of the type's methods. Count the concrete receiver types that reach the site. Validator question: **can this hot call site see three or more concrete receiver types at run time?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PF-13`, severity minor, `file`, `symbol`, `code` = the call site, and the new implementation when the diff adds one, quoted verbatim from the diff, `fix` = the split loop or the pattern `switch`, `rationale` naming the third receiver type and the inlining it loses).

## Source
HotSpot `src/hotspot/share/runtime/globals.hpp` (jdk-21-ga) — `TypeProfileWidth`, default 2, "Number of receiver types to record in call/cast profile"; `src/hotspot/share/opto/c2_globals.hpp` — `UseBimorphicInlining`, "Profiling based inlining for two receivers"; `TypeProfileMajorReceiverPercent`, default 90, "% of major receiver type to all profiled receivers". JMH benchmarks `ionutbalosin/jvm-performance-benchmarks`, `.../compiler/MegamorphicInterfaceCallBenchmark.java` and `MegamorphicMethodCallBenchmark.java` — monomorphic, bimorphic and megamorphic (three to eight receiver types) dispatch beside the same call site split per type, and `MEGAMORPHIC_6_DOMINANT_TARGET` (one target at about 90 % of the calls, six types over the remaining 10 %). Hölzle, Chambers, Ungar, "Optimizing dynamically-typed object-oriented languages with polymorphic inline caches", ECOOP 1991, DOI 10.1007/BFb0057013 — the inline-cache design and its megamorphic fallback — not fetched from the authoring environment.

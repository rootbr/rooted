---
title: A CompletableFuture chain ends in exceptionally, handle, whenComplete or a join, so an exceptional completion is not dropped at the last stage
rule_id: REL-59
domain: reliability
triggers: ['thenApply\(', 'thenAccept\(', 'thenRun\(', 'thenCompose\(', 'thenCombine\(', 'CompletableFuture', 'exceptionally\(', 'whenComplete\(', '[.]handle\(']
scope: file
check_kind: semantic
severity_default: major
---

# A CompletableFuture chain ends in exceptionally, handle, whenComplete or a join, so an exceptional completion is not dropped at the last stage

## Thesis
Every chain of `then*` stages either terminates in `exceptionally`, `handle` or `whenComplete` that records or recovers the failure, or is returned to a caller who joins it (`join`, `get`) or attaches the handler; a chain whose last stage is `thenAccept`/`thenRun` with nothing after it has no observer of exceptional completion.

## Rationale
When a stage's computation "terminates abruptly with an (unchecked) exception or error, then all dependent stages requiring its completion complete exceptionally as well, with a CompletionException holding the exception as its cause"; the dependent `then*` actions are skipped, not run with a null. Only `handle` and `whenComplete` "support unconditional computation whether the triggering stage completed normally or exceptionally", and `exceptionally` runs "only when the triggering stage completes exceptionally". A chain that ends in `thenAccept(this::store)` therefore stores nothing on failure and reports nothing: the exception sits in the last future, referenced by no one, and the work silently did not happen. An `exceptionally` that returns a default also swallows by design unless it records the failure.

## Example
```java
bad:  client.fetch(id).thenApply(this::parse).thenAccept(repo::store);
good: client.fetch(id).thenApply(this::parse).thenAccept(repo::store)
          .whenComplete((v, e) -> { if (e != null) log.error("fetch {} failed", id, e); });
```

## Limits
A chain returned as a `CompletableFuture` to a caller is observed by that caller; check the caller in the file before flagging, and flag only when the file shows a caller that drops it; a chain returned from a non-private method is assumed observed unless the file shows a caller that drops it. A chain whose every stage catches internally has no exceptional completion to observe. `allOf(...).join()` observes the joined futures. A tolerance stated in the project context — fire-and-forget metrics whose loss is accepted — rejects the finding for that chain.

## Validator
On the triggered hunk find each `then*` chain and follow it to its end in the file: a terminal `exceptionally`/`handle`/`whenComplete` that records or recovers, a `join`/`get`, or a return to a caller that does one of those. Validator question: **can a stage of this chain fail with no stage or caller that ever sees the exceptional completion?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: REL-59`, severity major, `file`, `symbol`, `code` = the chain quoted verbatim from the diff, `fix` = a terminal `whenComplete`/`handle`/`exceptionally` that records the failure, or the future returned to a caller that joins it, `rationale` naming the skipped stages and the unobserved exception).

## Source
`java.util.concurrent.CompletionStage` class Javadoc, Java SE 21 — "Two method forms (handle and whenComplete) support unconditional computation whether the triggering stage completed normally or exceptionally. Method exceptionally supports computation only when the triggering stage completes exceptionally"; "if a stage's computation terminates abruptly with an (unchecked) exception or error, then all dependent stages requiring its completion complete exceptionally as well, with a CompletionException holding the exception as its cause". `java.util.concurrent.CompletableFuture` class Javadoc — `isCompletedExceptionally`, `join` throwing the `CompletionException`.

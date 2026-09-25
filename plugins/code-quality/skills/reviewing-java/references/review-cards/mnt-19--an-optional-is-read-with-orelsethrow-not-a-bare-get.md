---
title: An Optional's value is read with orElseThrow, orElse, orElseGet, map or ifPresent, not with a bare get()
rule_id: MNT-19
domain: maintainability
triggers: ['[.]get\(\)\s*[;.)]', 'isPresent\(\)', 'orElseThrow\(', 'Optional<']
scope: file
check_kind: mechanical
severity_default: minor
---

# An Optional's value is read with orElseThrow, orElse, orElseGet, map or ifPresent, not with a bare get()

## Thesis
Code that needs the value inside an `Optional` states what happens when it is empty: `orElseThrow(() -> new NotFoundException(id))` for a failure with a typed exception, `orElse`/`orElseGet` for a default, `map`/`flatMap`/`ifPresent` to continue in the pipeline; a bare `get()` — which throws `NoSuchElementException` when empty and reads as a plain accessor — is not used unguarded.

## Rationale
`get()` looks like the accessor of a value that is there, so the reader and the author both skip the empty case; when it happens, the exception is a `NoSuchElementException` with no message naming what was missing. The typed `orElseThrow(Supplier)` makes the failure explicit and meaningful at the call site, and the JDK's own API note names `orElseThrow()` as the preferred alternative to `get()`.

## Example
```java
bad:  User u = repo.findById(id).get();        // NoSuchElementException with no message when absent
      String name = opt.get().name();
good: User u = repo.findById(id).orElseThrow(() -> new UserNotFoundException(id));
      String name = opt.map(User::name).orElse("anonymous");
```

## Limits
`get()` on a `Future`, `AtomicReference`, `Supplier`, `ThreadLocal` or a map is a different method. An `isPresent()` (or `!isEmpty()`) guard followed by `get()` on the same `Optional` is the compliant form and is not flagged; whether it reads better as `map` or `ifPresent` is a style question this card does not carry. Test code asserting `opt.get()` after `assertTrue(opt.isPresent())` is a lower-value finding.

## Validator
On the triggered hunk find each `.get()` whose receiver is an `Optional` (open the file to resolve the type) and skip a `get()` that sits inside an `isPresent()` or `!isEmpty()` guard on the same receiver. Validator question: **is an `Optional` unwrapped with an unguarded `get()` where an `orElseThrow`, `orElse`, `orElseGet`, `map` or `ifPresent` would name the empty case?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: MNT-19`, severity minor, `file`, `symbol`, `code` = the `get()` call quoted verbatim from the diff, `fix` = the replacement call, `rationale` naming the unnamed `NoSuchElementException`).

## Source
`java.util.Optional#get()` Javadoc, Java SE 21 — "If a value is present, returns the value, otherwise throws NoSuchElementException"; API note — "The preferred alternative to this method is orElseThrow()". SonarSource `java:S3655` "Optional value should only be accessed after calling isPresent()" — `get()` "will throw a NoSuchElementException if there is no value present … other methods such as orElse(...), orElseGet(...) or orElseThrow(...) can be used to specify what to do with an empty Optional"; its compliant solution is `get()` inside an `isPresent()` guard (rule text from the `sonar-java` 6.15.1 plugin resources).

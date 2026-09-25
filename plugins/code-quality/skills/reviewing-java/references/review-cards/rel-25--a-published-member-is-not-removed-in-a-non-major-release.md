---
title: A public or protected member of a published type is not removed, renamed or retyped in a non-major release; it is deprecated and kept
rule_id: REL-25
domain: reliability
triggers: ['public (abstract |static |final |sealed )*(class|interface|record|enum) ', 'public [\w<>\[\], ?]+ \w+\(', 'protected [\w<>\[\], ?]+ \w+\(', '@JsonProperty', '@Deprecated', 'module-info']
scope: base-compare
check_kind: semantic
severity_default: major
---

# A public or protected member of a published type is not removed, renamed or retyped in a non-major release; it is deprecated and kept

## Thesis
In a module whose types other code depends on — a library, an SDK, a shared API module, a wire DTO the project context declares published — a `public` or `protected` class, method, field or constructor present in the base version is still present in the head version with the same name, parameter types, return type and access; a change that removes it, narrows its access, alters its signature, or adds an abstract method to a public interface is made in a major release, after the old member has carried `@Deprecated` for at least one release.

## Rationale
Compiled callers link to a member by name and descriptor: removing or renaming it, changing a parameter or return type, or narrowing its access makes existing binaries fail at link time with `NoSuchMethodError`, `NoSuchFieldError` or `IllegalAccessError`, and existing sources fail to compile; adding an abstract method to a public interface keeps old implementor binaries linking but makes their sources fail to compile and throws `AbstractMethodError` the first time the new method is invoked on one of them. A consumer discovers the break when it upgrades, not when the change is made. Versioning schemes reserve such changes for a major version — "Major version X MUST be incremented if any backward incompatible changes are introduced to the public API" — and a deprecation period gives consumers a release in which both forms exist and the compiler warns them. A JSON field renamed or removed on a published DTO breaks clients the same way at the wire, without a compiler to warn anyone.

## Example
```java
bad:  public Optional<Order> find(long id) { ... }          // return type changed in place; the Order-returning find is gone
good: /** @deprecated use {@link #lookup(long)}; removed in 3.0 */
      @Deprecated(since = "2.4", forRemoval = true)
      public Order find(long id) { return lookup(id).orElse(null); }
      public Optional<Order> lookup(long id) { ... }
```

## Limits
Applies to published types: those in a module the project context names as consumed by other codebases, exported by a module descriptor, or annotated as public API. A type in an application's own internals, a package-private or private member, a `@Deprecated(forRemoval = true)` member whose removal the release notes announce in a major version, and a change in a project that states "no external consumers" are out of scope. Adding a method to a class, adding a `default` method to an interface, or widening access is compatible and is not flagged. The card dispatches on the renamed or retyped replacement; a pure removal adds no line and is a known gap of added-line dispatch.

## Validator
On the triggered hunk find each added or changed declaration of a public or protected member, a public interface's abstract method, or a published DTO field. Compare the base and head versions of the file: list the public and protected members of the base that are gone, renamed, retyped or narrowed in the head, and check whether the base version already carried `@Deprecated` and whether the project context names this release as major. Validator question: **does this change break a compiled or wire consumer of a published type without a deprecation period or a major version?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: REL-25`, severity major, `file`, `symbol`, `code` = the removed or changed declaration quoted verbatim from the diff, `fix` = the old member kept and annotated `@Deprecated(since, forRemoval)` delegating to the new one, `rationale` naming the link-time or wire failure consumers will hit).

## Source
Semantic Versioning 2.0.0 (`semver/semver`, `semver.md`) §8 — "Major version X (X.y.z | X > 0) MUST be incremented if any backward incompatible changes are introduced to the public API"; §7 — the minor version "MUST be incremented if any public API functionality is marked as deprecated"; FAQ "How should I handle deprecating functionality?" — "Before you completely remove the functionality in a new major release there should be at least one minor release that contains the deprecation so that users can smoothly transition to the new API". JLS §13 "Binary Compatibility" — deleting a member, changing its declared type or its access breaks pre-existing binaries; §13.5.6 "Interface Method Declarations" — adding an abstract method to an interface does not break compatibility with pre-existing binaries; the break is at the source level, and a pre-existing implementor binary throws `AbstractMethodError` when the new method is invoked on it (unfetched; cited as its provenance line anchors it). `java.lang.Deprecated` Javadoc, Java SE 21 — `forRemoval = true` "indicates intent to remove the annotated program element in a future version".

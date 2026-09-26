---
title: A constructor or public method that stores or dereferences a reference parameter validates it at entry
rule_id: MNT-21
domain: maintainability
triggers: ['this[.]\w+ = \w+;', 'requireNonNull\(', 'public \w+\([^)]*\w+ \w+[^)]*\)\s*\{']
scope: hunk
check_kind: mechanical
severity_default: suggestion
---

# A constructor or public method that stores or dereferences a reference parameter validates it at entry

## Thesis
A constructor that stores a reference parameter into a field, and a public method that will dereference a reference parameter, validates that parameter at entry, `Objects.requireNonNull(param, "param")` being the designed form, so that a `null` fails at the call that supplied it, with a message naming the parameter, rather than later at first use.

## Rationale
A `null` stored into a field surfaces as a `NullPointerException` in a method that runs later, on another thread or after other state has changed, with a stack trace that points at the use and not at the caller who passed it; the check at entry moves the failure to the constructor or method call where the wrong argument is on the stack. `requireNonNull` is designed for parameter validation in methods and constructors, returns its argument so the check folds into the assignment, and throws with the given message.

## Example
```java
bad:  OrderService(OrderRepository repo, Clock clock) { this.repo = repo; this.clock = clock; }
good: OrderService(OrderRepository repo, Clock clock) {
          this.repo = Objects.requireNonNull(repo, "repo");
          this.clock = Objects.requireNonNull(clock, "clock"); }
```

## Limits
A parameter declared `@Nullable`, a primitive, or one whose `null` is handled with a default is not checked. A project with JSpecify `@NullMarked` packages and a checker that fails the build on a `null` argument has the guarantee at compile time; the project context may declare the check redundant there. A private method, and a Spring-injected constructor whose arguments the container guarantees, are lower-value sites; a record puts the check in its compact constructor.

## Validator
On the triggered hunk find each constructor assignment `this.f = p` and each public method that dereferences a reference parameter, and look for a `requireNonNull` (or an equivalent guard, or an annotation-driven check) on that parameter. Validator question: **can a `null` argument reach a field or a dereference here without being rejected at entry?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: MNT-21`, severity suggestion, `file`, `symbol`, `code` = the assignment or dereference quoted verbatim from the diff, `fix` = the `requireNonNull` with a message, `rationale` naming the later, misleading NPE).

## Source
`java.util.Objects#requireNonNull(T, String)` Javadoc, Java SE 21 — "Checks that the specified object reference is not null and throws a customized NullPointerException if it is. This method is designed primarily for doing parameter validation in methods and constructors with multiple parameters"; returns `obj` if not `null`; `#requireNonNull(T)` — "designed primarily for doing parameter validation in methods and constructors". SEI CERT Oracle Coding Standard for Java, `MET00-J` "Validate method arguments" — the obligation to validate a method's arguments at entry.

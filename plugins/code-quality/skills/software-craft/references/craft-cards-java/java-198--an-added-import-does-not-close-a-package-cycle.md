---
title: An added import does not close a dependency cycle between two packages
rule_id: JAVA-198
domain: design
step: [design, implement]
applies_to: [java]
triggers: ['^import (?!static |java[.]|javax[.]|jakarta[.]|org[.]springframework|org[.]slf4j|org[.]junit|org[.]assertj|org[.]mockito|com[.]fasterxml|lombok[.]|org[.]apache|com[.]google|io[.]micrometer|reactor[.])[\w.]+;', '^import static (?!java[.]|org[.]junit|org[.]assertj|org[.]mockito)[\w.]+;']
scope: callers
check_kind: semantic
severity_default: minor
---

# An added import does not close a dependency cycle between two packages

## Thesis
When the diff adds an import of a class in another package of the same codebase, no class in that target package — or in a package it depends on — imports back into the importing package; a dependency that would close such a cycle is redirected: the shared type moves to a package both depend on, or the call is inverted through an interface owned by the callee's package.

## Rationale
Two packages that depend on each other can be understood, tested, versioned and released only together: a change in either may ripple into the other and back, and neither can be extracted into its own module. Empirical work finds most defects and defective components concentrated in components that take part in dependency cycles, directly or indirectly, and systems with more cycles score lower on maintainability. A cycle is cheapest to refuse at the import that would close it.

## Example
```java
bad:  package app.billing;
      import app.orders.OrderService;   // orders already imports app.billing.Invoice
good: package app.billing;
      import app.shared.OrderRef;        // shared type in a package both depend on
      // or: orders declares interface InvoiceIssuer; billing implements it; orders never imports billing
```

## Limits
Imports of the JDK, of third-party libraries and of the same package are out of scope. A cycle that already exists at the base commit and that the diff does not extend is reported once as pre-existing, if at all. Sub-packages of one feature (`orders` and `orders.internal`) that a project treats as one slice are a tolerance the project context may declare; ArchUnit slice rules in the repository define the unit where present.

## Validator
On the triggered hunk take each added import whose package belongs to this codebase and differs from the importing file's package. At callers scope grep the target package's sources for imports of the importing package, and one hop further for packages that import it. Validator question: **does the target package, directly or through one intermediate package, already import the package this file lives in?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: JAVA-198`, severity minor, `file`, `symbol`, `code` = the added import line quoted verbatim from the diff, `fix` = the moved type or the inverted dependency, `rationale` naming the two packages and the reverse import that completes the cycle).

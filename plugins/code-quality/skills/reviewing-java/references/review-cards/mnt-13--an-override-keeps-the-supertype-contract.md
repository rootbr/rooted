---
title: An override keeps the supertype's contract and neither throws UnsupportedOperationException for an inherited operation nor rejects arguments the supertype accepts
rule_id: MNT-13
domain: maintainability
triggers: ['UnsupportedOperationException', '@Override']
scope: file
check_kind: semantic
severity_default: major
---

# An override keeps the supertype's contract and neither throws UnsupportedOperationException for an inherited operation nor rejects arguments the supertype accepts

## Thesis
A method that overrides or implements a supertype method honours what the supertype promises: it does not throw `UnsupportedOperationException` (or silently do nothing) for an operation the supertype declares as always available, and it does not add preconditions — reject an argument range, a `null`, a state — that the supertype's callers are allowed to use; where a subtype cannot support the operation, the hierarchy is wrong, and composition or a narrower interface replaces it.

## Rationale
Code written against the supertype is correct only if every subtype behaves as the supertype's contract says; a subtype that strengthens a precondition or refuses an operation breaks that code at runtime, at a call site that looks correct, with an exception the supertype never documented. Behavioural subtyping — preconditions may not be strengthened, postconditions and invariants may not be weakened — is the condition under which substitution is safe. An interface with methods that some implementors must stub is telling you the interface is too wide for those implementors.

## Example
```java
bad:  class ReadOnlyCart implements Cart {
          @Override public void add(Item i) { throw new UnsupportedOperationException(); }
      }
good: interface Cart extends ReadableCart { void add(Item i); }
      class ReadOnlyCart implements ReadableCart { ... }   // callers needing add() take Cart
```

## Limits
The JDK collection interfaces declare "optional operations" and document `UnsupportedOperationException` for them, so an unmodifiable collection view is within contract. A subtype that narrows a return type or adds a postcondition is fine. A method that throws `UnsupportedOperationException` because the supertype documents that implementations may is not flagged. An abstract-method placeholder in a skeletal base class is out of scope.

## Validator
On the triggered hunk find each override or interface implementation whose body throws `UnsupportedOperationException`, returns without acting, or begins with a check that rejects an argument or state. Open the file; read the supertype's declaration when it is declared in the same file, and otherwise take the operation's documented contract as the finder knows it — a JDK or library interface's Javadoc, a project interface as the review inventory describes it — to see whether the supertype documents the operation as optional or the precondition as required. Validator question: **does this override refuse an operation or an argument that the supertype's contract allows?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: MNT-13`, severity major, `file`, `symbol`, `code` = the override quoted verbatim from the diff, `fix` = the narrower interface or the composition that removes the refused operation, `rationale` naming the supertype call that now fails).

## Source
Liskov, Wing, "A Behavioral Notion of Subtyping", ACM Transactions on Programming Languages and Systems 16(6), 1994, DOI 10.1145/197320.197383 — the subtype requirement: preconditions not strengthened, postconditions and invariants not weakened. `java.lang.UnsupportedOperationException` Javadoc, Java SE 21 — "Thrown to indicate that the requested operation is not supported", a member of the Collections Framework, whose interfaces document their optional operations.

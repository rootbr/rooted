---
title: A collection parameter that a routine only reads from is declared with a read-only or covariant type, so callers can pass a collection of a subtype
rule_id: CODE-49
domain: code
step: [design, implement]
applies_to: [static-types, dynamic-types]
triggers: ['(^|[(,])\s*(@\w+\s+|final\s+)*(List|ArrayList|LinkedList|Collection|Iterable|Set|HashSet|SortedSet|Map|HashMap|SortedMap|Queue|Deque)<\s*[A-Z][\w\s,]*>\s+\w+', '\b\w+\s*:\s*(Optional\[)?(list|List|dict|Dict|set|Set|MutableSequence|MutableMapping|MutableSet)\[']
scope: file
check_kind: semantic
severity_default: minor
---

# A collection parameter that a routine only reads from is declared with a read-only or covariant type, so callers can pass a collection of a subtype

## Thesis
A routine parameter that holds a collection or a map the routine only reads from, iterating, indexing, counting or looking up its elements and never adding, setting, inserting or removing one, is declared with a read-only collection type that is covariant in its element type, or, where the language expresses variance at the use site, with a wildcard bounded above by the element type. Either type accepts a collection of the element type or of any of its subtypes. The rule applies where the type system makes the declared collection type invariant in its element type, so that a collection of a subtype is rejected where a collection of its base type is declared. A parameter the routine writes elements into keeps a type that accepts the write.

## Rationale
A collection type that is invariant in its element type is neither a subtype nor a supertype of the same collection type over a subtype of the element: a list of managers is not a list of employees. A type checker rejects passing the one where the other is declared, because the routine might append an element of the base type to the list, which would violate the element type the caller declared for it; were the call accepted and the routine appended such an element, the caller's read of that element, which it holds as the subtype, would fail at run time. When the routine does not mutate its argument, accepting the collection of the subtype is correct, and that requires the parameter to act covariantly. A read-only collection type declared covariant in its element type, and a wildcard bounded above by the element type, each accept a collection of the element type or of any subtype: the routine can safely read elements of the element type from it but cannot write to it. The signature is then more flexible, because it accepts more types. Declared with the invariant type, the routine rejects every caller that holds a collection of a subtype, and that caller has to work around the rejection, for instance by copying its collection into a new one of the base type or declaring it with the base type from the start, before the call type-checks.

## Example
```java
bad:  double totalArea(List<Shape> shapes) {
          return shapes.stream().mapToDouble(Shape::area).sum();
      }
      double ringArea() { return totalArea(rings); } // rings: List<Circle>, rejected
good: double totalArea(List<? extends Shape> shapes) {
          return shapes.stream().mapToDouble(Shape::area).sum();
      }
      double ringArea() { return totalArea(rings); }
```

## Limits
A parameter the routine writes elements into is outside the rule, because the read-only type and the upper-bounded wildcard both forbid the write. Where the language expresses variance at the use site, a parameter the routine only writes into can take a wildcard bounded below by the element type, which accepts a collection of the element type or of any of its supertypes. A parameter the routine both reads and writes keeps the invariant type, because the lower-bounded wildcard hands its elements back only as the top type.

A read-only map type can be covariant in its value type and stay invariant in its key type. A map whose keys are of a subtype is then rejected by the read-only type as well, and only a wildcard bounded above on the key, where the language expresses variance at the use site, accepts it.

The upper-bounded wildcard forbids adding and setting elements but does not make the collection immutable: clearing it still type-checks. It guarantees type safety, not that the routine leaves the collection unchanged, so whether a routine only reads is decided from its body, not from its signature.

Where the type system accepts a mutable collection of a subtype where one of its base type is declared, taking a correctness trade-off, the call is not rejected and the rule has no rejected caller to restore.

Where the type system has no covariance or contravariance between instantiations of a generic type, there is no covariant collection type to declare and the rule has nothing to apply to. Where its only subtyping is between lifetimes, only an element type that carries a lifetime admits a subtype, and the rule applies to that element type alone.

A project may leave invariant collection types rigidly typed in its parameters and reserve wildcards for types that only produce or only consume values, or may exempt private routines as outside its public interface. A project context that states either tolerance rejects the finding.

## Validator
In the hunk, find each routine parameter declared with a collection or map type instantiated with a named element type rather than a wildcard or a read-only type, such as a list, set, map, queue or iterable of a class. Open the file and read the routine's body. Trace every use of the parameter: adding, setting, inserting, removing or clearing an element is a write, and so is passing the parameter to a callee that declares the invariant collection type for it, or whose declaration the file does not show, unless the diff changes that callee to a read-only or covariant type too. Go on only when every use reads. Skip a parameter whose element type admits no subtype, such as a class declared final, and one whose element type is a type parameter of the routine that appears nowhere else in its signature, neither in another parameter nor in the return type, because no caller's collection is rejected there. For a map, take the value type as the element type, and the key type only where a wildcard bounded above can be declared on the key. Skip a routine whose parameter type is fixed by a declaration it overrides or implements and the diff does not change. Skip where the language already accepts a mutable collection of a subtype for one of its base type, or has no variance between instantiations of a generic type. Skip where the project context states a tolerance that leaves invariant collection types rigidly typed or exempts private routines. Validator question: **Does this routine only read from a collection parameter whose invariant type rejects a collection of a subtype of its element type, where a read-only covariant type or an upper-bounded wildcard would accept it?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: CODE-49`, severity minor, `file`, `symbol`, `code` = the parameter declaration quoted verbatim from the diff, `fix` = the same parameter declared with a read-only collection type covariant in its element type or with a wildcard bounded above by the element type, in the file's language, `rationale` = the caller holding a collection of a subtype that the invariant type rejects, and the reads that are the routine's only use of the parameter).

---
title: A routine with a type parameter runs the same code for every type argument, and behaviour that differs by type is written as separate implementations behind an interface
rule_id: CODE-42
domain: code
step: [design, implement]
applies_to: [static-types, dynamic-types]
triggers: ['(?<![?])[.]\(\s*(type\b|[*\[\w])', '\binstanceof\b', '\b(isinstance|issubclass)\(', '\btypeof\s+[\w.]+\s*[!=]==?|\bswitch\s*\(\s*typeof\b', '\bTypeId::of\b|\bdowncast(_ref|_mut)?\b|[.]is::<', '\bgetClass\(\)|[.]class\s*(==|!=|[.](equals|isAssignableFrom)\()|(==|!=|\bequals\()\s*[\w.]+[.]class\b|\btype\(\w+\)\s*(is|==)|\b(is|==)\s+(int|float|str|bytes|bool|list|dict|tuple)\b|\bcase\s+([A-Z][\w.]*|int|float|str|bytes|bool|list|dict|tuple|set)\s*\(|\bcase\s+[A-Z][\w.]*(<[^>]*>)?\s+[a-z]\w*\s*(->|:|when\b)']
scope: file
check_kind: mechanical
severity_default: minor
---

# A routine with a type parameter runs the same code for every type argument, and behaviour that differs by type is written as separate implementations behind an interface

## Thesis
A routine or type with a type parameter holds code whose implementation is the same for every type it is instantiated with. Where the implementation differs for each type, each type carries its own implementation as a method of an interface or trait, and the shared code calls that method rather than inspecting the run-time type of a value whose type is the parameter, or is built from it, to decide what to do with it. An operation that has to cover even types that lack the method it needs, and that differs for each type, is the case left to run-time reflection.

## Rationale
A type parameter is reasonable for methods that look the same for all the relevant types, as the length and swap operations a sort requires are exactly the same for every slice type; the one per-type step there, the comparison, is a function passed in when the generic adapter is created. Where the implementation is different for each type, as reading from a file is nothing like reading from a random number generator, each type gets its own method and the code that reads uses an interface type. When several types share a useful unifying interface, modelling the solution with that interface may leave no need for a type parameter at all. Inspecting the types of received arguments in order to decide what to do with them is brittle and closed to extension: a developer using an already-written library may be unable to change how such code treats their objects, especially objects created by a third party. In a documented case, a type switch in a routine bounded to the types whose underlying type is a 32- or 64-bit float tests the actual type argument, which is not the same as the underlying type the bound matched, so the routine, whose cases are the two built-in float types, panics when called with a user-defined type whose underlying type is one of them. With one implementation per type behind an interface or trait, each implementing type provides its own body for the method, and the compiler or type checker verifies that every type having the trait implements the method the trait declares.

## Example
```go
bad:  func Area[T any](s T) float64 {
          switch v := any(s).(type) {
          case Circle: return math.Pi * v.R * v.R
          case Square: return v.Side * v.Side
          }
          panic("unsupported shape")
      }
good: type Shape interface{ Area() float64 }
      func (c Circle) Area() float64 { return math.Pi * c.R * c.R }
      func (s Square) Area() float64 { return s.Side * s.Side }
```

## Limits
An operation that has to support even types that lack the method it needs, so that an interface does not help, and that is different for each type, so that a type parameter is not appropriate, is written with run-time reflection, as an encoder to a data-interchange format that does not require an encoding method on every type it encodes is; that code is not simple, but it works, and it passes. A generic algorithm that checks whether its argument also implements a marker interface for fast random access, and alters its behaviour to keep its performance acceptable, passes: the best algorithms for random-access lists can produce quadratic behaviour on sequential-access lists, and one standard collection library defines that marker so that generic list algorithms make this check. Per-type behaviour that the caller passes in as a function, as a comparison passed to a generic tree or sort adapter is, meets the rule. So does a generic function composed of multiple functions that implement the same operation for different types, with the implementation for a call chosen by the type of a single argument. A routine whose shared implementation performs its operation for every type argument, and which tests for certain concrete types only to add special treatment for them, as a logger that prints any value and also prints the length of a string value does, is outside the rule: its branches do not each carry the behaviour for a different type.

## Validator
Grep the added lines for a run-time type test: a type switch or type assertion, an instance-of or is-instance test, a typeof comparison, a comparison of class objects or type identities, a downcast. Open the file, find the routine or type that encloses each test, and read whether it declares a type parameter and whether the tested value has that parameter, or a type built from it, as its static type before any conversion to the top type, or whether the test reads the type parameter's own class object or type identity. Skip a test on any other value, such as a caught error, and a test in code that declares no type parameter. Read the cases and the branches: skip a test for an interface or trait whose branch calls that interface's methods or only chooses an algorithm that performs acceptably with that capability, skip an operation that must handle values of every type, such as a serializer, written with reflection, and skip a test that only adds special treatment for certain types to a shared implementation that performs the routine's operation for every type argument. Validator question: **Does a routine or type that declares a type parameter test the run-time type of a value typed by that parameter, or by a type built from it, or the type argument itself through a class object or type identity, to choose between branches that each carry the behaviour for a different concrete type?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: CODE-42`, severity minor, `file`, `symbol`, `code` = the added type-test line, verbatim from the diff, `fix` = an interface or trait that declares the operation, one implementation per type and the shared code calling that method, or, where a type the branches list cannot be given a new method in the file's language, as a built-in or third-party type may not, the per-type operation passed in as a function argument or one routine per listed type, each written for its concrete type, in the file's language, `rationale` = the types the branches list and the behaviour that differs between them).

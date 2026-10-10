---
title: When a routine's result or another parameter must have the type of an argument, or a data structure holds elements of one caller-chosen type, a type parameter states that type instead of the top type
rule_id: CODE-43
domain: code
step: [design, implement]
applies_to: [static-types, dynamic-types]
triggers: [':\s*(any|unknown|Any|object)\b\s*([,)=;\[\]]|$)', '\)\s*(:|->)\s*(any|unknown|Any|object)\b', '\b\w+\s+(\[\])?(any|interface\{\})\s*([,)]|$)', '\)\s*(\[\])?(any|interface\{\})\s*\{|\bObject\s+\w+\s*[,)(;=]', '(\[\]|\]|[<\[,]\s*)(any|Any|Object|interface\{\}|object|unknown)\s*([>\],){=]|$)', '\bdyn\s+Any\b']
scope: hunk
check_kind: semantic
severity_default: major
---

# When a routine's result or another parameter must have the type of an argument, or a data structure holds elements of one caller-chosen type, a type parameter states that type instead of the top type

## Thesis
Where the type of one position in a routine or a data structure follows the type of another, a type parameter declares that type in place of the top type, the type that admits a value of any and all types. A position's type follows another's when a routine returns, stores or yields a value it was given, when two of its parameters must hold values of the same type, and when a data structure holds elements that all have the one type its user supplies at the point of use. Where all the code does with a value is call a method on it, an interface type that declares the method serves in place of either.

## Rationale
The top type accepts an argument of any and all types, but it loses the information about what that type was: a routine that returns its argument as the top type tells its caller only that a value of any type could come back. To use that value as the type it was given, its reader has to narrow it, cast it, assert its type or switch on its type, or, where the top type permits every use, uses it unchecked; either way the code loses the benefits of static typing. The checker accepts such a cast as written, and a wrong one shows up, if at all, only when the program runs: depending on the language it throws, panics or yields an empty result there, or it is not checked at run time either and the value passes on unchanged. A top type that lets code assign its values to any other type and dereference any property of them can mask severe programming errors, and its use undermines the value of having static types in the first place. With the top type, a routine has no way even to state that it takes two sequences with the same element type, or that it takes a map of one element type and returns a sequence of the same element type. A type parameter captures the type the caller provides and uses it again where that type follows, so the routine works over a range of types and is just as precise as one written for a single concrete type: it loses no information. A data structure written over a type parameter has the same type-checking advantages as the built-in collections: the checker can verify the type of every value it holds, and the code can avoid type assertions.

## Example
```rust
bad:  struct Stack { items: Vec<Box<dyn Any>> }
      impl Stack { fn pop(&mut self) -> Option<Box<dyn Any>> { self.items.pop() } }
      let item = stack.pop().unwrap().downcast::<Item>().unwrap();
good: struct Stack<T> { items: Vec<T> }
      impl<T> Stack<T> { fn pop(&mut self) -> Option<T> { self.items.pop() } }
      let item: Item = stack.pop().unwrap();
```

## Limits
Where all the code needs to do with a value is call a method on it, an interface type that declares the method is correct and a type parameter is not: omitting the parameter makes the routine easier to write and easier to read. Where the method's implementation differs for each type, the code uses an interface type with one implementation per type, not a type parameter. Where an operation has to support even types that have no methods, so that an interface type does not help, and the operation differs for each type, so that a type parameter is not appropriate, the code uses run-time reflection, which works with a value of any type, as an encoder of arbitrary values does; the top type is correct there. Where the code only needs to express that a value's type is unknown, the top type expresses it, and a top type that allows no use of the value until it is narrowed or cast is much safer there than one that allows dereferencing any property. Where only one type is instantiated in practice, the fix is that concrete type rather than a type parameter; adding polymorphism later is straightforward compared to removing an abstraction found to be unnecessary. Where the top type is the best type argument for a generic type, the top type is correct there, though in many cases a type parameter is more appropriate. A method that overrides a base method whose signature gives a parameter the top type keeps that parameter type: overriding a method with a more specific argument type is unsafe, because the overriding signature should accept all valid calls to the base method. A top type that a comment documents as legitimate, such as a mock object constructed in a test, is accepted.

## Validator
Grep the added lines of the hunk for the top type as the type of a parameter, a result, a field or the elements of a container: `any`, `unknown`, `Any`, `object`, `Object`, `interface{}`, `dyn Any`. For each, read the routine or the type it belongs to in the hunk and decide whether the type of that position follows the type of another: the routine returns, stores or yields a value that came in through a top-typed position, two of its parameters must hold values of the same type, or the data structure's elements all have the one type its user chooses. A cast, a type assertion, a type switch or a downcast that recovers a concrete type from such a value, in the hunk or its context, confirms the link. Skip a value the code only calls methods on through an interface type, an operation that inspects the value by reflection because it differs for each type and must accept types without methods, a value whose type the code only needs to express as unknown, a parameter whose top type comes from the signature of a base method it overrides, and a top type that a comment documents as legitimate. Validator question: **Does an added declaration give a parameter, a result, a field or a container's elements the top type at a position whose type follows the type of another position, so that a reader has to cast or assert the value back to the type the caller passed, or uses it unchecked?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: CODE-43`, severity major, `file`, `symbol`, `code` = the added declaration that gives the position the top type, quoted verbatim from the diff, `fix` = the declaration rewritten in the file's language with a type parameter for the shared type, or with the concrete type where only one type is instantiated, and the cast at the use dropped, `rationale` = the position whose type follows the other's and the cast, assertion or type switch the top type forces on each reader, or the unchecked use it permits).

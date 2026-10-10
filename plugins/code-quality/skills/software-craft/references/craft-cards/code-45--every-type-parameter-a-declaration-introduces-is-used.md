---
title: Every type parameter a routine or a type declares is used in its signature, a field, another type parameter's constraint or its body
rule_id: CODE-45
domain: code
step: [implement, refactor]
applies_to: [static-types, dynamic-types]
triggers: ['\b(function|class|interface|type|fn|struct|enum|trait|record)\s+\w+\s*<\s*[A-Z]\w*\b', '(\b(public|private|protected|static|abstract|default|final)\b[^=;(]*|^\s*)<\s*[A-Z]\w*[^>]*>\s*[\w.<>\[\]?, ]+\s\w+\s*\(', '\b(func|type)\s+(\([^)]*\)\s*)?\w+\s*\[\s*\w+(\s*,\s*\w+)*\s+[^\]]+\]', '\bTypeVar\(|\b(Generic|Protocol)\[|\b(def|class)\s+\w+\s*\[\s*\w+', '\bimpl\s*<\s*[A-Z]', '^\s*((public|private|protected|static|async|readonly|override)\s+)*\w+\s*<\s*[A-Z]\w*[^()=;]*?>\s*\(|=\s*(async\s+)?<\s*[A-Z]\w*[^()]*?>\s*\(']
scope: hunk
check_kind: mechanical
severity_default: minor
---

# Every type parameter a routine or a type declares is used in its signature, a field, another type parameter's constraint or its body

## Thesis
Each type parameter that a routine or a type declares is used within that declaration: in the type of a parameter or of the result, in the constraint of another type parameter, in the type of a field or a member, or in a type or an expression in the body. A constraint that bounds the parameter itself is not a use of it. A type parameter with no use is removed, unless it was put there on purpose to indicate what type of data a value is tied to although no data of that type is stored in it; such a parameter is given a use, such as a zero-size field whose type mentions it.

## Rationale
Type parameters relate two types, and a parameter with no use relates nothing at all. A type parameter that is not used is dead code, which can only distract and possibly confuse developers during maintenance; at best it makes the code harder to read. Type inference has nothing to infer it from, since no argument and no member carries its type: depending on the language, every call has to name a type argument explicitly, which serves no purpose but to satisfy the compiler, or inference settles on an empty default type where the caller expected the type it meant. A declaration that uses the parameter gets correct inference. One compiler rejects an unused type parameter on a data type outright, and static-analysis checks in several ecosystems flag it on routines, classes, interfaces and records.

## Example
```python
bad:  class Registry[T]:
          def __init__(self) -> None: self.names: list[str] = []
          def add(self, name: str) -> None: self.names.append(name)
      items = Registry[Item]()
good: class Registry:
          def __init__(self) -> None: self.names: list[str] = []
          def add(self, name: str) -> None: self.names.append(name)
      items = Registry()
```

## Limits
A method that implements a method of an interface or a trait keeps the type parameters of the declaration it implements where the language requires the two to have the same type parameters, even when its own body does not use them; one tool checks only methods that implement no trait method. A method declared without a body in an interface or a trait is outside the rule as well: the bodies that implement it may use the parameter, and removing it from the declaration breaks every implementation that keeps it where the language requires the same type parameters; one tool lints no trait method, whether declared or implemented. Removing a type parameter from a declaration that other packages already call is a change that breaks the callers that pass a type argument for it: one tool suppresses its check on exported routines by default for that reason, and a project context that keeps its exported interface stable rejects the finding on such a declaration. A routine that uses a type parameter solely to test types — an empty body, a parameter that has only its own constraint, and calls that name a type argument for the compiler to check against that constraint — is outside the rule, since removing the parameter removes the test: one tool skips every routine with an empty body, and another names functions that use type parameters solely to test types as the case in which to disable its check. The rule asks whether a parameter has any use; a parameter used exactly once is outside it.

## Validator
Grep the added lines for a type parameter list on a routine, a type, an interface, a trait or an impl header, and for a type variable listed among a class's generic bases. For each type parameter declared on an added line, read the declaration it belongs to in the hunk — a routine's signature and body, or a type's fields, members and methods — and search it for the parameter's name: in the type of a parameter or the result, in another type parameter's constraint, in a field or member type, or in a type or an expression in the body. A constraint that bounds the parameter itself is no use; a method receiver or an impl header that restates its type's parameters declares no new ones, and a type's parameters are searched for across the whole type. When the added lines hold only part of the declaration, decide only when the hunk's context lines show the rest of it, and skip it otherwise. Skip a method that implements an interface or trait method whose declaration has the same type parameters, a method declared without a body in an interface or a trait, a routine with an empty body whose type parameter has only its own constraint, a deliberate parameter given a use through a zero-size marker field, and an exported declaration the project context keeps stable. Validator question: **Does an added declaration introduce a type parameter that neither its signature, another type parameter's constraint, its fields and members nor its body use?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: CODE-45`, severity minor, `file`, `symbol`, `code` = the added line that declares the unused type parameter, verbatim from the diff, `fix` = the declaration without the parameter and each call in the hunk without its type argument, or, for a parameter kept on purpose, the declaration with a use of it — a zero-size field whose type mentions it where the language has one, otherwise a member whose type mentions it — in the file's language, `rationale` = the parameter nothing in the declaration uses and the type argument a caller has to name, or cannot have inferred, for it).

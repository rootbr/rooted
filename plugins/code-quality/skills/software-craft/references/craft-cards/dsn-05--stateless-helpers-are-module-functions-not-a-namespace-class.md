---
title: Stateless helper functions are module-level functions rather than static members of a class used only as a namespace, and where the language requires a class that class hides its constructor
rule_id: DSN-05
domain: design
step: [design, implement, refactor]
applies_to: [universal]
triggers: ['^\s*((export|default|public|private|protected|internal|final|abstract|static|pub(\([^)]*\))?)\s+)*(class|struct|enum)\s+\w*(Utils?|Utilities|Helpers?|Tools|Constants)\b|^\s*((public|abstract)\s+)?final\s+class\s+\w+|^\s*(pub(\([^)]*\))?\s+)?struct\s+\w+\s*(;|\{\s*\}\s*$)', '^\s*((public|private|protected|export)\s+)?static\s+(readonly\s+)?\w|^\s*@staticmethod\b|^\s*private\s+[A-Z]\w*\s*\(\s*\)\s*\{|^\s+pub(\([^)]*\))?\s+(((const|async|unsafe)\s+)*fn\s+\w+\s*(<[^>]*>)?\s*\((?!\s*(&\s*(\x27\w+\s+)?)?(mut\s+)?self\b)|const\s+[A-Z_][A-Z0-9_]*\s*:)']
scope: file
check_kind: mechanical
severity_default: minor
---

# Stateless helper functions are module-level functions rather than static members of a class used only as a namespace, and where the language requires a class that class hides its constructor

## Thesis
A class or other type whose members are all static, meaning functions that take no instance and fields that hold constants, holds no state and serves only as a namespace. Where the language lets functions and constants be declared at module level, they are declared and exported there, not wrapped in such a type. Where the language requires every function to belong to a class, that class declares a constructor that is not public: private, or protected where the class is meant to be subclassed. The compiler then generates no default constructor, and a private constructor can be called only from code inside the class or inside the top-level type that encloses it.

## Rationale
Such a type only groups names. Where the language has modules, the module already organizes whatever the type would hold. A wrapper type then adds cognitive complexity without adding any structural improvement. Where every function must belong to a class, the class has to stay, but creating an instance of it makes no sense. A class that declares no constructor still receives a parameterless one from the compiler, with the class's own access, and forgetting to hide that default constructor is a common mistake. Declaring a constructor that is not public prevents the compiler from generating it.

## Example
```rust
bad:  pub struct TextUtils;
      impl TextUtils {
          pub fn join(a: &str, b: &str) -> String { ... }
      }
good: pub mod text {
          pub fn join(a: &str, b: &str) -> String { ... }
      }
```

## Limits
The rule reaches a type only when every member is static and the type has no instance fields. It must also extend no class, implement no interface or trait, and hold no program entry point, and, where the language requires every function to belong to a class, be concrete rather than abstract. A type that fails any of these is not a utility type in the rule's sense, and the rule does not reach it. A type with no members holds nothing to group, and an enumeration that declares at least one value has instances; neither is a utility type in the rule's sense, while an enumeration with no values that holds only static members is one.

A static member that the code is forced to declare in order to integrate with an API defined in an existing library is accepted.

Analyzers of the rule let a project exempt types that carry a decorator, or an annotation the project names. A project context that names such an exemption rejects the finding.

Whether a type made only of static methods should instead become a single shared instance is contested. One position counts a class that contains only static methods as a good candidate for a single instance. It says so while describing single instances whose fields occur only once per class, just like static fields, and which often control access to resources such as database connections or sockets. The other position holds that static state is what is bad, that nothing is wrong with the static keyword, and that for pure functions such as sorting or math static is just fine. The condition that separates them is state. The rule reaches a type whose static fields hold only constants. A type whose static fields hold mutable state, or a resource such as a connection or a socket, is outside it. The rule does not decide whether such state should exist, or in what form. A static helper whose operation has one obvious receiver among the codebase's own types with behaviour is judged by its own rule, which makes it a method of that type.

## Validator
In the hunk, find each added class, struct or enum declaration, each added static member or static-method decorator, and each added private parameterless constructor. Open the file and read the whole type that holds it, together with every block in the file that attaches functions to that type. Go on only when the type has at least one member, every member is static, the type has no instance fields, and its static fields hold only constants. Skip a type that extends a class, implements an interface or trait, or holds a program entry point, and, where every function must belong to a class, a class that is abstract. Skip an enumeration that declares at least one value, and, where every function must belong to a class, every enumeration, whose constructor is never public. Skip a static member that an API defined in an existing library forces on the code. Skip a type carrying an annotation or decorator that the project context exempts. Where the language lets functions be declared at module level, take the type itself as the finding. Where every function must belong to a class, read the class's constructors, and go on only when it declares a public one, or declares none and the class itself is not private. Validator question: **Is this type a namespace for static functions and constants that either wraps what the language could declare at module level, or, where the language requires the class, leaves a public constructor, or a compiler-generated one on a class that is not itself private?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: DSN-05`, severity minor, `file`, `symbol`, `code` = the type's declaration line and its public constructor where the diff adds them, otherwise the added static member, static-method decorator or constructor line that brought the type into the check, quoted verbatim from the diff, `fix` = the functions and constants declared and exported at module level, or, where the language requires the class, each public constructor made private, or a private parameterless constructor added where the class declares none, in the file's language, `rationale` = that the module already organizes what the type holds, or that an instance of the class makes no sense and the compiler generates a constructor with the class's own access unless one is declared).

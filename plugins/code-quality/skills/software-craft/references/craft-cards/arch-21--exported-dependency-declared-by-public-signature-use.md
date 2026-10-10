---
title: A library whose build tool separates exported from internal dependencies declares as exported each dependency with a type in its public interface, such as a supertype, a parameter or return type of a visible method or a public field, and declares every other dependency as internal
rule_id: ARCH-21
domain: architecture
step: [implement, review]
applies_to: [library, public-api, build-config]
triggers: ['^\s*(api|implementation|compileOnlyApi|compileOnly)\b\s*[(]?\s*[''"(\w]', '\bpublic\s*=\s*true\b', '^\s*(public|protected)\s+([\w<>\[\],.?@]+\s+)*\w+\s*\(', '^\s*pub(\([\w:]+\))?\s+((async|const|unsafe)\s+)*(fn|struct|enum|trait|type|const|static|use)\b', '\bimpl(<[^>]*>)?\s+[\w:]*(From|Into|TryFrom|AsRef|Deref)\s*<\s*\w+::', '^\s*(public|protected)\s+([\w<>\[\],.?@]+\s+)+\w+\s*(=|;)', '\b(class|interface|record)\s+\w+(<[^>]*>)?[^{]*\b(extends|implements)\b', '^\s*pub(\([\w:]+\))?\s+\w+\s*:\s*\S']
scope: callers
check_kind: semantic
severity_default: major
---

# A library whose build tool separates exported from internal dependencies declares as exported each dependency with a type in its public interface, such as a supertype, a parameter or return type of a visible method or a public field, and declares every other dependency as internal

## Thesis
In a build whose tool separates the dependencies a library exports to its consumers from those internal to it, the library declares as exported each dependency that contains at least one type exposed in its public interface, such as a type used in a supertype, in a parameter or return type of a routine in that interface, in a public field, as a public annotation type or in a trait implementation. It declares as internal each dependency whose types are used only in routine bodies, in private members or in internal classes, and as exported such a dependency whose type a consumer's compiler still has to read, as for a private overload of a public routine or a type annotation on a private member; it prefers the internal declaration wherever that is possible.

## Rationale
Under one tool, an exported dependency is transitively exposed to consumers and appears on their compile classpath, while an internal one stays off it, so consumers never depend on it by accident, compile against a smaller classpath and need no recompilation when it changes. A semver-incompatible upgrade of an exported dependency is a breaking change of the library itself. When a type of a dependency declared internal leaks into the public interface, consumers fail to compile at once under one tool, and another tool's compiler lint `exported_private_dependencies`, a warning on by default, reports the type from a private dependency in a public interface. Under one tool a member counts as public when compilers can see it, so protected and package-private members count alongside public ones; under the other a routine visible only inside the library does not count. The compiler's view of the interface can be broader than these rules of thumb: it can need a type used only in a private member, most commonly when that member carries a type annotation or when overload resolution for a public routine has to examine it, and a consumer whose compile classpath lacks the type then fails to compile. Such a dependency is promoted to exported, as a compile-only export when consumers do not otherwise need it at runtime.

## Example
```java
bad:  // build.gradle.kts: implementation("com.example:yamlkit:1.0"), api("com.example:logkit:1.0")
      public yamlkit.Node load(String path) {
          logkit.Log.debug(path);
          return yamlkit.Parser.parse(path);
      }
good: // build.gradle.kts: api("com.example:yamlkit:1.0"), implementation("com.example:logkit:1.0")
      public yamlkit.Node load(String path) {
          logkit.Log.debug(path);
          return yamlkit.Parser.parse(path);
      }
```

## Limits
A build tool that declares every dependency in one list, with no split between exported and internal, carries no such declaration, and the rule does not reach it. One tool supports the split only on its nightly channel and only in a build that enables it; any other build of that tool lies outside the rule. A dependency whose type reaches consumers' compilation through a private member, such as by a type annotation on that member or through overload resolution of a public routine, is correctly declared exported although no public signature names it. When a type of an internal dependency is found in the public interface, two repairs satisfy the rule: switching the dependency to exported, or removing its type from the interface; translating a foreign type into the library's own type at the boundary is the second repair, and choosing between the two is a boundary-design question this rule leaves open. A module that exists to hand a set of dependencies to its consumers and holds no code of its own, such as a starter or an aggregate module, declares them exported by design, and the rule does not reach it.

## Validator
Grep the hunk for a dependency declaration in a build file that separates exported from internal dependencies (Gradle `api`, `implementation`, `compileOnlyApi`, `compileOnly`; a Cargo dependency with or without `public = true`, only where the build enables Cargo's public-dependency support, since a stable Cargo ignores the flag) and for a changed signature in the public interface: a supertype, a parameter or return type of a routine its build tool counts as public (under Gradle a public, protected or package-private one, under Cargo a `pub` one but not a `pub(crate)` one), a public field, a public annotation type, a trait implementation. For each dependency whose declaration the hunk touches or whose type a changed public signature names, open the library's sources at scope callers and list where that dependency's types are used: in the public interface, or only in routine bodies, private members and internal classes. Count as public-interface use any type a consumer's compiler still has to read, such as one that annotates a private member or one that overload resolution of a public routine examines. Validator question: **Is a dependency declared internal while one of its types is used in the library's public interface, or declared exported while its types are used only in routine bodies, private members or internal classes?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: ARCH-21`, severity major, `file`, `symbol`, `code` = the dependency declaration and the public signature or private-only use of its type, quoted verbatim from the diff, `fix` = the declaration moved to the exported or internal configuration that matches where the dependency's types are used, or the leaked type removed from the public signature, in the build file's or source file's language, `rationale` = which dependency's type is used where and what the mismatch costs: a consumer compile failure or lint warning for a leaked internal type, a wider consumer compile classpath and recompilation for an over-exported one).

---
title: A component exposes a dependency to its consumers only when a type from that dependency appears in its public API or headers or the compiler needs it to compile them, and declares every other dependency it uses as private to it
rule_id: ARCH-05
domain: architecture
step: [implement, review]
applies_to: [build-config, library]
triggers: ['^\s*api\s*\(', '^\s*api\s+["''\w]', '\btarget_link_libraries\s*\([^)]*\b(PUBLIC|INTERFACE)\b', '^\s*(PUBLIC|INTERFACE)\s+[\w:${]', '\bpublic\s*=\s*true\b']
scope: callers
check_kind: semantic
severity_default: minor
---

# A component exposes a dependency to its consumers only when a type from that dependency appears in its public API or headers or the compiler needs it to compile them, and declares every other dependency it uses as private to it

## Thesis
A component declares a dependency in the exposed form, the one its build passes on to consumers or declares part of the component's interface, only when at least one type of that dependency is exposed in the component's binary interface or public headers, or the compiler needs that dependency to compile consumers against the component; every other dependency is declared in the form that stays internal to the component.

## Rationale
Where the build passes the exposed form on to consumers, the dependency appears on their compile classpath, or its usage requirements are propagated to them as part of the component's link interface; where the build does not pass it on, the exposed form declares the dependency part of the component's interface, and, where the toolchain enables that declaration, the component's own build warns when a type of a dependency left internal appears in that interface. A dependency in the internal form is linked to the component but is not made part of that interface, so it does not leak into what consumers compile against. Where the build puts the exposed form on consumers' compile classpath, keeping a dependency internal has three effects for them: they never come to depend on it by accident as a transitive dependency, their compile classpath is smaller so they compile faster, and they need no recompilation when that dependency changes. Exposure also enters the component's own compatibility: bumping the version of a dependency whose types the component exports is a breaking change of the component itself, while, in a build that lets several versions of one dependency coexist in the graph, a dependency contained in the implementation is effectively invisible to consumers and can be duplicated there without compilation errors. A type counts as exposed when it appears, among other places, in a supertype or implemented interface, in a parameter of a member visible to compilers including generic parameter types, in a return value, in a public field, as a public annotation type, or in a public header, for example through inheritance. A type used only in routine bodies, only in private members or only in internal classes is irrelevant to that interface. Preferring the internal form also makes a leak visible: where the build puts the exposed form on consumers' compile classpath, they fail to compile at once if an implementation type slips into the public API.

## Example
```rust
bad:  // Cargo.toml: codec = { version = "1", public = true }
      pub fn encode(order: &Order) -> Vec<u8> { codec::to_bytes(order) }
good: // Cargo.toml: codec = "1"
      pub fn encode(order: &Order) -> Vec<u8> { codec::to_bytes(order) }
      // Cargo.toml: wire = { version = "1", public = true }
      pub fn frame(order: &Order) -> wire::Frame { wire::Frame::new(encode(order)) }
```

## Limits
A dependency used only by the public headers and not by the implementation takes the interface-only form, which adds it to the link interface without linking it into the component. The compiler's view of the interface can be broader than the author's: in some situations one compiler needs a dependency's compiled types to compile consumers even when the type is used only in a private member, most commonly when that member carries a type annotation or when overload resolution for a public routine has to examine it. Such a dependency is promoted into the exposed form, compile-only when consumers do not otherwise need it at runtime, because the separation has to account for what the compiler requires when compiling against the component and not only for the types its author considers public. Where the build puts the exposed form on consumers' compile classpath, moving a dependency from the exposed to the internal form takes it off that classpath; a consumer that used it as a transitive dependency is then advised to declare it directly, and dependency analysis tools report such used transitive dependencies. A manifest public flag takes effect only where the toolchain enables its unstable opt-in; without it the build ignores the flag, and the exposed and internal declarations build alike. An exposed-form entry that passes only version constraints on to consumers, such as a dependency on a platform or bill of materials, is outside the rule. So is every entry of a platform component: it has no binaries, and its exposed configuration exists to hand constraints, and the dependencies its build explicitly allows, to whoever compiles against it. The rule reaches the dependency declarations at a component's boundary; which class or routine inside a component imports which other is outside it.

## Validator
Grep the hunk for a dependency declared in the exposed form: an `api` configuration entry, a `PUBLIC` or `INTERFACE` item of a link command, a manifest entry carrying `public = true`; skip an entry that declares a platform, a bill of materials or a version constraint, and every entry in the build file of a platform component. For each such dependency, open the component's public surface: its exported types and their members visible to compilers, its public headers, its re-exports. Search that surface for any type of the dependency in a supertype or implemented interface, a parameter or return value, a public field, a public annotation, or a header include. Where every use sits in routine bodies, private members or internal classes, check whether a private member carries a type annotation from the dependency or a public routine's overload resolution examines such a member. Validator question: **Is a dependency declared in the exposed form while none of its types is exposed in the component's binary interface or public headers and the compiler does not need it to compile consumers?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: ARCH-05`, severity minor, `file`, `symbol`, `code` = the exposed-form declaration line quoted verbatim from the diff, `fix` = the same dependency declared in the internal form — an `implementation` entry, a `PRIVATE` item, the manifest entry without the public flag — in the file's build syntax, or the declaration removed when the implementation does not use the dependency either, `rationale` = names the dependency, states that none of its types appears in the component's binary interface or public headers, and names what the exposed form costs in that build: the dependency passed into consumers' compilation, and on a compile classpath their recompilation when it changes, or, for a manifest public flag, the dependency's version made part of the component's own compatibility).

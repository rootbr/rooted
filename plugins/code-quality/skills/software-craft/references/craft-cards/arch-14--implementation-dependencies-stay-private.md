---
title: A dependency a component uses only inside its implementation is declared as private to the component, such as an implementation or PRIVATE dependency, and only a dependency that the component's public interface uses is exported to its consumers
rule_id: ARCH-14
domain: architecture
step: [implement, refactor, review]
applies_to: [build-config, library]
triggers: ['^\s*(api|compileOnlyApi)\s*[(\s]\s*["''(\w]|\bexports\s*=\s*\[|\btarget_link_libraries\s*\([^)]*\b(PUBLIC|INTERFACE)\b|^\s*(PUBLIC|INTERFACE)\s+[\w:$<>{}.-]+']
scope: callers
check_kind: semantic
severity_default: minor
---

# A dependency a component uses only inside its implementation is declared as private to the component, such as an implementation or PRIVATE dependency, and only a dependency that the component's public interface uses is exported to its consumers

## Thesis
Where the build distinguishes a component's exported dependencies from its internal ones, a dependency that a change adds or edits is declared as internal when only the component's implementation uses it. It is declared as exported only when the component's public interface uses it: at least one of its types is exposed there, such as a superclass or implemented interface, a parameter of a public routine including a generic type argument, a public field or a public annotation type, or a public header uses something it provides, such as one of its headers, a macro, an inline routine or a type.

## Rationale
An exported dependency is transitively exposed to the component's consumers, as if each of them had declared it; an internal dependency is not exposed to them, so a consumer never comes to depend on it by accident, and a consumer that does use its types declares that dependency itself. Where the build also keeps internal dependencies out of what consumers compile against, consumers compile faster, need not be recompiled when an implementation dependency changes, and fail to compile at once if one of the dependency's types accidentally leaks into the public interface. Public here means visible to compilers, which includes protected and package-visible members where the language has them. Types used exclusively in routine bodies, in private members, or in classes internal to the component are irrelevant to that interface.

## Example
```python
bad:  # json is used only inside the method bodies of Orders.java
      java_library(name = "orders", srcs = ["Orders.java"],
                   deps = [":json"], exports = [":json"])
good: java_library(name = "orders", srcs = ["Orders.java"],
                   deps = [":json"])
```

## Limits
The compiler's view of the interface can be broader than the declared one. A consumer's compiler sometimes needs a type that appears only in a private member, most commonly when that member carries a type annotation or when overload resolution for a public routine has to examine it; such a dependency is exported, as compile-only where consumers do not otherwise need it at runtime. A dependency needed only at runtime goes to a runtime-only declaration where the build has one, which keeps it available at runtime and out of compilation. Where a component's published metadata puts implementation and interface dependencies in one compile scope, both reach what the consumer compiles against, so the separation takes effect only through metadata that keeps the two scopes apart. Where the build also has an interface-only form, a dependency that only the public headers use, and the implementation does not, takes that form; the validator leaves the choice between that form and an exported declaration alone, since the public headers use the dependency either way. A component with no sources of its own, such as an alias, a wrapper around a third-party library or an aggregate starter, exists to re-export the dependencies it declares; those declarations are its interface, and the validator leaves them alone.

## Validator
Grep the hunk for a dependency declared as exported: an `api` or `compileOnlyApi` configuration entry, an `exports` list, or a `PUBLIC` or `INTERFACE` keyword on a link declaration. For each hit, name the dependency and the component that declares it, and skip the hit when the component has no sources of its own. Open the component's public interface and search it for any type the dependency provides: the supertypes and implemented interfaces of its public types, the signatures of its public routines with their generic type arguments, and its public fields and annotation types; search its public headers for any use of the dependency, an include of one of its headers or a macro among them. Where neither appears, open the private members of the public types and look for a type annotation, or an overload of a public routine, that names one of the dependency's types. Trace the component's consumers across the repository and list each one that uses the dependency directly, since each of them takes its own declaration in the fix. Validator question: **Does the change export a dependency that the component's public headers do not use and none of whose types appears in the component's public interface or in a private member that a consumer's compiler must read?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: ARCH-14`, severity minor, `file`, `symbol`, `code` = the exported dependency declaration quoted verbatim from the diff, `fix` = the same dependency declared as internal in the file's build language, plus a direct declaration in each consumer that uses it directly, `rationale` = names that the component's public interface does not use the dependency, so exporting it exposes it to the compilation of every consumer).

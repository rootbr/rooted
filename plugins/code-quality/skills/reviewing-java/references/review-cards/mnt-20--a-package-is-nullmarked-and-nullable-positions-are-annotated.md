---
title: A package is @NullMarked, and every parameter, return type or field that may hold null carries the JSpecify @Nullable annotation
rule_id: MNT-20
domain: maintainability
triggers: ['return null;', '@Nullable', '@NonNull', '@NullMarked', 'package-info', '== null|!= null']
scope: file
check_kind: mechanical
severity_default: minor
---

# A package is @NullMarked, and every parameter, return type or field that may hold null carries the JSpecify @Nullable annotation

## Thesis
In a project that has adopted JSpecify, every package under review is `@NullMarked` (in its `package-info.java`, or on the module), so that unannotated types are non-null by contract, and every method that can return `null`, every parameter that accepts `null`, and every field that may be `null` carries `org.jspecify.annotations.Nullable`; an override repeats the annotations of the method it overrides.

## Rationale
Without a null-marked scope the nullness of a type is unspecified, so neither a checker nor a reader can tell a return that may be `null` from one that never is, and null checks accumulate where they are not needed while going missing where they are. In `@NullMarked` code, `String x` means a non-null `String`; `@Nullable` marks the exceptions explicitly, which are the minority, and a checker (NullAway in `OnlyNullMarked` mode, the IDE) reports each dereference of a nullable value and each `null` passed where non-null is declared, at compile time. Spring Framework 7 exposes its own API through these annotations, and a project depending on it is recommended to use the same, so that one checker reads both.

## Example
```java
bad:  package app.orders;                                           // package not null-marked
      public String findNote(long id) { if (!notes.containsKey(id)) return null; return notes.get(id); }   // unannotated
good: @NullMarked package app.orders;  import org.jspecify.annotations.NullMarked;   // package-info.java
      public @Nullable String findNote(long id) { return notes.get(id); }
```

## Limits
Applies when the project has JSpecify on the classpath or a null-safety policy in the project context; a project that has not adopted nullness annotations is out of scope. A `@NullUnmarked` scope explicitly opts a legacy package out. Local variables are inferred and are not annotated. Kotlin sources carry nullness in the type system.

## Validator
On the triggered hunk find each `return null`, each parameter or field compared with `null`, and each nullness annotation. Open the file: treat the scope as `@NullMarked` only when the hunk or the file itself shows the marker — a `@NullMarked` on the class, or a `package-info.java` or `module-info.java` that is part of the diff — and as unmarked otherwise, without opening a sibling file; then check whether each nullable position carries the JSpecify `@Nullable`. Validator question: **can this position hold `null` without a JSpecify `@Nullable` in a `@NullMarked` scope?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: MNT-20`, severity minor, `file`, `symbol`, `code` = the unannotated return, parameter or field quoted verbatim from the diff, `fix` = the `@NullMarked` package-info or the `@Nullable` position, `rationale` naming the dereference a checker would otherwise miss).

## Source
JSpecify User Guide, "@NullMarked" — "When you apply @NullMarked to a module, package, class, or method, it means that unannotated types in that scope are treated as if they were annotated with @NonNull … packages are not hierarchical; applying @NullMarked to package com.foo does not make package com.foo.bar @NullMarked". Spring Framework reference, Null-safety → JSpecify — `@NullMarked` "is typically set in Spring projects at the package level via a package-info.java file"; "In @NullMarked code, nullable type usage is defined explicitly with @Nullable"; "When overriding a method, JSpecify annotations are not inherited from the original method"; NullAway `NullAway:OnlyNullMarked=true` checks packages annotated with `@NullMarked`.

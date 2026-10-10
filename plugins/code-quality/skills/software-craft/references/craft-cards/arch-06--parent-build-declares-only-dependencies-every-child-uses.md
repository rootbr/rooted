---
title: A parent or root build file declares a dependency for every child module only when every child uses it, and for a dependency that only some children use it centralizes the version alone
rule_id: ARCH-06
domain: architecture
step: [implement, refactor, review]
applies_to: [build-config]
triggers: ['^\s*<dependency>\s*$', '^\s*(subprojects|allprojects)\s*\{', '\bconfigure\s*\(\s*(subprojects|allprojects)\b', '\b(subprojects|allprojects)\s*\(']
scope: callers
check_kind: semantic
severity_default: minor
---

# A parent or root build file declares a dependency for every child module only when every child uses it, and for a dependency that only some children use it centralizes the version alone

## Thesis
A parent or root build file adds a dependency to all of its child modules only when every child that receives it uses it. For a dependency that only some children use, the parent centralizes the version alone, and each child that uses the dependency declares it without a version.

## Rationale
Where a build tool passes a parent's dependency list down by inheritance, a module receives every dependency in that list along with the ones it declares, so an entry in that list reaches every child. In a study of one public package repository, 4,963 artifacts belonged to multi-module projects and inherited dependencies from a parent. Of all inherited dependency relationships, 61.8% (111,649, which is 15.4% of every dependency studied) were not used by the module that inherited them. Multi-module artifacts carried a median of 5 unused inherited dependencies, with a first quartile of 1 and a third quartile of 20. The analysis names two challenges of a common parent: unused inherited dependencies emerge because removing a dependency from a parent is harder than removing it from a module's own build, and developers find it harder to be aware of and understand the dependencies a module inherits. A shared parent still contributes to limiting redundant dependencies and facilitates consistent versioning of dependencies in large projects. Its version-management section controls which version of a dependency a child uses when, or if, the child references it. Build logic that a root build injects into children through cross-project configuration is not obvious when looking at a child's own build script. In the long run such configuration usually grows in complexity and becomes a burden, and it can introduce configuration-time coupling between projects. Declaring a partially used dependency in the children that use it puts it in the build script a reader of that child opens, while the parent keeps the shared version.

## Example
```java
bad:  root.subprojects(child -> child.getDependencies()
          .add("implementation", "org.example:codec:1.2"));
good: root.getDependencies().getConstraints()  // the root's own build, a platform
          .add("api", "org.example:codec:1.2");
      user.getDependencies().add("implementation",  // each user's own build
          user.getDependencies().platform(user.getRootProject()));
      user.getDependencies().add("implementation", "org.example:codec");
```

## Limits
A dependency that every child uses may stay in a parent's inherited dependency list, since one declaration shared by many modules is the main motivation for a parent build. A cross-project block that injects a dependency every child uses passes this rule, while the cited build-tool guidance advises against such blocks whatever they inject. An entry in the parent's version-management section sets a version without adding the dependency to a child and is outside the rule. A dependency that a child reaches only through reflective calls or dynamic loading, or uses only for compile-time constants or annotations the compiler discards, counts as used; an analysis of compiled code can miss these uses, which can lead to false positives. The rule reaches what a child receives from its parent or root build; a dependency that a module declares itself and never uses, and a transitive dependency, are judged at the level of that module.

## Validator
Grep the hunk for a dependency entry in a parent or root build file's own dependency list, outside its version-management section, and for a cross-project block (`subprojects`, `allprojects`, or a configure call over them) that adds a dependency. Open the children that receive it at scope callers: the modules that name this build as their parent, or the subprojects the block selects; where a child has no sources of its own and is itself the parent of further modules, check those modules in its place. For each child, search its sources and tests for a reference to the dependency's packages or types, a reflective or dynamic load of it, and a runtime-only role such as a driver, engine or provider. Validator question: **Does the parent or root build add this dependency to at least one child that shows none of these uses?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: ARCH-06`, severity minor, `file`, `symbol`, `code` = the dependency entry or the cross-project block verbatim from the parent build, `fix` = the entry moved to the parent's version-management section and a version-less declaration of the dependency added to each child that uses it, together with that child's import of the parent's version set where the build tool does not pass versions down by inheritance, in the build file's language, `rationale` = the children that receive the dependency without using it, with their count, and the share of inherited dependencies found unused in multi-module projects).

---
title: An added import leaves the dependency graph of modules and packages acyclic, with no path of imports leading back to the importing module
rule_id: DSN-10
domain: design
step: [design, implement]
applies_to: [universal]
triggers: ['^\s*import\s+[\w.{*''"]', '^\s*from\s+[.\w]+\s+import\b', '\bfrom\s+[''"]', '\b(require|import)\s*\(\s*[''"]', '\b(use\s+\w+|crate|super)::', '^\s*([\w.]+\s+)?"[\w.\-]+(/[\w.\-]+)+"\s*(//.*)?$']
scope: callers
check_kind: semantic
severity_default: major
---

# An added import leaves the dependency graph of modules and packages acyclic, with no path of imports leading back to the importing module

## Thesis
An import added from one module of the codebase to another leaves the import graph acyclic: following imports onward from the imported module never leads back to the importing module, whether the path is direct (A imports B and B imports A) or runs through other modules. A module is the unit an import names, such as a source file or a package. Where the project's configured cycle check declares sibling packages acyclic, the same holds one level up for them, the directories or namespaces that group modules under one parent: an import from any module inside one sibling into any module inside another is an edge between the two siblings, and those edges form no cycle either. An import counts wherever it sits and however it loads, at the top level, deferred into a routine or loaded dynamically; an import marked type-only, which the compiler erases, or guarded so that it runs only under the type checker, is not an edge unless the project's build or configured cycle check counts it.

## Rationale
Dependency cycles among components are pervasive in real systems and are known to harm understandability, testability, reusability, buildability and maintainability. Some toolchains refuse them: one language specification makes it illegal for a package to import itself directly or indirectly, one module system's resolution can fail when it detects a cycle such as two modules that require each other, and various build systems will not accept a cycle because each module has to depend on the other. Where the language accepts a cycle, linters and import-contract checks report it, one of them at severity error in its preset, and the cycle can still fail at load time. In one module system, modules that import each other as a whole load, but when the second module takes a name out of the first with a top-level import, the import fails, because the first module's names are not yet available while it is busy importing the second; elsewhere a cycle can lead to symbols that are unexpectedly undefined. Moving the import into a routine avoids that failure but keeps the cycle, and one linter names its option that stops reporting a cycle through a dynamic import unsafe. Defect studies associate cycles with defects. In 19 large-scale projects, files involved in architecture anti-patterns, cliques of files with cyclic dependencies and package cycles among them, were more error-prone and change-prone; every anti-pattern contributed, two others by far the most. In six applications, most defects and defective components were concentrated in components that are cyclically dependent, directly or indirectly. The rule restores imports that go in a single direction. A cycle is broken by moving code so that imports go one way, for example the shared contract into a neutral module; by consolidating packages too small to stand on their own; or by removing one import through an interface that the module needing the other declares and uses in place of the other's concrete type, which is dependency inversion. Introducing interfaces to break dependency cycles is often a signal of improperly structured packages, and the best strategy depends heavily on the context of the code and the affected modules.

## Example
```rust
bad:  mod order { use crate::billing::charge;
          pub struct Order { pub total: u64 }
          pub fn place(o: &Order) { charge(o) } }
      mod billing { use crate::order::Order;
          pub fn charge(o: &Order) { ... } }
good: mod model { pub struct Order { pub total: u64 } }
      mod order { use crate::{billing::charge, model::Order};
          pub fn place(o: &Order) { charge(o) } }
      mod billing { use crate::model::Order;
          pub fn charge(o: &Order) { ... } }
```

## Limits
An import that only the type checker reads, marked type-only and erased before run time or guarded so that it never runs, cannot fail at load time, and three cycle checks leave it out of the graph by default; the rule leaves it out too, unless the project's build declares a dependency for it or the project's configured cycle check counts it, as one import-contract check does by default: one style guide calls any cycle caused by typing a code smell and a good candidate for refactoring, because various build systems will not let each module depend on the other. An import that runs counts even when the module uses only types from it. A module that imports itself is outside the rule, which judges an import from one module to another; one cycle check allows a self-import that exposes a module's own names as a namespace. The rule judges imports between modules and packages of one codebase: an import of a standard or third-party library is not traced, and a dependency between services over a network is outside it. The package level applies only where the project's configured cycle check declares sibling packages acyclic; there the rule compares siblings under a common parent, generation by generation, and an import between a package and its own descendants is judged at the module level only. Without that declaration the rule judges the module graph alone. An edge that the project's configured cycle check ignores by name, such as an entry in its list of ignored imports, is a documented tolerance, and a project context that names it rejects the finding for that edge.

## Validator
Grep the added lines for an import: an import or use statement, a from-import, a re-export, a require or dynamic import call, a path line inside an import block. Skip an import of a standard or third-party library, an import marked type-only or guarded to run only under the type checker unless the project's build files or configured cycle check count it, and a module importing itself. For each remaining import by module A of module B, open B and follow its imports of modules inside the codebase, then theirs in turn, searching the repository for a path back to A; a single import of A by B is the direct case. Where the project's configured cycle check declares sibling packages acyclic, also find the nearest common parent of A and B: when they sit in different sibling packages under it, search the repository for imports from modules of B's sibling into the other siblings and trace whether such edges lead back to A's sibling. Skip an edge that the project's configured cycle check ignores and the project context names. Validator question: **Does an added import complete a path of imports that leads back to the importing module, or, where the project's configured cycle check declares sibling packages acyclic, back to the importing module's package through its sibling packages?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: DSN-10`, severity major, `file`, `symbol`, `code` = the added import line quoted verbatim from the diff, `fix` = the cycle broken, in the file's language: the shared code moved into a module both import, the modules consolidated, or the import replaced by an interface that the importing module declares, `rationale` = the cycle as its chain of modules or packages, each edge with the file and line of its import, and the direction the fix leaves the imports pointing).

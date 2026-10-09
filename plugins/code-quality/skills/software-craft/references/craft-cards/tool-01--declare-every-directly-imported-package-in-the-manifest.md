---
title: Every package the code imports directly is declared in the ecosystem's manifest rather than reached through a transitive dependency
rule_id: TOOL-01
domain: tooling
step: [implement, review]
applies_to: [universal]
triggers: ['^\s*import\b', '^\s*from\s+[A-Za-z_][\w.]*\s+import\b', '\brequire\s*\(\s*["''][^./"'']', '\bimport\s*\(\s*["''][^./"'']', '^\s*(pub\s+)?use\s+[A-Za-z_]\w*::|^\s*extern\s+crate\b', '^\s*(import\s+)?(\w+\s+)?"[\w.-]+[.][a-z]{2,}/[\w./-]+"\s*$']
scope: callers
check_kind: mechanical
severity_default: major
---

# Every package the code imports directly is declared in the ecosystem's manifest rather than reached through a transitive dependency

## Thesis
An external package that a module's code imports or references directly is declared in that module's manifest, even when another declared dependency already brings it in transitively.

## Rationale
A package that arrives only through another dependency stays in the build only while that dependency keeps it: when the intermediate dependency updates or removes its own dependency on the package, the importing code may fail to build, and code that works locally can break after dependencies are re-installed. Such a package also carries no version the project chose: the package manager resolves it from the project context, so its version shifts whenever a declared dependency is upgraded, with no manifest entry to signal that the dependency exists, let alone changed. Across 19,812 versions of 1,157 of the most used libraries in one ecosystem's central repository, 6,761 versions (34.12%) contained at least one used-but-undeclared dependency; approximately 48% of these dependencies introduced breaking changes through version drift, and 22% of them had their breaking entities actively used by the root project. Many widely used composition-analysis tools examine only declared dependencies, and 30.28% of the undeclared ones were affected by known vulnerabilities under the version-range convention those tools apply to declared dependencies. A declared dependency can still drift within its range, but that drift follows the project's own choice, and a project that carries its own specification for a shared dependency notices any conflict with another dependency's requirement.

## Example
```typescript
bad:  // manifest dependencies: { "web-client": "^2.1.0" }
      import { retry } from "retry-kit"; // reached only through web-client
      export const loadOrder = retry(fetchOrder);
good: // manifest dependencies: { "web-client": "^2.1.0", "retry-kit": "^4.0.0" }
      import { retry } from "retry-kit";
      export const loadOrder = retry(fetchOrder);
```

## Limits
The rule covers external packages: a standard-library module takes no manifest entry, and an import of the module's own files is no external dependency. A declaration in any of the manifest's dependency sections (runtime, development, optional, peer or bundled) counts as declared, and so does a declaration in a parent manifest the module inherits; whether development-only dependencies are used by non-development code is a separate check. Where the manifest format at the language version in use includes an entry for every module that provides any package transitively imported by the main module, a manifest that holds those entries meets the rule. Detectors that read imports and references statically miss runtime-only uses: reflection, configuration-driven class loading, or an import whose name comes from a variable.

## Validator
Grep the hunk for added import, require, use and module-path lines whose target is a bare package name or a module path rather than a relative path; drop standard-library modules and the module's own packages, and confirm the name is an external package rather than a path alias of the project. For each remaining package, open the manifest of the module that contains the file, and any parent or workspace manifest it inherits, and look for the package, or the module that provides it, in every dependency section; when it is absent, open the lock file or the resolved dependency tree to name the declared dependency that brings it in. Validator question: **Does the hunk import or reference an external package that neither the importing module's manifest nor a manifest it inherits declares in any dependency section?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: TOOL-01`, severity major, `file`, `symbol`, `code` = the import or reference line verbatim from the diff, `fix` = the manifest entry that declares the package with a version constraint, in the manifest's own format, `rationale` = names the package, the declared dependency that brings it in transitively, and the break or version drift that follows when that dependency changes or drops it).

## Source
- arXiv:2608.16262, DOI 10.1145/3832783.3837552 (ASE 2026; Maven Central libraries and GitHub modules), §3.1.1, §3.2.3, Finding 5, abstract, §1, §3.3, §3.2.1 (fetched): "6,761 versions (34.12%) contained at least one implicit dependency"; "Approximately 48% of implicit dependencies have introduced breaking changes due to version drift driven by the evolution of root projects, and 22% of them have their breaking entities actively used by the root projects"; "30.28% of implicit dependencies are affected by known vulnerabilities under the version-range convention SCA tools use for declared dependencies"; "Implicit dependencies, lacking user-specified versions, are automatically resolved by package managers based on the project context, making their versions volatile"; "many widely used SCA tools focus exclusively on direct dependencies"; "An implicit dependency, by contrast, is absent from the manifest and shifts with no signal that the dependency even exists, let alone changed"; "Even though an unpinned declared dependency drifts too, that drift is under the developer’s control, following an explicit choice not to pin the version"; "A dependency declared only in a parent POM is resolved to the same Level-1 position as an explicitly declared direct dependency"; "Dynamic analysis can, in principle, uncover runtime-only dependencies (e.g., reflection [3] or configuration-driven class loading)". Caveat: the numbers come from one ecosystem; the documents below state the mechanism for others.
- Apache Maven, Introduction to the Dependency Mechanism, §Transitive Dependencies (fetched): "it is a good practice to explicitly specify the dependencies your source code uses directly [...] it may cause build failure when project B suddenly updates/removes its dependency on project C."
- eslint-plugin-n, rule n/no-extraneous-import, in recommended-module and recommended-script (fetched): "the program may work locally but can break after dependencies are re-installed [...] Transitive dependencies should still be added as an explicit dependency in your `package.json` to avoid the risk of a dependency potentially changing or removing the transitive dependency."
- eslint-plugin-import, rule import/no-extraneous-dependencies (fetched): "Forbid the import of external modules that are not declared in the `package.json`'s `dependencies`, `devDependencies`, `optionalDependencies`, `peerDependencies`, or `bundledDependencies`."
- deptry, rules DEP003, DEP004, DEP005 and usage §Dynamic imports (fetched): "Package A should be explicitly added to your project's list of dependencies"; "Project should not use development dependencies in non-development code"; "Dependencies that are part of the Python standard library should not be defined as dependencies in your project"; "importlib.import_module(bar)  # Not detected".
- Semantic Versioning 2.0.0, FAQ on updating dependencies without changing the public API (fetched): "Software that explicitly depends on the same dependencies as your package should have their own dependency specifications and the author will notice any conflicts."
- The Go Modules Reference, §go directive, at go 1.17 or higher (fetched): "The `go.mod` file includes an explicit `require` directive for each module that provides any package transitively imported by a package or test in the main module."

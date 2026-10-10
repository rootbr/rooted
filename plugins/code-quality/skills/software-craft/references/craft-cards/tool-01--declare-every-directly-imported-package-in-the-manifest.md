---
title: Every package the code imports directly is declared in the ecosystem's manifest rather than reached through a transitive dependency
rule_id: TOOL-01
domain: tooling
step: [implement]
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

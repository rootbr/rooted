---
title: A change that removes the last use of a dependency also removes its declaration from the manifest
rule_id: TOOL-08
domain: tooling
step: [refactor, implement, review]
applies_to: [universal]
triggers: ['^\s*import\b', '^\s*from\s+[A-Za-z_][\w.]*\s+import\b', '\brequire\s*\(\s*["''][^./"'']', '\bimport\s*\(\s*["''][^./"'']', '^\s*(pub\s+)?use\s+[A-Za-z_]\w*::|^\s*extern\s+crate\b', '^\s*(import\s+)?(\w+\s+)?"[\w.-]+[.][a-z]{2,}/[\w./-]+"\s*$']
scope: callers
check_kind: semantic
severity_default: major
---

# A change that removes the last use of a dependency also removes its declaration from the manifest

## Thesis
When a change deletes or replaces the last code that uses a package, so that no source file, test, tool, build script, configuration file or platform-specific file of the project uses it any longer, the same change deletes the package's declaration as a direct dependency from the ecosystem's manifest, and the project still builds and passes its tests without it.

## Rationale
Removing the code that uses a dependency usually also requires removing the dependency from the build configuration, and that step can be missed; the build then keeps spending time on a dependency nothing uses. A dependency that is packaged with the application but not needed to build and run it grows the built binary and increases maintenance effort. The step is missed in practice: across the history of 435 projects of a single ecosystem, bloated dependencies steadily increased over time, and of the direct dependencies that became bloated, 8.8% did so when all the code that used them was removed and 6.9% when the code was updated to drop the use while the manifest still declared the dependency, so the study recommends checking the usage status of dependencies when removing code. Once bloated, a dependency stays so: 89.2% of the direct dependencies that were bloated remained bloated in all subsequent versions, which suggests that a bloated dependency can be removed safely. It also induces unnecessary maintenance: 22% of the dependency updates developers performed were made on bloated dependencies, and an automated update service suggested a similar ratio. Maintainers are willing to remove such dependencies when notified: in a study with 30 notable open-source projects, 21 of 26 answered pull requests that removed bloated dependencies were accepted and merged, removing 140 dependencies, 75 of them direct. Deleting the declaration together with its last use keeps the manifest matched to the source code, the state that dependency checkers test for and that a tidy command restores by removing requirements on modules that provide no relevant packages.

## Example
```rust
bad:  // Cargo.toml [dependencies] keeps itertools = "0.13"
      use std::collections::BTreeSet; // replaced use itertools::Itertools;
      fn distinct(items: &[u32]) -> BTreeSet<u32> { items.iter().copied().collect() }
good: // Cargo.toml [dependencies]: itertools deleted with its last use
      use std::collections::BTreeSet;
      fn distinct(items: &[u32]) -> BTreeSet<u32> { items.iter().copied().collect() }
```

## Limits
Usage detectors report false positives, so a package reported as unused is a candidate for removal, not a proof. Analysis at bytecode level misses uses that leave no trace in the bytecode, such as constants, annotations with source retention and documentation links, and a package whose only use is such a construct is reported as unused. A dependency declared for a whole package but used by only one of its build targets is reported as unused in a target that does not use it. A development dependency is usually meant to be used outside the codebase, in tests or as a command-line tool for type checking or formatting, so a check of source imports leaves development dependencies out. A package that another dependency still requires stays in the resolved graph: where the manifest lists every module that provides a transitively imported package, the tidy command keeps its requirement and marks it indirect, and where the resolver picks the nearest definition, a version declared in the project's own manifest is the one guaranteed, so deleting that declaration can change the version selected; the declaration then stays only as an indirect requirement or a version constraint. The removal is confirmed when the project builds and all its tests pass without the dependency. The rule reaches a change that also adds lines matching its triggers, such as the import of a replacement package; a change that only deletes code adds no line to match.

## Validator
Grep the hunk's deleted lines for an import, use or require line, or a path-qualified reference, that names an external package rather than a relative path, and its added lines for the import of a replacement. For each package whose import or reference the change deletes, search the whole project for a remaining use: sources, tests, tools, build scripts, configuration and platform-specific files. Open the ecosystem's manifest and check whether the change deletes that package's direct declaration, or keeps it only as an indirect requirement or version constraint when another dependency still requires the package; leave out development dependencies whose use lies in tests or tooling. Validator question: **Does the change delete the last use of a package while the ecosystem's manifest still declares it as a direct dependency?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: TOOL-08`, severity major, `file`, `symbol`, `code` = the deleted import line of the package, quoted verbatim from the diff, `fix` = the manifest with that package's direct declaration deleted, or kept only as an indirect requirement or version constraint when another dependency still requires the package, and the lock file regenerated, in the manifest's own syntax, `rationale` = the package, the last use the change removed, and the search that found no remaining source, test, tool, build-script, configuration or platform-specific use).

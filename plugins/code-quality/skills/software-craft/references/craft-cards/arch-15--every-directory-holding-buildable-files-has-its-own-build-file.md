---
title: In a build whose package is a directory with a build file that lists its targets' sources, every directory holding buildable files has a build file of its own
rule_id: ARCH-15
domain: architecture
step: [implement, refactor, review]
applies_to: [build-config]
triggers: ['\bsrcs\s*[=:]\s*\[[^\]]*["\x27][\w.-]+/[\w./-]+["\x27]', '\b(?:glob\s*\(\s*|include\s*=\s*)\[[^\]]*["\x27][^"\x27\]]*/', '^\s*["\x27][\w.*-]+/[\w./*-]+[.](java|kt|scala|go|py|ts|tsx|js|cc|cpp|c|h|hpp|rs|proto)["\x27]\s*,?\s*$']
scope: file
check_kind: mechanical
severity_default: minor
---

# In a build whose package is a directory with a build file that lists its targets' sources, every directory holding buildable files has a build file of its own

## Thesis
In a build system whose package is a directory containing a build file together with each subdirectory beneath it that holds no build file of its own, and whose build file declares targets that list, by name or by pattern, the source files they compile, every directory that contains buildable files should be a package of its own. A build file that refers to files in a subdirectory — by a source entry such as `a/b/File.ext`, or by a pattern that reaches into subdirectories — is a sign that a build file should be added to that subdirectory.

## Rationale
A package includes all files in its directory plus all subdirectories beneath it, except those that themselves contain a build file, and no file or directory may be part of two different packages. A subdirectory without a build file is therefore a directory belonging to its parent's package. The longer this structure exists, the more likely circular dependencies are inadvertently created, a target's scope creeps, and an increasing number of reverse dependencies have to be updated. A build file added to the subdirectory makes it a package of its own, whose files belong to no other package.

## Example
```typescript
bad:  // app/BUILD.ts
      tsLibrary({ name: "app", srcs: ["main.ts", "util/strings.ts",
          "util/numbers.ts",
          ...glob(["io/**/*.ts"]),
      ] });
good: // app/BUILD.ts
      tsLibrary({ name: "app", srcs: ["main.ts"], deps: ["//app/util", "//app/io"] });
      // app/util/BUILD.ts, and app/io/BUILD.ts alike
      tsLibrary({ name: "util", srcs: ["strings.ts", "numbers.ts"] });
```

## Limits
The rule reaches only a build system whose package is a directory containing a build file together with each subdirectory beneath it that holds no build file of its own, and whose build file declares targets that list the source files they compile. A build system that defines no such package is outside the condition although its build file also lists each target's sources. A manifest that defines one unit of release for a whole source tree, and leaves its sources to a documented layout of subdirectories without a manifest of their own, is outside the condition although its package is also a directory containing a build file. A subdirectory that contains no buildable files, such as a data directory, is outside the condition and may stay a directory belonging to its parent's package. A target is outside the condition when the compiler takes its sources as a single unit, starting from one root file and reaching every module file beneath it; module files in its subdirectories cannot be built as targets of their own.

## Validator
Confirm first that the build system makes a package of a directory containing a build file together with each subdirectory beneath it that holds no build file of its own, and that the build file declares targets listing their source files; a build system without such packages, or a manifest of a whole source tree, is outside the condition, and the check stops there. The check also stops where the entry or pattern lists the module files beneath one root file that the compiler takes as a single unit. Grep the build file's hunk for a source entry or a pattern that contains a path separator: a quoted path such as `dir/file.ext` in a source list, or a recursive pattern such as `**/`. Open the build file and name, for each such entry or pattern, the subdirectory it reaches into. Trace that subdirectory: check whether it contains buildable files and whether it holds a build file of its own. Validator question: **Does this build file refer to buildable files in a subdirectory that has no build file of its own?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: ARCH-15`, severity minor, `file`, `symbol`, `code` = the source entry or pattern that reaches into the subdirectory, verbatim from the diff, `fix` = a build file in that subdirectory declaring a target for its files and the parent target depending on that target, in the build file's language, `rationale` = a subdirectory holding buildable files belongs to its parent's package, and the structure invites inadvertent circular dependencies, target scope creep and a growing number of reverse dependencies to update).

## Source
- Bazel documentation, Best practices, § Packages — bazelbuild/bazel master `docs/configure/best-practices.mdx` (fetched): "Every directory that contains buildable files should be a package. If a `BUILD` file refers to files in subdirectories (such as, `srcs = ["a/b/C.java"]`) it's a sign that a `BUILD` file should be added to that subdirectory. The longer this structure exists, the more likely circular dependencies will be inadvertently created, a target's scope will creep, and an increasing number of reverse dependencies will have to be updated."
- Bazel documentation, Repositories, workspaces, packages, and targets — bazelbuild/bazel master `docs/concepts/build-ref.mdx` (fetched): "A package is defined as a directory containing a `BUILD` file named either `BUILD` or `BUILD.bazel`. A package includes all files in its directory, plus all subdirectories beneath it, except those which themselves contain a `BUILD` file. From this definition, no file or directory may be a part of two different packages." and "Note that `my/app/data` is not a package, but a directory belonging to package `my/app`." and "A package is a container of _targets_, which are defined in the package's `BUILD` file."
- Bazel documentation, BUILD style guide, § Recursive — bazelbuild/bazel master `docs/build/style-guide.mdx` (fetched): "Do not use recursive globs to match source files (for example, `glob(["**/*.java"])`). Recursive globs make `BUILD` files difficult to reason about because they skip subdirectories containing `BUILD` files." and "It is good practice to author a `BUILD` file in each directory and define a dependency graph between them."
- Bazel Rust rules, `rust_library` attributes — bazelbuild/rules_rust main `rust/private/rust.bzl` (fetched): "List of Rust `.rs` source files used to build the library. If `srcs` contains more than one file, then there must be a file either named `lib.rs`. Otherwise, `crate_root` must be set to the source file that is the root of the crate to be passed to rustc to build this crate." The same repository's `crate_universe/BUILD.bazel` (fetched) declares its `cargo_bazel` library with `srcs = glob(include = ["src/**/*.rs"], exclude = ["src/main.rs"])`.
- The Rust Programming Language, ch. 7.5 — rust-lang/book HEAD `src/ch07-05-separating-modules-into-different-files.md` (fetched): "For a module named `hosting` that is a submodule of `front_of_house`, the compiler will look for the module’s code in:" followed by "_src/front_of_house/hosting.rs_ (what we covered)".
- Caveat: the three Bazel pages document one build system; the rule carries to another only where that system defines a package the same way and its build files list each target's source files.

---
title: A library published for others to depend on declares compatible version ranges, with no exact pin and no upper cap below a version known to be incompatible
rule_id: TOOL-04
domain: tooling
step: [implement]
applies_to: [library, build-config]
triggers: ['(?:^\s*["'']?|["''])[A-Za-z][\w.\[\],-]*\s*==\s*\d', '=\s*["'']=\s*\d', '^\s*"[@\w./-]+"\s*:\s*"\d+[.]\d+[.]\d+"', '["'']~\s*\d|~=\s*\d+(?:[.]\d+){2}', ',\s*<\s*\d|["'']\s*>=?\s*\d[\w.-]*\s+<=?\s*\d', '\[\d+(?:[.][\w-]+)+\]|\d[.][*+xX]["'']', '["'':>][\[(][\w.-]*,\s*\d[\w.-]*[)\]]']
scope: file
check_kind: semantic
severity_default: major
---

# A library published for others to depend on declares compatible version ranges, with no exact pin and no upper cap below a version known to be incompatible

## Thesis
In the manifest of a package that other projects depend on, each runtime requirement admits more than one version. Its upper bound, where it has one, sits no lower than the next release the versioning scheme marks incompatible, unless a version is known to break the package.

## Rationale
An exact version in a package that others depend on greatly complicates the deployment of security fixes and prevents its users from gaining the benefit of dependency upgrades. Where the resolver settles on one version of the package within a compatible range, an upper bound below the next incompatible release fails when another package in the same dependency tree requires a newer version, leading to an unresolvable error; where requirements are hard, the build fails when no version satisfies all of them. Specifications that are too tight risk version lock, the inability to upgrade a package without releasing new versions of every dependent package, while specifications that are too loose assume compatibility with more future versions than is reasonable. A range enables flexibility in resolution that can prevent different versions of the same package being included and facilitates the automated deployment of bug fixes. In simulations of dependency resolution over historical time points in one package ecosystem, pinning direct dependencies increased the cost of maintaining vulnerable and outdated dependencies. The exact version is intended primarily for repeatable deployments of applications, and controlling a version in the lock file may be more appropriate than capping it in the manifest.

## Example
```java
bad:  DependencyHandler deps = project.getDependencies();
      deps.add("api", "com.example:json:[2.4.1]");
      deps.add("api", "com.example:codec:[1.3,1.4)");
good: DependencyHandler deps = project.getDependencies();
      deps.add("api", "com.example:json:[2.4.1,3.0)");
      deps.add("api", "com.example:codec:[1.3,2.0)");
```

## Limits
The separating condition is whether other projects resolve against the manifest. An application or binary that no one else depends on may pin: an exact version requirement is intended primarily for repeatable deployments of applications, a tight upper bound may not matter when no one else depends on the package, for example when it only builds a binary, and a supply-chain scorecard asks a project producing an application to declare all its dependencies with specific versions and to check in its lock file. That side rests on predictability: a fixed version gives runtime behaviour that is easier to predict, and developers struggle to find the sweet spot between that predictability and the agility of flexible versions. A library that keeps ranges for its runtime requirements may pin its development-only ones. A fully specified version may be warranted for a pre-release dependency, to avoid its breaking changes, and for a library that re-exports a code-generating macro whose generated code calls into the re-exporting library, so that the macro is never newer than the library. A cap below the next incompatible release makes sense when a version is known to break the package, and a requirement may exclude a single version, for example because it has a critical vulnerability. One dependency-update tool's documentation lets a library for a runtime where duplicate copies are less of a concern consider pinning all its dependencies; simulations in that same ecosystem found that pinning direct dependencies increased the cost of maintaining vulnerable and outdated dependencies.

## Validator
Grep the hunk for requirement lines of a dependency manifest that carry an equality operator before a version, a bare full version the ecosystem reads as exact, a single-version bracket, a bracketed interval with an upper end, a tilde, a minor-level wildcard or a '<' bound. Open the manifest at file scope and establish whether the package is published for others to depend on (a library target, publication metadata) or only builds an application or binary. For each matched runtime requirement of a published package, decide whether it admits one version only or caps its range below the next release the versioning scheme marks incompatible; skip development-only requirements, a pre-release pin, an exact version that a comment ties to a re-exported code-generating macro, and a cap or exclusion that a comment or linked issue ties to a known break or vulnerability. Validator question: **Does a runtime requirement of a package published for others to depend on admit exactly one version, or cap its range below the next incompatible release with no known break recorded behind the cap?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: TOOL-04`, severity major, `file`, `symbol`, `code` = the requirement line verbatim from the diff, `fix` = the same requirement rewritten as a range from the lowest supported version up to the next incompatible release, in the manifest's own syntax, `rationale` = names that the package's users resolve against this requirement and that the exact version or tight cap blocks their security fixes and upgrades and can leave their dependency tree unresolvable).

---
title: A change that moves a dependency whose types or traits appear in a published library's public API to a version incompatible with the one it replaces is released as a breaking change of the library
rule_id: ARCH-22
domain: architecture
step: [implement, review]
applies_to: [library, public-api, build-config]
triggers: ['^\s*[\w-]+\s*=\s*(\{[^}]*\bversion\s*=\s*)?[''"][\^~=<>]*\d', '^\s*"(@[\w.-]+/)?[\w.-]+"\s*:\s*"[\^~>=<]*\d', '^\s*(require\s+)?[\w.-]+[.][\w.-]+(/[\w.-]+)+\s+v\d', '<version>[^<]*</version>|^\s*(api|implementation)\s*[(]?\s*[''"][\w.-]+:[\w.-]+:[\w.${}-]+[''"]', '^\s*[''"]?[\w.-]+(\[[\w,]+\])?\s*(==|>=|~=|\^|<)\s*\d']
scope: base-compare
check_kind: semantic
severity_default: major
---

# A change that moves a dependency whose types or traits appear in a published library's public API to a version incompatible with the one it replaces is released as a breaking change of the library

## Thesis
A dependency whose types or traits appear in a published library's public API, in parameters, return values, trait or interface implementations, supertypes or public fields, is a public dependency, and a change to it changes the library's contract with its consumers. A change that moves a public dependency to a version incompatible with the one it replaces is a breaking change of the library itself. The library releases such a change under a version that marks it as incompatible with the previous release: by the package manager's compatibility rule where the package manager states one, and otherwise by a raised left-most non-zero component of the library's version.

## Rationale
A public dependency is part of what consumers compile against: a dependency exposed in the library's API reaches the consumers' compile path. Some package managers resolve every user of a shared dependency to one version within a compatibility range and build a separate copy of the dependency for each incompatible version. Under such a package manager, when the library moves its public dependency to an incompatible version while the consumer's own code still requires the old one, the dependency resolves to a different version for each usage. A compiler that identifies a type by the copy that declares it then considers the types of the two copies different even where they carry the same name, so where values from the two copies need to be used together they do not match, and the consumer's code refuses to compile with unclear messages. A package manager that keeps a single copy of each package makes everything that depends on the shared dependency agree on one version, so the consumer either moves to the new version, whether it wants to or not, or keeps a version the library was not built for, or meets a resolution error. A package manager with compatibility ranges assumes an update within a range is safe and keeps a requirement inside its range, so a release marked incompatible is not pulled into a consumer's build by an update. Breaking changes shipped in non-major releases do reach dependents: in one package ecosystem, around 12% of the dependent packages and 14% of their releases were impacted by a breaking change during updates of non-major releases of their dependencies, and of all the manifesting breaking changes, 44% were introduced both in minor and patch releases, which in principle should be backward compatible.

## Example
```rust
bad:  // Cargo.toml: geo "0.7" -> "0.8", crate version 1.4.0 -> 1.5.0
      version = "1.5.0"
      geo = "0.8"
      pub fn area(shape: &geo::Polygon<f64>) -> f64 { ... }
good: // Cargo.toml: geo "0.7" -> "0.8", crate version 1.4.0 -> 2.0.0
      version = "2.0.0"
      geo = "0.8"
      pub fn area(shape: &geo::Polygon<f64>) -> f64 { ... }
```

## Limits
The requirement holds for public dependencies only. Updating a private dependency leaves the library's public API unchanged and is a compatible change; a consumer that uses the same dependency declares its own requirement and notices any conflict there. Where the package manager builds a copy per incompatible version, a private dependency can also be duplicated freely in the dependency graph without causing compilation errors. A type of a private dependency that the library exports as its own still exposes that dependency: the type cannot be forced to be distinct, and its users might accidentally start depending on that type being compatible once they depend on the package that actually implements it. Under a package manager that admits no two versions within one compatibility range, a move inside that range builds no second copy and stays compatible; the finding covers the move across ranges. Whether a dependency is public follows from what a consumer's compiler needs to compile against the library, which can be broader than the types the author considers part of the public API.

## Validator
Grep the hunk for a changed dependency requirement in a build manifest. Confirm that the library is published under a version for others to depend on. Open the manifest at base and at head and decide whether the new requirement still admits a version compatible with the old one, by the package manager's compatibility rule where it states one and otherwise by whether the left-most non-zero component of the required version changed, since a soft requirement that the package manager may replace by any version states no compatibility; where it does not, trace whether any type or trait of that dependency appears in the library's public API at base and still at head, counting parameters, return values, trait or interface implementations, supertypes, public fields, annotations and re-exports, and counting what a consumer's compiler needs rather than only what the author calls public. Then compare the library's own version, or the release entry its changelog keeps for the next release, at base and at head; where head leaves both untouched, the change is not yet labelled and the answer is no. Validator question: **Does the change move a public dependency to an incompatible version while the library version or release entry it records at head marks the release as compatible with base?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: ARCH-22`, severity major, `file`, `symbol`, `code` = the changed requirement line and the line that records the release, the library's version line or the changelog's release entry, quoted verbatim from the diff, `fix` = that record raised to the next release that the rule in the Thesis marks as incompatible, in the record's own syntax, `rationale` = names the public dependency, its old and new requirement, the public item that exposes it, and the conflict a consumer that also uses the dependency would meet under the package manager's resolution: two copies whose types do not match, or one version that the consumer or the library was not built for).

---
title: A component released at version 1.0.0 or later uses in its public API no type or trait from a dependency at a 0.y.z or pre-release version
rule_id: ARCH-09
domain: architecture
step: [design, implement, review]
applies_to: [library, public-api, build-config]
triggers: ['(=|[''"]\s*:)\s*[''"][\^~=]?0[.]\d+|\sv0[.]\d+[.]\d+|<version>0[.]\d+|:[\^~]?0[.]\d+([.]\d+)*[''"]|\d-(?i:alpha|beta|rc|pre|preview|snapshot)\b', '^\s*(export|pub|public)\b|^\s*impl\b.*\bfor\b|^(func|type)\s+(\([^)]*\)\s*)?[A-Z]|^\s*(async\s+)?def\s+[A-Za-z]', '^\s*(import|use|from)\s']
scope: callers
check_kind: semantic
severity_default: major
---

# A component released at version 1.0.0 or later uses in its public API no type or trait from a dependency at a 0.y.z or pre-release version

## Thesis
A component versioned under semantic versioning and released at 1.0.0 or later, without a pre-release label, uses in its public API types and traits only from dependencies that are themselves released at 1.0.0 or later without a pre-release label. A dependency is public when a type or trait from it appears in that API, such as a parameter or return type, a public field, a re-export, or a trait or conversion implementation on a public type. A dependency used only behind private types is outside the rule, whatever its version.

## Rationale
Under semantic versioning, version 1.0.0 defines a component's public API, and every later version number is incremented according to that API and how it changes. A type or trait taken from a dependency and exported through that API makes the dependency public, so bumping the dependency's version is a breaking change of the component itself. A dependency at 0.y.z is in initial development: its public API should not be considered stable, it makes no stability or backward-compatibility guarantees, and its own 1.x releases are allowed to break code written against its 0.y.z releases. A pre-release version likewise indicates that the version is unstable and might not satisfy the intended compatibility requirements of its normal version. A component that exposes such a type cannot be stable, because a component is stable only when all of its public dependencies are stable. Keeping the dependency behind private types, or moving to a release of it at 1.0.0 or later, restores that condition.

## Example
```typescript
bad:  // library released at 1.2.0; package.json has "dep": "^0.4.1"
      import { Thing } from "dep";
      export function load(input: Thing): Report { ... }
good: import { parse } from "dep";
      export interface Input { readonly text: string }
      export function load(input: Input): Report {
        const thing = parse(input.text); ...
      }
```

## Limits
A component at 0.y.z or at a pre-release version, and an application that publishes no API for others to depend on, such as a CLI or GUI component, promise no stability and carry no obligation. A dependency kept behind private types puts none of its types or traits into the component's public API and stays outside the rule at any version. The rule is contested where stability is read from a module's position in the dependency graph. One side checks that a module depends in the direction of stability, flagging a dependency whose instability, dependencies / (dependents + dependencies), is higher than that of the module depending on it. The other side holds that a 100% unstable module, such as a CLI or GUI component that only depends on other modules, is not bad, and that depending on a package not expected to change is no cause for concern. The condition that separates the cases is the declared promise, not the graph position: the rule binds a component that declares a stable API at 1.0.0 or later and exposes a dependency that declares none, and an instability value computed from dependency counts alone is not a finding under this rule.

## Validator
Grep the hunk for a dependency version at 0.y.z or with a pre-release label in a build manifest, and for an import or an exported declaration that names a type from such a dependency. Read the component's own version from its manifest or, where the manifest carries none, from its latest release tag, and each dependency's version from the manifest: when the component is not versioned under semantic versioning, when its version is below 1.0.0 or carries a pre-release label, or when it is an application that publishes no API for others to depend on, stop. For each dependency at 0.y.z or at a pre-release version, trace its types and traits into the component's exported declarations — parameter and return types, exported types and aliases, re-exports, implementations of its traits or interfaces on exported types, conversions to or from its types — and drop the uses confined to private types and routine bodies. Validator question: **Does an exported declaration of a component released at 1.0.0 or later, without a pre-release label, put a type or trait from a dependency at 0.y.z or at a pre-release version into the component's public API?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: ARCH-09`, severity major, `file`, `symbol`, `code` = the line of the diff that puts the dependency's type into the public API — the exported declaration, or the manifest line carrying the dependency's version when the hunk changes that line — verbatim from the diff, `fix` = the declaration rewritten over the component's own type with the dependency used only inside the implementation, or the manifest line moved to a release of the dependency at 1.0.0 or later, in the file's language, `rationale` = names the dependency and its version and that bumping it is a breaking change of the component's own public API).

## Source
- Rust API Guidelines, § "Public dependencies of a stable crate are stable (C-STABLE)", https://raw.githubusercontent.com/rust-lang/api-guidelines/master/src/necessities.md (fetched): "A crate cannot be stable (>=1.0.0) without all of its public dependencies being stable. Public dependencies are crates from which types are used in the public API of the current crate." … "// Should be okay even if other_crate isn't // stable, because ErrorImpl is private." … "// Oh no! This puts other_crate into the public API // of the current crate. impl From<other_crate::Error> for Error {"
- Rust RFC 1977 "public_private_dependencies", § Motivation, https://raw.githubusercontent.com/rust-lang/rfcs/master/text/1977-public-private-dependencies.md (fetched): "A dependency is public if some of the types or traits of that dependency are themselves exported through the public API of main crate. The most common places where this happens are return values and function parameters. The same applies to trait implementations and many other things." … "if you bump a public dependency's version, it's a breaking change of your *own* crate." … "a private dependency is contained within your crate and effectively invisible for users of your crate."
- Semantic Versioning 2.0.0, items 1, 4, 5 and 9, https://raw.githubusercontent.com/semver/semver/master/semver.md (fetched): "Software using Semantic Versioning MUST declare a public API." … "Major version zero (0.y.z) is for initial development." … "The public API SHOULD NOT be considered stable." … "Version 1.0.0 defines the public API. The way in which the version number is incremented after this release is dependent on this public API and how it changes." … "A pre-release version indicates that the version is unstable and might not satisfy the intended compatibility requirements as denoted by its associated normal version."
- Go documentation, "Module version numbering", § "v0 number" and § "Major version", https://raw.githubusercontent.com/golang/website/master/_content/doc/modules/version-numbers.md (fetched): "Though a v0 version can be used in production, it makes no stability or backward compatibility guarantees. In addition, versions v1 and later are allowed to break backward compatibility for code using the v0 versions." … "A v1 or above version number signals that the module is stable for use (with exceptions for its pre-release versions)."
- rustc lint `exported_private_dependencies`, compiler/rustc_lint_defs/src/builtin.rs, https://raw.githubusercontent.com/rust-lang/rust/master/compiler/rustc_lint_defs/src/builtin.rs (fetched): "public interface leaks type from a private dependency" … "To fix this, avoid exposing the dependency in your public interface."
- dependency-cruiser rules reference, § moreUnstable, https://raw.githubusercontent.com/sverweij/dependency-cruiser/main/doc/rules-reference.md (fetched): "moreUnstable matches for any dependency that has a higher Instability than the module that depends on it." … "depend in the direction of stability" … the formula, as rendered: "Instability = #dependencies / (#dependents + #dependencies)" … "a module with no dependents, but with one or more dependencies is 100% Instable." … "it's not 'bad' to be a 100% Instable module - it's only the nature of the module. A CLI or GUI component typically only depends on other modules and is 100% Instable. This is not a bad thing." … "Making changes to a 100% Instable module will have consequences for itself only."
- JDepend documentation, § Volatility, https://raw.githubusercontent.com/clarkware/jdepend/master/docs/JDepend.html (fetched): "Packages that are not expected to change can be specifically configured with a volatility (V) value" … "If V=0, meaning the package is not at all subject to change, then the package will automatically fall directly on the main sequence (D=0)." … "Creating dependencies on it is not cause for concern."
- Caveat: the public-dependency rule and its lint are stated for one ecosystem's packages; the semantic-versioning and module-versioning texts carry the version semantics the rule generalizes on.

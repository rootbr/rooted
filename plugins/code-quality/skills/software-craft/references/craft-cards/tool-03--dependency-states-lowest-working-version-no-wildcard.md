---
title: A declared dependency states the lowest version the code works with and never accepts every version through a wildcard
rule_id: TOOL-03
domain: tooling
step: [implement]
applies_to: [build-config]
triggers: ['[\w-]+\s*=\s*["\x27]\*["\x27]', '"[@\w./-]+"\s*:\s*"(\*|latest|x|X|)"', 'latest[.](release|integration)|["\x27][\w.-]+:[\w.-]+:\+["\x27]', '>=\s*0([.]0)*\s*(["\x27,;]|$)', '^\s*["\x27][A-Za-z0-9][\w.-]*(\[[\w,.-]+\])?["\x27]\s*,?\s*$|dependencies\s*=\s*\[(.*,)?\s*["\x27][A-Za-z0-9][\w.-]*(\[[\w,.-]+\])?["\x27]\s*[,\]]']
scope: callers
check_kind: mechanical
severity_default: major
---

# A declared dependency states the lowest version the code works with and never accepts every version through a wildcard

## Thesis
Each dependency the ecosystem's manifest declares carries a version requirement whose lower bound is the lowest version the code works with; a range as general as every release of one major version meets the rule once that bound is right. A wildcard, an empty requirement, a name with no version constraint, a lower bound of zero, or a tag or dynamic selector that resolves to whichever release is published under it or is newest states no such bound and is replaced by a requirement that does. When the code starts depending on a feature added only in a later release, the lower bound rises to that release.

## Rationale
A wildcard says the code will work with every version ever, which is never going to be true: it is the range from 0.0.0 upward, and it matches any version. It is highly unlikely that code works with every possible version of a dependency, and wildcard requirements would cause unnecessary breakage across the ecosystem; one ecosystem's central registry rejects every package, not just libraries, that declares one. Lower bounds are not critical in the happy path but are important when dependencies conflict: with no lower bound, a resolver that searches back through versions to settle a conflict can, and often will, backtrack to the oldest version of a package; that old version often fails to build, or the resolver can end up picking a version old enough that it does not depend on the conflicting package but also does not work with the code. They are particularly critical in a library, where a user may otherwise receive an old, incompatible version of one of the library's dependencies and the library fails with an unexpected error. A requirement specified too loosely assumes compatibility with more future versions than is reasonable. The bound is correct only while it reflects the minimum versions the code actually uses — a declared 1.0.0 is wrong once the code depends on features added only in 1.5.0 — and a continuous-integration run that resolves direct dependencies to the minimum versions the requirements allow checks that. Missing bounds in one package also limit a check run by the packages that depend on it: enforcing minimal versions for all transitive dependencies is of limited use because not all external dependencies declare proper lower version bounds.

## Example
```rust
bad:  // Cargo.toml:     some_crate = "*"
      // package.json:   "some-pkg": "latest"
      // build.gradle:   implementation 'org.example:some-lib:+'
      // pyproject.toml: dependencies = ["some-pkg>=0", "other-pkg"]
      let value = some_crate::parse_strict(input)?; // API added in 1.4.0
good: // Cargo.toml:     some_crate = "1.4"
      let value = some_crate::parse_strict(input)?; // API added in 1.4.0
```

## Limits
A range that admits every later compatible release meets the rule once its lower bound is right; narrowing a requirement tighter than needed risks version lock, the inability to upgrade a package without releasing new versions of every dependent package. In an ecosystem whose requirement directive always names one version and declares it the minimum required version, every declaration carries a lower bound by construction, and the rule there reaches only whether that minimum still covers the features the code depends on. A dependency taken only from a version-control repository, a URL or a local path, with no registry version, is outside the rule, as it is outside the reference wildcard lint, which checks only registry-sourced entries; an entry that pairs such a location with a registry version is checked on that version, which the published package carries; an entry whose requirement is declared elsewhere — inherited from a workspace root, or managed by a platform, a bill of materials, a dependency constraint or a constraints file — is checked where that requirement is declared.

## Validator
Grep the manifest hunk for each dependency entry the change adds or edits, and read its version requirement: a wildcard, an empty string, a name with no version constraint, a lower bound of zero, a distribution tag such as `latest`, or a dynamic latest-release selector states no lower bound. Skip an entry whose only source is a version-control repository, a URL or a local path, check the version of an entry that pairs such a location with a registry version, and read an entry whose requirement is declared elsewhere — a workspace root, a platform or bill of materials, a dependency constraint or a constraints file — at that declaration; a name with no version constraint states no lower bound only when no such declaration governs it. Where the diff itself shows that newly added code calls an API introduced in a later release than the entry's lower bound (a comment, a changelog line, a raised minimum in a sibling manifest), compare the two versions. Validator question: **Does a dependency entry the change adds or edits carry a requirement with no lower bound above zero, or a lower bound below a release the diff shows the new code needs?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: TOOL-03`, severity major, `file`, `symbol`, `code` = the dependency entry quoted verbatim from the manifest hunk, `fix` = the same entry with a requirement whose lower bound is the lowest version the code works with, in the manifest's syntax, `rationale` = names the requirement form that states no lower bound, or the release the new code needs).

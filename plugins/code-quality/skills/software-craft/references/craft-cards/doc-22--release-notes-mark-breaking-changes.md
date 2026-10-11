---
title: A changelog or release-note entry for a change that removes or incompatibly alters existing behaviour marks it as breaking
rule_id: DOC-22
domain: docs
step: [document]
applies_to: [public-api, library]
triggers: ['(?i)^\s*#{2,3}\s*\[?v?\d+[.]\d+([.]\d+)?', '(?i)^\s*#{2,4}\s*(removed|changed|deprecated|breaking( changes)?)\s*$', '(?i)^\s*[-*]\s*(remove[sd]?|rename[sd]?|move[sd]?|drop(ped|s)?|no longer)\b']
scope: file
check_kind: semantic
severity_default: minor
---

# A changelog or release-note entry for a change that removes or incompatibly alters existing behaviour marks it as breaking

## Thesis
A changelog or release-note entry that records a breaking change — renaming, moving or removing a public item, a non-trivial change to an item's signature, or another backwards incompatible change to the public interface or documented functionality — clearly identifies that change as breaking, with a heading, a label or the project's own marker.

## Rationale
Users of a package can read the release notes to find a summary of what changed in each published release, and breaking changes are the entries meant to be clearly identified there. Every major change is breaking: renaming, moving or removing any public item is a major change, so is any non-trivial change to an item's signature, and so is a backwards incompatible change to a module's public interface or documented functionality, such as removing a package. Downstream code cannot be annotated in advance to avoid the breakage a rename causes, and that breakage cannot be kept from affecting dependencies. Security releases may contain breaking changes too: a security release should be well documented and require minimal migration effort to facilitate fast adoption by its clients, yet across 4,377 security advisories in seven package ecosystems, 13.2% of the security releases indicated backward incompatibility through semantic versioning, while 6.4% mentioned breaking changes in their release notes; the two figures are separate measures.

## Example
```go
bad:  const notes = `
      ## v2.0.0
      ### Changed
      - Removed Client.Retry; set Options.Retries`
good: const notes = `
      ## v2.0.0
      ### Breaking changes
      - Removed Client.Retry; set Options.Retries`
```

## Limits
An entry for a backwards compatible change needs no marker: such a change increments the minor version. A deprecation entry is not a break, since marking public API functionality as deprecated increments the minor version; the later entry that removes the item is a break. A version number does not stand in for the marker: the guidance asks that the breaking changes themselves be clearly identified in the release notes, and v0 versions are unstable and have no compatibility guarantee. The guidance names no form, so the project's documented convention — a section heading, a bold label, a breaking-change token in a log generated from commits — meets the rule. The rule covers the notes; a deprecation notice inside the code is outside it.

## Validator
Grep the hunk for added changelog and release-note lines: a version heading; a Removed, Changed, Deprecated or Breaking heading; or list entries that begin with remove, rename, move, drop or no longer. For each added entry that records the removal, rename or move of an item, a non-trivial signature change or an incompatible change of documented behaviour, read the surrounding hunk to decide whether the item is public — exported, published or documented — and skip entries for private items, deprecations and compatible additions or fixes. Then open the file, find the section heading and the release heading the entry sits under, which can lie outside the hunk, and look for a breaking marker on the entry itself, on that section heading or on that release heading: a heading or label that says breaking, a breaking-change token, a `!` after the commit type, a section heading that names removals, such as Removed, or the marker the file's other releases use. Validator question: **Does an added changelog or release-note entry record a removal, rename, signature change or incompatible behaviour change of a public item with no marker on the entry, its section or its release that identifies it as breaking?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: DOC-22`, severity minor, `file`, `symbol` = the release heading the entry sits under, `code` = the unmarked entry line verbatim, `fix` = the same entry under the project's breaking marker — a breaking-changes heading or a breaking label — in the file's format, `rationale` = names the public item removed, renamed or changed and that readers of the notes find breaking changes by their marker).

## Source
- Rust API Guidelines, C-RELNOTES, `rust-lang/api-guidelines` `src/documentation.md` (fetched): "Users of the crate can read the release notes to find a summary of what changed in each published release of the crate." · "Breaking changes (as defined in [RFC 1105]) should be clearly identified in the release notes."
- Rust RFC 1105, API evolution, `rust-lang/rfcs` `text/1105-api-evolution.md` (fetched): "Breaking change: a change that, strictly speaking, can cause downstream code to fail to compile." · "all major changes are breaking, but not all breaking changes are major." · "Major change: renaming/moving/removing any public items." · "Major change: any non-trivial change to item signatures." · "it's not possible to annotate code in advance to avoid the breakage, nor is it possible to prevent the breakage from affecting dependencies."
- Go Modules Reference, `golang/website` `_content/ref/mod.md`, Versions and Major version suffixes (fetched): "The major version must be incremented and the minor and patch versions must be set to zero after a backwards incompatible change is made to the module's public interface or documented functionality, for example, after a package is removed." · "The minor version must be incremented and the patch version set to zero after a backwards compatible change" · "v0 versions are unstable and have no compatibility guarantee"
- Semantic Versioning 2.0.0, `semver/semver` `semver.md`, item on the minor version (fetched): "It MUST be incremented if any public API functionality is marked as deprecated."
- DOI 10.1109/TSE.2022.3181010, IEEE TSE 2022, abstract (fetched from `neverworkintheory/neverworkintheory.github.io` `tex/todo.bib`): "The security release should be well-documented and require minimal migration effort to facilitate fast adoption by the clients." · "over a dataset of 4,377 security advisories across seven package ecosystems" · "security releases may contain breaking change(s) as 13.2\% indicated backward incompatibility through semantic versioning, while 6.4\% mentioned breaking change(s) in the release notes."
- Caveat: the requirement to identify breaking changes rests on a published guideline, not a measured effect; the study covers security releases only, and its two figures are separate measures, not the share of breaking releases left unmarked.

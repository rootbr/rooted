---
title: A relative link that a change adds to a document, or whose target the change moves or deletes, points to an existing file and heading
rule_id: DOC-21
domain: docs
step: [document, refactor, review]
applies_to: [universal]
triggers: ['\]\((?!https?:|mailto:)[^)\s]+(\s+"[^"]*")?\)', '(?i)\b(href|src)\s*=\s*["''](?!https?:|mailto:|#|data:)[^"'']+["'']']
scope: callers
check_kind: mechanical
severity_default: minor
---

# A relative link that a change adds to a document, or whose target the change moves or deletes, points to an existing file and heading

## Thesis
A relative link that a change adds to a document, and every relative link or cross-reference in the repository's documents or source comments whose target file or heading the change moves, renames or deletes, resolves in the changed tree: its path names an existing file, and its fragment, when it has one, matches a heading or an explicit anchor of that file.

## Rationale
In a taxonomy of documentation issues mined from issue trackers, pull requests, mailing lists and a question-and-answer site, broken links were 29 of the 37 outdated or obsolete references among 190 up-to-dateness issues. In a survey, 64% of practitioners indicated outdated or obsolete references as an important documentation issue. Tools perform the lookup: a lint rule, enabled by default, is triggered when a link fragment matches none of the fragments generated for the headings in a document; a link checker checks that links point to existing local files and headings in the repository, links to headings in other documents included; a documentation generator in its nitpicky mode warns about all references whose target cannot be found.

## Example
```typescript
bad:  // this change moves docs/setup.md to docs/install.md, fixes README's link
      /** Options are listed in [setup](../docs/setup.md#options). */
      export interface Options { verbose?: boolean }
      /** Defaults: <a href="../docs/setup.md#defaults">setup</a>. */
      export const defaults: Options = { verbose: false };
good: /** Options are listed in [setup](../docs/install.md#options). */
      export interface Options { verbose?: boolean }
      /** Defaults: <a href="../docs/install.md#defaults">setup</a>. */
      export const defaults: Options = { verbose: false };
```

## Limits
An external URL is outside the rule: the link checker does not check external URLs, and the lookups resolve local files and headings in the repository. A fragment that names an explicit anchor, an element with an id attribute or an a tag with a name attribute, resolves as a heading's fragment does. A target the project lists in its checker's ignore configuration, a fragment pattern for the lint rule or a warning-type and target pair for the generator's nitpicky mode, is a documented tolerance. A change that only moves, renames or deletes a file or a heading adds no link line, so a check that starts from added lines does not reach the links it leaves stale.

## Validator
Grep the hunk for relative links and cross-references in documents and for files or headings the change moves, renames or deletes. For each added relative link, resolve its path against the directory of the file that holds it and look the file up in the changed tree; when it carries a fragment, derive the fragments of the target's headings and explicit anchors with the rendering platform's heading algorithm and look the fragment up. For each moved, renamed or deleted file or heading, search the repository's documents and source comments at the callers scope for relative links to its old path or old fragment. Validator question: **Does a relative link that the change adds to a document, or a relative link or cross-reference that points to a file or heading the change moves, renames or deletes, name a path with no file in the changed tree, a fragment that matches no heading or anchor of its target, or a target that does not exist?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: DOC-21`, severity minor, `file`, `symbol`, `code` = the link or cross-reference verbatim from the file that holds it, `fix` = the link pointed at the target's current path and heading, or, when the change deletes the target and leaves no successor, the link removed, in the markup of the file that holds it, `rationale` = the file, heading or target the link names and the tree lacks).

## Source
- DOI 10.1109/ICSE.2019.00122 (ICSE 2019), replication package figure taxonomy-more-numbers.png, Information Content (What) > Up-to-dateness (fetched): "Up-to-dateness 190 [...] Outdated/Obsolete references 37 [...] Broken link 29" (transcribed from the figure).
- DOI 10.1145/3377811.3380405 (ICSE 2020), Figure 2, Up-to-dateness (fetched): "Outdated/Obsolete references 64%"; legend: "“% important” reports the percentage of surveyed practitioners that indicated the related issue as an important one."
- markdownlint rule MD051 link-fragments, doc/md051.md and README 'Configuration' (fetched): "This rule is triggered when a link fragment does not match any of the fragments that are automatically generated for headings in a document"; "any HTML tag with an `id` attribute or an `a` tag with a `name` attribute can be used to define a fragment"; `ignored_pattern`: "Pattern for ignoring additional fragments"; "All rules are enabled by default."
- remark-validate-links, readme.md (fetched): "check that markdown links and images point to existing local files and headings in a Git repo"; "Links to headings in other markdown documents (`examples/foo.md#hello`) and links to files (`license` or `index.js`) are also checked."; "This plugin does not check external URLs".
- Sphinx, doc/usage/configuration.rst, confvals nitpicky and nitpick_ignore (fetched): "In nitpicky mode, Sphinx will warn about *all* references where the target cannot be found."; "tuples that should be ignored when generating warnings".
- Caveat: the taxonomy counts broken links without separating repository-relative links from external URLs, so its numbers size the issue class rather than the relative-link share.

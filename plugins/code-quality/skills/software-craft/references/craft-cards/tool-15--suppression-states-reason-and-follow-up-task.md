---
title: Every suppression a change adds states why the check is ignored at that site, and a temporary one names its follow-up task
rule_id: TOOL-15
domain: tooling
step: [implement, document, review]
applies_to: [universal]
triggers: ['#!?\[(?:allow|expect)\((?![^)]*reason\s*=)', 'eslint-disable[\w-]*(?:(?!--).)*$', '@ts-(?:expect-error|ignore)\s*$', '@SuppressWarnings\(', '#\s*(?:noqa|type:\s*ignore|pyright:\s*ignore|pylint:\s*disable)', '//\s*nolint(?::[\w,-]+)?\s*$']
scope: hunk
check_kind: mechanical
severity_default: minor
---

# Every suppression a change adds states why the check is ignored at that site, and a temporary one names its follow-up task

## Thesis
Each suppression a change adds or edits (an attribute, annotation or directive comment that silences a check of the compiler, the type checker or the project's configured analyzer) carries a reason that describes why the check should be ignored at that specific site. The reason sits where the language's suppression mechanism provides for it: a reason parameter, a description following the directive, or a comment on the directive's line or directly above it. A suppression added as a temporary measure to address a pressing issue also names the follow-up task or issue that addresses the underlying problem. A symbolic rule name that already makes the reason clear counts as the reason.

## Rationale
A suppression records a decision that a check is not applicable at one site. Its reason acts as documentation for other people reading the code, the author included later; it helps readers understand the reasoning and may allow the suppression to be removed once its purpose is obsolete. Code review can help identify the reasons behind suppressions and ensure that they are used appropriately. The decision is worth storing directly with the suppression it affects. Suppressions written at the site are easy to search for and revisit. For a temporary suppression, the follow-up task ensures the suppression is revisited and resolved at a later stage, and a reference to that task at the site, ideally a tracked issue, points later readers to its context and follow-up.

## Example
```rust
bad:  #[allow(clippy::cast_possible_truncation)]
      fn to_index(value: u64) -> u32 { value as u32 }
      #[allow(dead_code)]
      fn legacy_lookup() {}
good: #[allow(clippy::cast_possible_truncation, reason = "value < MAX_ITEMS fits in u32")]
      fn to_index(value: u64) -> u32 { value as u32 }
      #[allow(dead_code, reason = "temporary until issue 123 deletes it")]
      fn legacy_lookup() {}
```

## Limits
A suppression whose symbolic rule name already makes clear why it applies at the site needs no further explanation. Where the suppression mechanism makes the reason a required field, the tool itself requires it; in other mechanisms the reason is an optional parameter or a documented convention, and an analyzer rule that demands it applies only where the project's analyzer configuration enables it, so a tool enforces the reason only where the project's configuration enables such a rule, while this rule asks for the reason whether or not a tool enforces it. The rule checks that a site-specific reason is present; whether the reason is true stays with the reviewer. The rule covers suppressions the hunk adds or edits; whole-rule settings in the analyzer configuration and suppressions the change leaves untouched lie outside it.

## Validator
Grep the hunk's added and edited lines for suppressions: lint-level attributes that allow or expect a lint, disable or ignore directive comments of linters and type checkers, suppression annotations, and directive comments that name ignored checks. For each one, read the mechanism's reason slot (a reason parameter, the text after the directive's description separator, a justification field) and the comment on the directive's line and on the line directly above it. If that text marks the suppression as temporary (temporary, for now, until, workaround, TODO, FIXME), look in it for a reference to a task or issue. Validator question: **Does a suppression the hunk adds or edits lack a reason at that site saying why the check is ignored there, where its symbolic rule name leaves that unclear, or, when marked temporary, lack a reference to its follow-up task or issue?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: TOOL-15`, severity minor, `file`, `symbol`, `code` = the suppression attribute, annotation or directive comment quoted verbatim from the diff, `fix` = the same suppression with a site-specific reason in the mechanism's reason slot or an adjacent comment, plus the follow-up task reference for a temporary one, in the file's language, `rationale` = the suppressed check and the missing reason or follow-up task reference).

## Source
- Staticcheck configuration docs, 'Line-based linter directives' (dominikh/go-tools website/content/docs/configuration/_index.md): "The `reason` is a required field that must describe why the checks should be ignored for that line of code. This field acts as documentation for other people (including future you) reading the code." (fetched)
- Clippy lint `allow_attributes_without_reason`, group `restriction` (rust-lang/rust-clippy clippy_lints/src/attrs/mod.rs): "Justifying each `allow` helps readers understand the reasoning, and may allow removing `allow` attributes if their purpose is obsolete."; its example reason names an issue, `reason = "False positive rust-lang/rust-clippy#1002020"`; README category table, row `clippy::restriction`: "lints which prevent the use of language and library features", default level `allow` (fetched)
- Rust Reference `attributes.diagnostics.lint.reason` (rust-lang/reference src/attributes/diagnostics.md): "All lint attributes support an additional `reason` parameter, to give context why a certain attribute was added." (fetched)
- RFC 2383 'lint_reasons', § Motivation (rust-lang/rfcs text/2383-lint-reasons.md): "the decisions are worth storing in the project directly with the settings they affect. [...] text it ignores will drift out of sync with the code over time [...] Lint settings should have an explanation for their use to explain why they were chosen and where they are or are not applicable." (fetched)
- ESLint docs 'Configure Rules' > 'Use configuration comments' (eslint/eslint docs/src/use/configure/rules.md): "Provide a comment explaining the reason for disabling a particular rule after the `--` section of the comment. [...] If a disable comment is added as a temporary measure to address a pressing issue, create a follow-up task to address the underlying problem adequately. This ensures that the disable comment is revisited and resolved at a later stage." and "Code reviews can help identify the reasons behind disable comments and ensure that they are used appropriately." (fetched)
- typescript-eslint rule `ban-ts-comment` (packages/eslint-plugin/docs/rules/ban-ts-comment.mdx): "`@ts-expect-error` is allowed when it includes a description"; option `allow-with-description` "will report if it finds a directive that does not have a description following the directive (on the same line)" (fetched)
- google/styleguide pyguide.md §2.1.4 'Lint', Decision: "If the reason for the suppression is not clear from the symbolic name, add an explanation. Suppressing in this way has the advantage that we can easily search for suppressions and revisit them." (fetched)
- google/styleguide pyguide.md §3.12 'TODO Comments': "Use `TODO` comments for code that is temporary, a short-term solution, or good-enough but not perfect. A `TODO` comment begins with the word `TODO` in all caps, a following colon, and a link to a resource that contains the context, ideally a bug reference. A bug reference is preferable because bugs are tracked and have follow-up comments." (fetched)
- google/styleguide tsguide.html §'Suppressing `any` lint warnings' (#any-suppress, on lint warnings about the `any` type): "add a comment that suppresses the lint warning, and document why it is legitimate"; its example puts the explanation on the lines above the directive (fetched)
- Caveat: the evidence is tool and style-guide documentation; no cited study measures the effect of a written suppression reason.

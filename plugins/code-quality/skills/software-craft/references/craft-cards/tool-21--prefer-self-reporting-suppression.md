---
title: Where the language offers a suppression that reports itself once the diagnostic stops firing, a change uses it instead of the silent form unless the diagnostic fires under only some of the project's build configurations
rule_id: TOOL-21
domain: tooling
step: [implement, review]
applies_to: [universal]
triggers: ['#!?\[allow\(|@ts-ignore\b']
scope: hunk
check_kind: mechanical
severity_default: minor
---

# Where the language offers a suppression that reports itself once the diagnostic stops firing, a change uses it instead of the silent form unless the diagnostic fires under only some of the project's build configurations

## Thesis
Where the suppression mechanism offers a form that reports itself when the suppressed diagnostic is no longer emitted, a suppression added by a change uses that form instead of the silent one. The exception is a diagnostic emitted under only some of the build configurations the project builds with, such as toolchain versions, platforms, feature sets, test builds or compiler settings: there the change uses a form that tolerates the difference and gives it a reason that names the condition.

## Rationale
The silent form does not trigger when no diagnostic is found: on code that no longer produces the diagnostic it does nothing, so a suppression that has outlived its diagnostic stays in the source and the form itself never reports it. The self-reporting form suppresses the diagnostic while checking that the code still emits it; when the diagnostic is not emitted, the toolchain reports at the suppression itself that the expectation is no longer fulfilled, which notifies the maintainer when the diagnostic is no longer triggered. Where one build configuration the project builds with emits the diagnostic and another does not, the self-reporting form is reported on the second, and a clean run on both needs a form that tolerates the difference. The reason gives the context why the suppression was added.

## Example
```rust
bad:  #[allow(dead_code, reason = "kept for v1 readers until they migrate")]
      fn legacy_checksum(data: &[u8]) -> u32 { ... }
good: #[expect(dead_code, reason = "kept for v1 readers until they migrate")]
      fn legacy_checksum(data: &[u8]) -> u32 { ... }
```

## Limits
A mechanism with a single suppression form leaves no form to choose; where its tool reports unused suppressions through a project-wide option instead, enabling that option is project configuration and outside this rule. A scope-wide setting at the top of a file or module, which enables or disables a diagnostic for the whole scope, is outside the rule; the rule concerns a suppression attached to one construct. The sources differ on the silent form. A linter's recommended configuration reports the ignore directive by default and proposes the expect directive, and a restriction-group lint of another toolchain proposes replacing an allow attribute on an item with expect. A toolchain's release notes leave the choice to the team and name three cases for the silent form: a line that errors in one toolchain version but not another, new errors in a larger project in code with no clear owner, and a team without the time to decide between the forms. A style guide forbids both directive forms outside unit tests. The condition that separates the cases is whether the suppressed diagnostic fires under every build configuration the project builds with: toolchain version, platform, feature set, test build and compiler setting. If it does, the self-reporting form applies. If it fires under only some, the tolerant form applies with a reason, as in the documented example that keeps an ignore, together with an explicit tolerance of its own unused-suppression report, to get a clean run on both of two language versions, and the one that gives an allow-level suppression the reason "this is only modified on some platforms". The ownerless bulk case, a team without the time to decide and a policy of no directives at all are project choices the rule leaves to the project's configuration.

## Validator
Grep the hunk's added lines for a suppression in the silent form: an allow-level lint attribute, an ignore directive comment. Skip a scope-wide setting at the top of a file or module. For each remaining suppression, confirm that the project's toolchain, at every version it builds with, the oldest supported one included, offers a self-reporting form for that diagnostic, such as an expect lint level or an expect-error directive; where it offers none, stop. Open the project's analyzer configuration: where it explicitly permits the silent form, such as an ignore directive allowed with a description, or forbids the self-reporting form as well, stop. Open the suppression's reason and the build configuration the hunk belongs to: where the project builds with several build configurations, such as toolchain versions, platforms, feature sets, test builds or compiler settings, and the reason names one under which the diagnostic does not fire, stop. Validator question: **Does the hunk add a silent-form suppression where the toolchain offers a self-reporting form, without a reason that names a build configuration under which the diagnostic does not fire?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: TOOL-21`, severity minor, `file`, `symbol`, `code` = the added silent-form suppression line verbatim, `fix` = the same suppression rewritten in the self-reporting form with the same diagnostic name and reason, in the file's language, `rationale` = names the suppressed diagnostic and that the silent form stays unreported once that diagnostic is no longer emitted).

## Source
- rust-lang/rust src/doc/rustc/src/lints/levels.md, § expect (fetched): "Sometimes, it can be helpful to suppress lints, but at the same time ensure that the code in question still emits them."; "If the lint in question is not emitted, the `unfulfilled_lint_expectations` lint triggers on the `expect` attribute, notifying you that the expectation is no longer fulfilled."; § Via an attribute: "to give context why a certain attribute was added. This reason will be displayed as part of the lint message", example `#[allow(unused_mut, reason = "this is only modified on some platforms")]`.
- rust-lang/reference src/attributes/diagnostics.md, attributes.diagnostics.expect.intro (fetched): "If the expectation is unfulfilled, because lint `C` would not be emitted, the `unfulfilled_lint_expectations` lint will be emitted at the attribute."
- rust-lang/rust-clippy clippy_lints/src/attrs/mod.rs, ALLOW_ATTRIBUTES, restriction group (fetched): "Checks for usage of the `#[allow]` attribute and suggests replacing it with the `#[expect]` attribute"; "`#[allow]` will not trigger if a warning isn't found. `#[expect]` triggers if there are no warnings."; "This can be useful to be notified when the lint is no longer triggered."; "This lint only warns outer attributes (`#[allow]`), as inner attributes (`#![allow]`) are usually used to enable or disable lints on a global scale."
- microsoft/TypeScript-Website packages/documentation/copy/en/release-notes/TypeScript 3.9.md (fetched): "While it's entirely up to you and your team, we have some ideas of which to pick in certain situations."; "if there's no error, TypeScript will report that `// @ts-expect-error` wasn't necessary"; "`// @ts-ignore` will do nothing if the following line is error-free"; "Pick `ts-ignore` if: - you have a larger project and new errors have appeared in code with no clear owner - you are in the middle of an upgrade between two different versions of TypeScript, and a line of code errors in one version but not another. - you honestly don't have the time to decide which of these options is better."
- typescript-eslint packages/eslint-plugin/src/rules/ban-ts-comment.ts and docs/rules/ban-ts-comment.mdx, recommended (fetched): "Use \"@ts-expect-error\" instead of \"@ts-ignore\", as \"@ts-ignore\" will do nothing if the following line is error-free."; "`@ts-ignore` and `@ts-nocheck` are reported."
- python/mypy docs/source/error_code_list2.rst, unused-ignore (fetched): "If you use [...] `--warn-unused-ignores` mypy generates an error if you don't use a `# type: ignore` comment"; "The \"[unused-ignore]\" is needed to get a clean mypy run on both Python 3.8, and 3.9".
- google/styleguide tsguide.html, § @ts-ignore (fetched): "Do not use `@ts-ignore` nor the variants `@ts-expect-error` or `@ts-nocheck`."; "You may use `@ts-expect-error` in unit tests, though you generally *should not*."
- hands-on check, rustc 1.97.0 and tsc 6.0.2: `#[expect(dead_code)]` on a helper used only under `#[cfg(feature = "extra")]` or `#[cfg(test)]` compiles clean in one configuration and fails with "error: this lint expectation is unfulfilled" under `-D warnings` in the other; one `// @ts-expect-error` line passes under `--strict` and fails with "error TS2578: Unused '@ts-expect-error' directive." under `--strict false`.
- Caveat: the self-reporting forms evidenced here belong to two toolchains, and the build-configuration exception rests on release notes, documentation examples and compiler runs, not on a study.

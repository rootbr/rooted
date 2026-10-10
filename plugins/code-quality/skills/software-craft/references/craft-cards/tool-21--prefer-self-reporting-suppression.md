---
title: Where the language offers a suppression that reports itself once the diagnostic stops firing, a change uses it instead of the silent form unless the diagnostic fires under only some of the project's build configurations
rule_id: TOOL-21
domain: tooling
step: [implement]
applies_to: [universal]
triggers: ['#!?\[allow\(|@ts-ignore\b']
scope: callers
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
A mechanism with a single suppression form leaves no form to choose; where its tool reports unused suppressions through a project-wide option instead, enabling that option is project configuration and outside this rule. A scope-wide setting at the top of a file or module, which enables or disables a diagnostic for the whole scope, is outside the rule; the rule concerns a suppression attached to one construct. The sources differ on the silent form. A linter's recommended configuration reports the ignore directive by default and proposes the expect directive, and a restriction-group lint of another toolchain proposes replacing an allow attribute on an item with expect. A toolchain's release notes leave the choice to the team and name three cases for the silent form: a line that errors in one toolchain version but not another, new errors in a larger project in code with no clear owner, and a team without the time to decide between the forms. A style guide forbids both directive forms outside unit tests. The condition that separates the cases is whether the suppressed diagnostic fires under every build configuration the project builds with: toolchain version, platform, feature set, test build and compiler setting. If it does, the self-reporting form applies. If it fires under only some, the tolerant form applies with a reason, as in the documented example that keeps an ignore, together with an explicit tolerance of its own unused-suppression report, to get a clean run on both of two language versions, and the one that gives an allow-level suppression the reason "this is only modified on some platforms". The ownerless bulk case, a team without the time to decide and a policy of no directives at all are project choices the rule leaves to the project's configuration. The reason a self-reporting suppression carries meets the requirements on any suppression's reason, so a reason that marks it as temporary also names its follow-up task or issue.

## Validator
Grep the hunk's added lines for a suppression in the silent form: an allow-level lint attribute, an ignore directive comment. Skip a scope-wide setting at the top of a file or module. For each remaining suppression, confirm that the project's toolchain, at every version it builds with, the oldest supported one included, offers a self-reporting form for that diagnostic, such as an expect lint level or an expect-error directive; where it offers none, stop. Open the project's analyzer configuration: where it explicitly permits the silent form, such as an ignore directive allowed with a description, or forbids the self-reporting form as well, stop. Open the suppression's reason and the build configuration the hunk belongs to: where the project builds with several build configurations, such as toolchain versions, platforms, feature sets, test builds or compiler settings, and the reason names one under which the diagnostic does not fire, stop. Validator question: **Does the hunk add a silent-form suppression where the toolchain offers a self-reporting form, without a reason that names a build configuration under which the diagnostic does not fire?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: TOOL-21`, severity minor, `file`, `symbol`, `code` = the added silent-form suppression line verbatim, `fix` = the same suppression rewritten in the self-reporting form with the same diagnostic name and reason, in the file's language, `rationale` = names the suppressed diagnostic and that the silent form stays unreported once that diagnostic is no longer emitted).

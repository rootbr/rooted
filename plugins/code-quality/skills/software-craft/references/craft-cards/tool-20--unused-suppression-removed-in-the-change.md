---
title: A suppression that no longer silences any diagnostic is removed, in the change that made it unnecessary
rule_id: TOOL-20
domain: tooling
step: [implement, refactor, review]
applies_to: [universal]
triggers: ['#\s*(?:(?:ruff|flake8):\s*)?noqa|#\s*(?:type|pyright):\s*ignore|#\s*pylint:\s*disable', 'eslint-disable|@ts-(?:expect-error|ignore|nocheck)\b', '@Suppress(?:Warnings|FBWarnings)\(|//\s*NOPMD\b', '#!?\[(?:allow|expect)\(|#!?\[cfg_attr\(.*\b(?:allow|expect)\(', '//\s*(?:nolint|lint:(?:file-)?ignore)\b']
scope: base-compare
check_kind: semantic
severity_default: minor
---

# A suppression that no longer silences any diagnostic is removed, in the change that made it unnecessary

## Thesis
A change that fixes, rewrites or deletes the code a suppression covers, so that the diagnostic it names no longer fires there, removes that suppression in the same change. Every suppression the change adds, or leaves at code it edits, covers a diagnostic that the project's configured analyzer would report at that site without it, and every entry of a committed suppression baseline whose violation the change resolved is pruned from the baseline. A suppression that one analyzer run reports as unused, but that another platform, another toolchain version or another tool still needs, stays and either states that need in its reason or carries the analyzer's own marker for an expected-unused suppression.

## Rationale
A suppression that no longer matches any diagnostic is likely included by mistake, and should be removed to avoid confusion. Some suppressions, useless ones included, may unintentionally hide future warnings, and cleaning up directives that are no longer applicable can prevent later errors from being unexpectedly suppressed. In a study of suppressions for four static analyzers in projects written in three languages, 50.8% of all suppressions did not affect any warning and were practically useless. A suppression goes stale when the code it covers changes, and also when an analyzer release fixes the false positive it was written for, since the analyzer then no longer generates the incorrect report. Several analyzers report a stale suppression as a problem of its own: a check disabled for a line or block but never triggered, an ignore comment on a line where no error would be generated anyway, a lint expectation that is no longer fulfilled. One analyzer's committed bulk-suppression file shows the same mechanism: when the violations have been resolved but their suppressions are still in place, the analyzer reports the unused suppressions as an error, and a prune command removes the suppressions that are no longer needed.

## Example
```rust
bad:  #[allow(unused_variables)]
      let limit = settings.limit;
      process(&items, limit);
good: let limit = settings.limit;
      process(&items, limit);
```

## Limits
An analyzer can report a suppression as unused when it suppressed nothing during the current run, so a suppression needed on another platform or toolchain version, or by rules that were not part of the run, can report as unused there. Such a suppression is kept when its reason gives the context why it was added, for example that the variable it covers is only mutated on some platforms, or when it lists the analyzer's unused-suppression code next to the code it suppresses so that runs on every supported toolchain version stay clean. An analyzer that cannot know whether another tool produces a warning at a site leaves a broad suppression there unreported, so a clean run does not show that a broad suppression is still needed. The rule reaches the suppressions and baseline entries the change adds, and those whose covered code the change edits or deletes; an unused suppression at code the change leaves untouched predates the change. A finder is dispatched only on a file where an added line carries a suppression token, so a stale suppression left on an unchanged line, or a stale baseline entry, in a change that adds no suppression token to that file is not reviewed against this rule; the author of the change applies the validator question to it.

## Validator
Grep the hunk, and the file at base and at head, for the language's suppression mechanism (line, block and file-level directives, ignore comments, suppression annotations, lint attributes), and keep the suppressions on added lines and those whose covered line, construct, block or file contains an edited or removed line. For each suppression the change adds, or whose covered construct the change edits or deletes, read the diagnostic it names and trace whether the head code still produces that diagnostic at that site: the variable now read, the cast removed, the call deleted, or the analyzer output when the change carries it. An analyzer that has the named check disabled in its configuration may not report the directive as unnecessary, so read the code rather than rely on a clean run. In the committed suppression baseline that the analyzer's configuration names, changed or not, check at head that entries for violations the change fixed or deleted are gone. Read each surviving suppression's reason or marker for a platform, toolchain version or other tool that still needs it. Validator question: **Does the head revision keep a suppression the change added, a suppression at code the change edited or deleted, or a baseline entry for a violation the change resolved, whose diagnostic does not fire at that site at head, with no reason or marker naming a platform, toolchain version or other tool that still needs it?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: TOOL-20`, severity minor, `file`, `symbol`, `code` = the suppression directive, annotation, attribute or baseline entry verbatim from the head revision, `fix` = the same code with the suppression removed, in the file's language, `rationale` = the diagnostic the suppression names, the edit that stopped it firing, and the later diagnostics at that site the stale suppression would hide).

## Source
- DOI 10.1145/3715729, 'An Empirical Study of Suppressed Static Analysis Warnings', Proc. ACM Softw. Eng. 2(FSE), FSE014, abstract (fetched, from the PurCL/ASE bibliography): "studying projects written in three popular languages and suppressions for warnings by four popular static analyzers [...] 50.8% of all suppressions do not affect any warning and hence are practically useless, (iv) some suppressions, including useless ones, may unintentionally hide future warnings". Caveat: the abstract gives the share without a per-language breakdown.
- Ruff RUF100 unused-noqa, rule documentation (fetched): "A `noqa` directive that no longer matches any diagnostic violations is likely included by mistake, and should be removed to avoid confusion."
- Pylint I0021 useless-suppression (fetched): "Reported when a message is explicitly disabled for a line or a block of code, but never triggered."
- mypy error code unused-ignore (fetched): "there is a comment, but there would be no error generated by mypy on this line anyway"; its example: "The "[unused-ignore]" is needed to get a clean mypy run on both Python 3.8, and 3.9 where this module was added" above `# type: ignore[import,unused-ignore]`.
- ESLint CLI, `--report-unused-disable-directives` (fetched): "This can be useful to prevent future errors from unexpectedly being suppressed, by cleaning up old `eslint-disable` and `eslint-enable` comments which are no longer applicable." and "If the bug is then fixed in a patch release of ESLint, the `eslint-disable` comment becomes unused since ESLint is no longer generating an incorrect report."
- ESLint Bulk Suppressions, 'Resolving Suppressions' (fetched): "an error is reported about unused suppressions. This is because the violations have been resolved but the suppressions are still in place." and "To remove the suppressions that are no longer needed, you can use the `--prune-suppressions` flag."; the file is committed: "You should commit this file to the repository".
- Staticcheck configuration, 'Maintenance of linter directives' (fetched): "It is crucial to update or remove outdated linter directives when code has been changed. Staticcheck helps you with this by making unnecessary directives a problem of its own." and "Checks that have been disabled via configuration files will not cause directives to be considered unnecessary."
- PMD UnnecessaryWarningSuppression (fetched): "did not suppress a violation _during the current run_" and "`@SuppressWarnings("all")` is never reported as we cannot know if another tool is producing a warning there that must be suppressed."
- rustc book, 'Lint Levels' (fetched): "the `unfulfilled_lint_expectations` lint triggers on the `expect` attribute, notifying you that the expectation is no longer fulfilled" and "All lint attributes support an additional `reason` parameter, to give context why a certain attribute was added", e.g. `#[allow(unused_mut, reason = "this is only modified on some platforms")]`.

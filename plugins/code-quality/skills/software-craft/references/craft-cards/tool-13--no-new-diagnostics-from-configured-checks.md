---
title: A change adds no new diagnostic to the output of the project's configured compiler, type checker and analyzers, and each warning it would introduce is fixed or marked in the source as a false positive
rule_id: TOOL-13
domain: tooling
step: [implement, review]
applies_to: [universal]
triggers: []
scope: callers
check_kind: semantic
severity_default: minor
---

# A change adds no new diagnostic to the output of the project's configured compiler, type checker and analyzers, and each warning it would introduce is fixed or marked in the source as a false positive

## Thesis
A change leaves the output of the project's configured compiler, type checker and analyzers (the checks enabled in its source code or build instructions) free of any diagnostic the change introduces. Each warning the change would add is fixed in the code or, when it is a false positive, marked as a false positive in the source. The gate covers the change's own diagnostics only: warnings that untouched code already drew stay outside it, and new code is held to no new issues.

## Rationale
A diagnostic worth reporting is worth fixing in the code, and one not worth fixing is not worth reporting. Warnings about weak cases can make compilation noisy, masking the real errors that should be fixed. In interviews with 20 developers, all of whom felt that using static analysis tools is beneficial, false positives and the way warnings are presented were among the barriers to use. Fixing every existing issue at the moment a check is introduced into a large codebase is not practical, and it is much better to allow no issues in new code. One analyzer's documentation recommends running it in continuous integration with its warnings denied, so that its lints prevent the integration run from passing. A longitudinal study of 54 open source projects (112,266 commits) found that an analyzer's presence in the build process had a small, not statistically significant influence on warning-removal trends per line of code. Taking defect density as a proxy for external quality, the same study saw a positive effect where the analyzer was present in the build configuration.

## Example
```typescript
bad:  function sum(items: number[]): number {
        const count = items.length; // noUnusedLocals: never read
        return items.reduce((acc, item) => acc + item, 0);
      }
good: function sum(items: number[]): number {
        return items.reduce((acc, item) => acc + item, 0);
      }
```

## Limits
Ideally a project has no warnings at all, but it may accept some warnings as a whole, typically fewer than 1 warning per 100 lines or fewer than 10 warnings; that count is no allowance for a change, so this rule flags each warning a change adds however few the project has, and warnings that code the change leaves untouched already drew are not its findings. A diagnostic marked in the source as a false positive is addressed. One analyzer's documentation states that its heuristics do not guarantee that all its reports are genuine problems, that it does not check every possible problem, and that its output should be used as guidance only, not as a firm indicator of program correctness. No trigger pattern is set: any line a change adds, modifies or removes can draw a diagnostic, and which construct draws one depends on the checks the project configures, so the rule runs on every hunk.

## Validator
List the lines the hunk adds, modifies or removes. Open the file and the project's committed checker configuration that governs it (compiler flags, type-checker settings, analyzer configuration) and note which checks are enabled. Where the checks' output for the change is available, read the diagnostics it reports on the file and at usages of a declaration the hunk changes. Otherwise trace each added or modified construct, and each declaration or import a removal leaves without a use, against the enabled checks: a local or import never read, a value the type checker cannot type under the configured strictness, a pattern an enabled analyzer rule names. Where the hunk changes a declaration's name, parameters or type, open its usages across the repository and trace each against the enabled checks. Set aside diagnostics the code already drew before the change. For each remaining diagnostic, look for a fix in the change or a false-positive marking in the source with the language's suppression mechanism. Validator question: **Does the change introduce a diagnostic from the project's configured compiler, type checker or analyzer that it neither fixes nor marks in the source as a false positive?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: TOOL-13`, severity minor, `file`, `symbol`, `code` = the line that draws the diagnostic, quoted verbatim from the file as the change leaves it (for a diagnostic a removal causes, the declaration or import left without a use; for one drawn at a usage in another file, that usage's line), `fix` = that line rewritten in the file's language so the configured check reports nothing, or the false-positive marking with its reason, `rationale` = names the configured check and the diagnostic it reports on the change).

## Source
- Go FAQ, 'Can I stop these complaints about my unused variable/import?' (golang/website `_content/doc/faq.md`): "if it's worth complaining about, it's worth fixing in the code. (Conversely, if it's not worth fixing, it's not worth mentioning.) Second, having the compiler generate warnings encourages the implementation to warn about weak cases that can make compilation noisy, masking real errors that *should* be fixed." (fetched)
- OpenSSF Best Practices Badge criteria, 'warnings' and 'warnings_fixed' (coreinfrastructure/best-practices-badge `docs/criteria.md`): "These are typically enabled within the source code or build instructions." / "The project MUST address warnings. [...] The project should fix warnings or mark them in the source code as false positives. Ideally there would be no warnings, but a project MAY accept some warnings (typically less than 1 warning per 100 lines or less than 10 warnings)." (fetched) The tolerance is stated for a project's warnings as a whole.
- golangci-lint configuration reference, `issues.new` (golangci/golangci-lint `.golangci.reference.yml`): "It's a super-useful option for integration of golangci-lint into existing large codebase. It's not practical to fix all existing issues at the moment of integration: much better don't allow issues in new code." (fetched)
- Clippy book, 'Continuous Integration' (rust-lang/rust-clippy `book/src/continuous_integration/README.md`): "It is recommended to run Clippy on CI with `-Dwarnings`, so that Clippy lints prevent CI from passing." (fetched) Stated for that analyzer.
- Google TypeScript Style Guide, 'Toolchain requirements' > 'TypeScript compiler' (google/styleguide `tsguide.html`): "All TypeScript files must pass type checking using the standard tool chain." (fetched) Stated for that language's type checker; the same section bars suppressing its errors in the source, so it supports the fix route only.
- cmd/vet documentation (golang/go `src/cmd/vet/doc.go`): "Vet uses heuristics that do not guarantee all reports are genuine problems [...] the tool does not check every possible problem and depends on unreliable heuristics, so it should be used as guidance only, not as a firm indicator of program correctness." (fetched) Stated of that analyzer's own checks.
- DOI 10.1109/ICSE.2013.6606613, 'Why Don't Software Developers Use Static Analysis Tools to Find Bugs?', ICSE 2013, pp. 672-681, abstract (DeveloperLiberationFront/bibtex-library `our-papers.bib`): "We conducted interviews with 20 developers and found that although all of our participants felt that use is beneficial, false positives and the way in which the warnings are presented, among other things, are barriers to use." (fetched) An interview study.
- DOI 10.1007/s10664-020-09880-1 (arXiv:1912.02179), 'A longitudinal study of static analysis warning evolution and the effects of PMD on software quality in Apache open source projects', Empirical Software Engineering 2020, abstract (eosc-sq/ensure-sq `docs/papers-batch-freezed/papers_batch_000-019.md`): "We analyzed the commit history of 54 projects (with 112,266 commits in total) [...] the influence of the presence of PMD in the build process of the project on warning removal trends for the number of warnings per lines of code is small and not statistically significant. Regardless, if we consider defect density as a proxy for external quality, we see a positive effect if PMD is present in the build configuration of our study subjects." (fetched) One analyzer in Apache open source projects; observational.

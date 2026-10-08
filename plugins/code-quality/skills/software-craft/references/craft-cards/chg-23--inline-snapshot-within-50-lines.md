---
title: An inline snapshot stays within 50 lines and a longer expected output moves to a snapshot file
rule_id: CHG-23
domain: change
step: [test, review]
applies_to: [tests]
triggers: ['(?i)inline_?snapshot|snapshot!\(.*@|==\s*snapshot\(|expect!\[\[|expect_?selfie\(', 'signal:test_file']
scope: file
check_kind: mechanical
severity_default: minor
---

# An inline snapshot stays within 50 lines and a longer expected output moves to a snapshot file

## Thesis
A snapshot written inline in the test code stays within 50 lines, the default limit of the lint check that measures snapshot size, or the inline maximum the project configures in that check; a longer expected output is stored in a snapshot file.

## Rationale
A stored snapshot is part of a test, like the value of any other assertion, and it is only as good as its review; keeping it short and readable is important to allow a thorough review. Inline snapshots are recommended mostly for simpler and smaller outputs; for complex and longer outputs, developers should favour snapshots based on external files, to avoid cluttering the test method. In an empirical study of snapshot tests, the median test was 14 lines of code and tests with more than 53 lines of code were counted as outliers; the presence of those large outliers suggests keeping snapshots brief and avoiding inline snapshots that are too big. The same study names an inline snapshot that grows excessively large, cluttering the test code, as a test smell. Large snapshots can be cumbersome to review and manage, especially during merge conflicts: in a review of 50 grey-literature documents on snapshot testing, 8 (16%) named large snapshots as a drawback, particularly for complex components, and 7 (14%) gave writing small snapshots as a practice that reduces the downsides of snapshot testing; smaller, focused snapshots were recommended to improve readability and ease of maintenance. The lint check measures each stored snapshot, in a snapshot file or inline, as its closing line number minus its opening line number and flags a measure above 50 by default; a separate inline limit, when set, applies to inline snapshots, and otherwise the one maximum applies to both kinds. One test framework's official snapshot-testing guidance suggests that check as a tool to promote committing short, focused assertions.

## Example
```rust
bad:  // the whole rendered page, 400 lines, written inline in the test
      insta::assert_snapshot!(render_page(&model), @r#"
      <html>
        ...
      "#);
good: // the same expected output, stored in a snapshot file
      insta::assert_snapshot!(render_page(&model));
```

## Limits
For complex and longer outputs a snapshot file is the recommended home; the size of a snapshot file is outside this rule. The 50-line figure is a configurable tool default; the practitioner review that names large snapshots as a drawback gives no line count, and the study's 53-line outlier bound counts the lines of whole tests, not of snapshots; where a project sets an inline maximum, or one maximum for both kinds, an inline snapshot is measured against that maximum, as the lint check applies its options. The rule measures length only: a snapshot within the limit is still committed and reviewed as part of the regular code review.

## Validator
Grep the hunk for an inline snapshot: an assertion whose expected value the snapshot tool writes into the test code and rewrites when the snapshot is updated, whether its matcher, macro or function name contains snapshot or it is a snapshot tool's inline expectation such as `expect![[...]]` or a `toBe(...)`/`to_be(...)` on an `expectSelfie(...)`/`expect_selfie(...)` subject. Open the file at each hit and, for each added or changed inline snapshot, subtract the line number on which its literal opens from the line number on which that literal closes. Read the project's lint configuration for a configured inline maximum, or for one maximum set for both kinds where no inline maximum is set. Validator question: **Does an added or changed inline snapshot measure more than the inline maximum the project configures, or more than 50 lines where it configures none, counted as its closing line number minus its opening line number?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: CHG-23`, severity minor, `file`, `symbol`, `code` = the opening line of the oversized inline snapshot's assertion, verbatim, `fix` = the assertion in its snapshot-file form, in the file's language, `rationale` = the inline snapshot's measure against the configured inline maximum or the 50-line default, and that a longer expected output belongs in a snapshot file).

## Source
- eslint-plugin-jest rule `jest/no-large-snapshots`, jest-community/eslint-plugin-jest docs/rules/no-large-snapshots.md, introduction, §Rule details, §Options (fetched): "A stored snapshot is only as good as its review and as such keeping it short, sweet, and readable is important to allow for thorough reviews." · "This rule looks at all Jest inline and external snapshots" · "validates that each stored snapshot within those files does not exceed 50 lines (by default, this is configurable as explained in `Options` section below)" · "Max number of lines allowed could be defined by snapshot type (Inline and External)." · "If only `maxSize` is provided on options, the value of `maxSize` will be used for both snapshot types (Inline and External)."
- Its source src/rules/no-large-snapshots.ts and the port vitest-dev/eslint-plugin-vitest `vitest/no-large-snapshots`, src/rules/no-large-snapshots.ts (fetched): `maxSize: lineLimit = 50` · `const lineCount = endLine - startLine` · `if (!isAllowed && lineCount > lineLimit)` · `maxSize: options.inlineMaxSize ?? options.maxSize`. The port's docs/rules/no-large-snapshots.md (fetched) states "`inlineMaxSize` (default: `0`): The maximum size of a snapshot when it is inline.", a default its source does not apply: with `inlineMaxSize` unset, the inline limit falls back to `maxSize` and then to 50.
- Jest documentation, jestjs/jest docs/SnapshotTesting.md, §Best Practices 1 'Treat snapshots as code' and FAQ (fetched): "Ensure that your snapshots are readable by keeping them focused, short, and by using tools that enforce these stylistic conventions." · "to promote committing short, focused assertions" · "They should be considered part of a test, similar to the value of any other assertion in Jest." · "Commit snapshots and review them as part of your regular code review process."
- Master's dissertation 'Understanding Snapshot Testing in Practice', PPGCC/UFMG, 2024, VictorGazzinelli/dissertacao-mestrado-ppgcc-ufmg exemplo-victor/exemplo.tex, carrying material from J. Syst. Softw. 204 (2023) 111797; ch. 3 grey-literature review RQ3.2, RQ3.3 and ch. 4 empirical study (fetched): "we selected 50 documents for analysis" · "Eight documents (16\%) mentioned the issue of large snapshots, particularly for complex components. Large snapshots can be cumbersome to review and manage, especially during merge conflicts." · "Best practices to reduce downsides of snapshot testing." · "Write small snapshots & 14\% & 7" · "Smaller, focused snapshots and detailed test descriptions were also recommended to improve readability and ease of maintenance" · "As we discussed earlier, inline snapshots are recommended mostly for simpler and smaller outputs. For complex and longer outputs, developers should favor regular snapshots based on external files to avoid cluttering the test method." · "the distribution of lines of code (LOC) across all tests in our sample" · "with a median size of 14 LOC" · "we considered tests as outliers if they had LOC greater than 53" · "the presence of large outliers in this distribution suggests that developers should be careful to keep snapshots brief and avoid including inline snapshots that are too big in their tests" · "the Large Snapshot Test smell, which occurs when inline snapshots grow excessively large, cluttering the test code" · "The core idea behind this refactoring is to move the large inline snapshot from the test code into a separate external file. This reduces the size and complexity of the test method itself".
- Caveat: the line limit and the evidence come from one JavaScript test framework's ecosystem, and the 50-line figure is a tool default that no cited study measured.

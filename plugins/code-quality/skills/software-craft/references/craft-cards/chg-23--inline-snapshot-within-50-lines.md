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

---
title: A skipped, disabled or quarantined test states its reason or tracking reference in the skip itself, and no test is skipped unconditionally without one
rule_id: TST-38
domain: tests
step: [test, review]
applies_to: [tests]
triggers: ['^\s*@(Ignore|Disabled)\s*(\(\s*\))?\s*(//.*)?$', '^\s*@(unittest[.]skip|pytest[.]mark[.](skip|xfail))\s*(\(\s*\))?\s*(#.*)?$', '\b(it|test|describe)[.](skip|fixme)\(|\b(xit|xdescribe|xtest)\(', '\bt[.](Skip|SkipNow)\(\s*\)', '^\s*#\[ignore\]\s*(//.*)?$', '\bassume(True\(\s*false|False\(\s*true)\b']
scope: hunk
check_kind: mechanical
severity_default: minor
---

# A skipped, disabled or quarantined test states its reason or tracking reference in the skip itself, and no test is skipped unconditionally without one

## Thesis
A skip, disable, ignore, quarantine or non-strict expected-failure mark on a test states why the test is off in the mark itself: as the mark's reason argument where the mechanism takes one, otherwise as a comment on the mark. An assumption that is always false skips the test without a mark; it is removed, or replaced by a skip mark that states its reason. A tracking reference serves as that reason. Every unconditional skip names its reason.

## Rationale
A test that is ignored without some notation about why may never be reactivated: such tests are difficult to address without comprehensive knowledge of the project, and they end up polluting it. A non-strict expected-failure mark keeps the test's failure from breaking the whole build, so it can be considered a manual quarantine, and it is rather dangerous to use permanently. The reason in the mark is the notation about why the test is off.

## Example
```python
bad:  @pytest.mark.skip
      def test_export(): ...
      @pytest.mark.xfail
      def test_import(): ...
good: @pytest.mark.skip(reason="export sandbox is down; tracked as export-sandbox")
      def test_export(): ...
      @pytest.mark.xfail(reason="rounding bug; tracked as import-rounding")
      def test_import(): ...
```

## Limits
A skip that applies only under a stated condition, such as a browser or environment setup, and names its reason satisfies the rule. An unconditional skip that names why the test is off, for example an infrastructure issue that makes it fail for now, also satisfies it. The rule reaches the mark in the diff; whether the tracked item is later closed and the test reactivated is the team's process and lies outside the diff.

## Validator
Grep the hunk for added skip, disable, ignore, fixme, non-strict expected-failure and quarantine marks on tests, and for assumptions that are always false. For each mark, read the reason argument where the mechanism takes one, and the comment on the mark's line or the line above it only where the mechanism takes none; a test's title is not a reason. Where a condition guards the skip, check that the skip still names its reason. An always-false assumption is flagged whatever message it carries. Validator question: **Does the hunk add an always-false assumption to a test, or a skip, disable, ignore, fixme, non-strict expected-failure or quarantine mark on a test that states no reason in its reason argument where the mechanism takes one, or in a comment on it where the mechanism takes none?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: TST-38`, severity minor, `file`, `symbol`, `code` = the mark verbatim with the test's signature line, `fix` = the same mark carrying a reason argument that states why the test is off or names its tracking reference, or such a comment where the mechanism takes no reason argument, or, for an always-false assumption, a skip mark carrying such a reason in its place, in the file's language, `rationale` = names that a test switched off without a stated reason may never be reactivated).

## Source
- SonarSource java:S1607, rule description (fetched): "When a test fails due, for example, to infrastructure issues, you might want to ignore it temporarily. But without some kind of notation about why the test is being ignored, it may never be reactivated. Such tests are difficult to address without comprehensive knowledge of the project, and end up polluting their projects"; "raises an issue for each ignored test that does not have any comment about why it is being skipped"; compliant `@Ignore("See Ticket #1234")`; "Cases where assumeTrue(false) or assumeFalse(true) are used to skip tests are targeted as well"; check message (IgnoredTestsCheck, fetched): "This assumption is called with a boolean constant; remove it or, to skip this test use an @Ignore/@Disabled annotation in combination with an explanation about why it is skipped."
- SonarSource python:S1607, rule description (fetched): "raises an issue for each skipped test with "unittest.skip" or "pytest.mark.skip" without providing a reason argument".
- Clippy lint ignore_without_reason, declaration (fetched): "Checks for ignored tests without messages"; "The reason for ignoring the test may not be obvious"; use instead `#[ignore = "Some good reason"]`.
- eslint-plugin-playwright no-skipped-test, Options › allowConditional (fetched): "allow conditional tests based on browser/environment setup"; "still catching an unconditional skip that someone left behind". Caveat: the rule flags every unconditional skip, with or without a reason, and by default a conditional one too; accepting an unconditional skip that names its reason rests on the compliant `@Ignore("See Ticket #1234")` of java:S1607.
- pytest documentation, Flaky tests › Xfail strict (fetched): "can be used to mark a test so that its failure does not cause the whole build to break. This could be considered like a manual quarantine, and is rather dangerous to use permanently."
- pytest documentation, How to use skip and xfail › XFail › `condition` and `reason` parameters (fetched): "If a test is only expected to fail under a certain condition, you can pass that condition as the first parameter"; "Note that you have to pass a reason as well"; "You can specify the motive of an expected failure with the reason parameter".

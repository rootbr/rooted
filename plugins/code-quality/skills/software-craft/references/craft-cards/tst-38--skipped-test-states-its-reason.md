---
title: A skipped, disabled or quarantined test states its reason or tracking reference in the skip itself, and no test is skipped unconditionally without one
rule_id: TST-38
domain: tests
step: [test]
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

A test switched off because it fails or flakes and the change leaves that unfixed owes in its mark both the reason and the issue that tracks the failure; that further obligation lies outside this rule, which asks only that the mark say why the test is off.

## Validator
Grep the hunk for added skip, disable, ignore, fixme, non-strict expected-failure and quarantine marks on tests, and for assumptions that are always false. For each mark, read the reason argument where the mechanism takes one, and the comment on the mark's line or the line above it only where the mechanism takes none; a test's title is not a reason. Where a condition guards the skip, check that the skip still names its reason. An always-false assumption is flagged whatever message it carries. Validator question: **Does the hunk add an always-false assumption to a test, or a skip, disable, ignore, fixme, non-strict expected-failure or quarantine mark on a test that states no reason in its reason argument where the mechanism takes one, or in a comment on it where the mechanism takes none?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: TST-38`, severity minor, `file`, `symbol`, `code` = the mark verbatim with the test's signature line, `fix` = the same mark carrying a reason argument that states why the test is off or names its tracking reference, or such a comment where the mechanism takes no reason argument, or, for an always-false assumption, a skip mark carrying such a reason in its place, in the file's language, `rationale` = names that a test switched off without a stated reason may never be reactivated).

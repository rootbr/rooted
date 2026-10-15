---
title: The description of a change sent for review says how the change was verified, such as the tests added or run and any manual steps, in enough detail for a reviewer to repeat the check
rule_id: DOC-09
domain: docs
step: [document, review]
applies_to: [universal]
triggers: ['\b(def|fn|func|function|class|struct|interface|trait|enum|impl)\s+\w+', '\b(if|elif|else|switch|match|case|for|while|return|throw|raise)\b', 'signal:test_file']
scope: base-compare
check_kind: semantic
severity_default: suggestion
---

# The description of a change sent for review says how the change was verified, such as the tests added or run and any manual steps, in enough detail for a reviewer to repeat the check

## Thesis
A change that alters behaviour reaches review with a description of the testing done to verify it: the tests added or run and any manual steps taken, written as a repeatable list with enough detail that someone unfamiliar with the change can follow it to verify the behaviour.

## Rationale
A good test plan convinces a reviewer that the author has been thorough in making sure the change works as intended, and gives someone unfamiliar with the change enough detail to verify its behaviour. In a survey in which developers rated 28 reasons for confusion during code review by frequency, the organization of work, with an unclear commit message among its examples, ranked among the five most frequent. One remedy the literature proposes for it is to describe the change informatively, emphasizing its motivation and the tests associated with it.

## Example
```java
bad:  String description = """
          Round half up in class InvoiceTotals if tax applies
          Tested locally.
          """;
good: String description = """
          Round half up in class InvoiceTotals if tax applies
          Tests: added InvoiceTotalsTest.roundsHalfUpWithTax; ran mvn test, all pass
          Manual: in staging, billed 4.50 at 1% tax; total showed 4.55
          """;
```

## Limits
A change that alters no behaviour, such as an edit to a comment, has no behaviour to verify. The account may sit in the pull-request description, in a test-plan field of the review tool, or in a tag of the commit message; any of these places meets the rule. A project may document a tolerance: the note of manual testing is waived where automated pre-submit runs cover all of the testing, and a review tool's configuration may make the test-plan field optional. Work not yet sent for review has no description to judge.

## Validator
Grep the hunk for a changed routine signature, a changed branch or a test file. Where the description the change was sent for review with is in view (the pull-request body, the review tool's test-plan field, or the commit message a commit-based review tool shows as the description), read it with the commit messages and their tags; where it is not in view, as in a review of uncommitted work or of a branch with no review request, stop. Look there for the tests added or run and for manual steps. Pass a hunk that edits only comments, and a project whose contribution guide waives the account where automated pre-submit runs cover all of the testing. Validator question: **Does a change that alters behaviour reach review with a description that names no test added or run and no step someone unfamiliar with the change could repeat to verify it?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: DOC-09`, severity suggestion, `file`, `symbol`, `code` = the changed signature or branch line quoted verbatim from the diff, `fix` = a testing section for the description naming the test added, by its name in the file's language, and the command or manual steps that verify the change, `rationale` = names the behaviour the change alters and that the description gives the reviewer no check to repeat).

## Source
- OpenJDK Developers' Guide, "Working With Pull Requests", checklist item "Write a useful description" (fetched): "The PR description should also list what testing has been done."
- Phabricator Differential User Guide, "Test Plans", Overview (fetched): "When you send a revision for review in Differential you must include a test plan"; "A test plan is a repeatable list of steps which document what you have done to verify the behavior of a change"; "A good test plan convinces a reviewer that you have been thorough in making sure your change works as intended and has enough detail to allow someone unfamiliar with your change to verify its behavior"; "(this can be disabled or made optional in the config)", option `differential.require-test-plan-field`, default true.
- Chromium docs/contributing.md, commit message tag `Test:` (fetched): "A freeform description of manual testing performed on the change."; "Not necessary if all testing is covered by trybots."
- DOI 10.1007/s10664-020-09909-5, §4.2.3 RQ4 and Table 4 (fetched): "mean and median Likert scores for the 28 reasons for confusion in terms of frequency"; "The first group contains the most frequent five reasons for confusion."; "They are: long or complex code change, organization of work (e.g., an unclear commit message, the status of the code review, a change addressing multiple issues)"; §5.2.2 RQ5, "Organization of work" item 1: "describing code changes in an informative way, particularly emphasizing the motivation for the change and the tests associated with it", reporting DOI 10.1109/MS.2017.265100500 (relayed).
- Caveat: the research proposes the remedy from a literature mapping; no study here measures the effect of a stated test plan on review outcomes.

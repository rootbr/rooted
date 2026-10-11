---
title: A test that records more than one external snapshot names each one for the content it records
rule_id: CHG-24
domain: change
step: [test]
applies_to: [tests]
triggers: ['[.](toMatchSnapshot|toThrowErrorMatchingSnapshot)\(\s*\)', '\bassert_\w*snapshot!\(\s*[^"\s)]', '==\s*snapshot\s*$', '\bexpect\s*[.]\s*toMatchSnapshot\(', '[.]scenario\(\s*"?\d+"?\s*\)']
scope: file
check_kind: mechanical
severity_default: suggestion
---

# A test that records more than one external snapshot names each one for the content it records

## Thesis
Where one test, or one scope together with the calls nested in it, records two or more external snapshots, each snapshot carries a name or hint that describes its expected content, rather than no name or a number that only tells it from the others.

## Rationale
A runner that stores snapshots outside the test source can name each one after its test and append a number to it; to tell several snapshots of one test apart, a short descriptive hint might be more useful than those numbers. A name that describes the expected content makes it easier for reviewers to verify the snapshot during review, and for anyone to know whether an outdated snapshot is the correct behaviour before updating it. A snapshot test typically makes a single, broad assertion, so its failure message can be vague and uninformative: in a review of 50 grey-literature documents on snapshot testing, 11 (22%) discussed this lack of context. The same review adds that this lack of context, often caused by minimal or unclear descriptions written with the test, complicates debugging when the test fails, and records the advice that snapshots carry detailed descriptions. The threshold of two follows the default of the lint check that enforces the practice, which requires a hint only when there are multiple external snapshot matchers within the scope, nested calls included.

## Example
```java
bad:  expect.scenario("1").toMatchSnapshot(render(order, Layout.COMPACT));
      expect.scenario("2").toMatchSnapshot(render(order, Layout.FULL));
good: expect.scenario("compact layout").toMatchSnapshot(render(order, Layout.COMPACT));
      expect.scenario("full layout").toMatchSnapshot(render(order, Layout.FULL));
```

## Limits
A test that records a single external snapshot is below the threshold: its test name can carry the description, since the documented practice asks for descriptive test and/or snapshot names. A project may set the same check to require a hint on every external snapshot; that stricter setting is a documented project choice, and this rule's threshold is the check's default. An inline snapshot, whose value the runner writes back into the test source, is out of scope: the rule, like the check, reaches external snapshots only.

## Validator
Grep the hunk for a snapshot assertion that records to an external file with no name or hint argument, or with a name that is only a number or a loop index. Open the file and, for each test or helper that contains a hit, count the external snapshots that scope records, the calls nested in it included and an assertion inside a loop counting once for each iteration; inline snapshots, whose value is written into the source, do not count. For each counted assertion, read its name or hint: a phrase that states what the snapshot holds (the output stream, the layout, the input case) passes; a missing name, a number or an index fails. Validator question: **Does a test or scope in the file record two or more external snapshots, at least one of which has no name or a name that is only a number or an index?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: CHG-24`, severity suggestion, `file`, `symbol` = the test or helper that records the snapshots, `code` = the snapshot assertions without a descriptive name, quoted verbatim from the diff, `fix` = the same assertions, each given a name or hint that states its expected content, in the file's language, `rationale` = a content name lets a reviewer verify each snapshot and tell whether an outdated snapshot is the correct behaviour before updating it).

## Source
- Jest docs, 'Snapshot Testing' §Best Practices 3 'Use descriptive snapshot names', jestjs/jest docs/SnapshotTesting.md (fetched): "The best names describe the expected snapshot content. This makes it easier for reviewers to verify the snapshots during review, and for anyone to know whether or not an outdated snapshot is the correct behavior before updating." §Inline Snapshots: "Inline snapshots behave identically to external snapshots (.snap files), except the snapshot values are written automatically back into the source code."
- Jest docs, 'Expect' §`.toMatchSnapshot(propertyMatchers?, hint?)`, jestjs/jest docs/ExpectAPI.md (fetched): "Although Jest always appends a number at the end of a snapshot name, short descriptive hints might be more useful than numbers to differentiate multiple snapshots in a single it or test block."
- eslint-plugin-jest rule `jest/prefer-snapshot-hint`, docs/rules/prefer-snapshot-hint.md (fetched): "provide a hint (as the last argument to the matcher) describing the expected snapshot content"; rule details: "This rule looks for any use of an external snapshot matcher (e.g. toMatchSnapshot and toThrowErrorMatchingSnapshot)"; option `'multi'` (default): "Require a hint to be provided when there are multiple external snapshot matchers within the scope (meaning it includes nested calls)."; option `'always'`: "Require a hint to always be provided when using external snapshot matchers."
- Grey-literature review of snapshot testing, 'Understanding Snapshot Testing in Practice', master's dissertation, PPGCC/UFMG, 2024, ch. 3 §Study Design, §Results RQ3.2 and §Discussion (fetched, GitHub-hosted LaTeX source VictorGazzinelli/dissertacao-mestrado-ppgcc-ufmg exemplo-victor/exemplo.tex; the dissertation states that it contains material from Journal of Systems and Software 204 (2023) 111797, an article not opened): "In the end, we selected 50 documents for analysis"; "Eleven documents (22%) discussed the lack of context in writing snapshot tests. Because snapshot tests typically use a single, broad assertion, the error messages can be vague and uninformative"; "The lack of context in snapshot tests, often caused by minimal or unclear descriptions when written, further complicates debugging when test failures occur"; "practitioners are advised to use smaller, focused snapshots and ensure they contain detailed descriptions."
- Example API: origin-energy/java-snapshot-testing `Expect.scenario(String)` (fetched): "@param scenario - unique scenario description".
- Caveat: the practice, the numbering and the check are documented for one JavaScript runner and its lint plugin; the card carries them to every runner that stores several snapshots of one test under generated or numeric names.

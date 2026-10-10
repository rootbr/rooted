---
title: A change that adds tests pinning existing behaviour alters none of the production behaviour those tests pin, and a fix for an oddity they expose lands in a change of its own
rule_id: CHG-19
domain: change
step: [test, review]
applies_to: [universal]
triggers: ['signal:test_file', '(?i)(characteri[sz]\w*|golden[ _-]?(master|file)|approval\w*|snapshot\w*|current[ _-]?behaviou?r)', '(?i)(#|//|/\*|\*)\s*.*\b(bug|quirk|odd(ity)?|suspicious|surpris\w*|looks wrong|should be)\b']
scope: base-compare
check_kind: semantic
severity_default: major
---

# A change that adds tests pinning existing behaviour alters none of the production behaviour those tests pin, and a fix for an oddity they expose lands in a change of its own

## Thesis
A change whose purpose is to put existing code under characterization, snapshot, golden-file or approval tests, together with the edits that make that code constructible in those tests, leaves every production behaviour the new tests observe, values returned and exceptions thrown included, as it was at the base. Behaviour that looks wrong is asserted as the base code produces it, and its correction lands in a change of its own that carries the new expected value.

## Rationale
Tests that pin existing behaviour work as regression tests do: they assert the current behaviour of the code under test, the values returned or exceptions thrown, and after a later change they alert when that change affects the external behaviour. Tests for pre-existing code submitted in a change of their own, ahead of a refactoring, can validate that the tested behaviour is unchanged before and after it; such independent test changes can go apart the way refactorings do, and a refactoring is usually best kept apart from feature changes or bug fixes because reviewers understand the changes of each more easily when they are separate. Once a pinned expectation exists, fixing a bug changes the expected behaviour, so the test fails and the difference goes to a diff tool and a review of the changes that approves it as wanted or sends it back as unwanted; a new test has no approved expectation yet, so a correction folded into the change that first writes it is reviewed only as a result, with no earlier expectation to differ from. Bundled work is common and costly: in five open-source projects up to 15% of all bug fixes consisted of multiple tangled changes, untangling them showed that on average at least 16.6% of all source files are incorrectly associated with bug reports, and a commit that bundles a bug fix with unrelated work makes review, reversion and integration harder and historical analyses less reliable. Backward-incompatible behaviour changes also ship poorly documented: cross-version regression testing of 68 consecutive version pairs from 15 libraries detected 296 behavioural backward incompatibilities in 52 of the pairs, the majority not well documented in API documents or release notes.

## Example
```java
bad:  @Test void characterizesEmptyCartTotal() {
          assertEquals(0, pricer.total(new Cart()));  // base returns -1, a bug fixed here
      }   // the same change edits Pricer.total to return 0 for an empty cart
good: @Test void characterizesEmptyCartTotal() {
          assertEquals(-1, pricer.total(new Cart()));  // suspicious: pinned as the base behaves
      }   // returning 0 lands in its own change, which updates this expectation
```

## Limits
Edits that alter no pinned behaviour, such as fixing a local variable name or a dependency-breaking refactoring, are outside the rule; how large a refactoring may grow before it makes the review harder is left to the judgment of developers and reviewers. A regression introduced by the change in hand is fixed in that change, not pinned and not moved to a change of its own: when it breaks an already recorded snapshot, the bug is fixed before the snapshots are re-generated, so the buggy behaviour is not recorded and the code behaves as at the base. The correction may also land first, as its own change with tests for the new behaviour, ahead of the pinning tests, which then record the corrected behaviour; a generated-test workflow keeps the same order, fixing the defects its error-revealing tests expose before it adds its regression tests to the suite.

## Validator
Grep the hunk for new tests that the change presents as pinning existing behaviour (characterization names, a description saying it puts existing code under test, snapshot, approval or golden-file tests for code the change does not set out to change) and for comments that call a pinned value a bug, quirk, oddity or suspicious. Open, at the base and at the head, each production routine those tests exercise. Trace every production edit in the change to the values, exceptions, outputs and side effects the new tests assert; an edit that only adds a constructor parameter, extracts an interface or renames a local leaves them as at the base. Compare each new expectation with what the base code produces; an expectation the base would fail, or a comment saying the base behaves otherwise, marks a correction folded into the change. Set aside a change whose stated purpose is a behaviour change, a feature or a fix named in its description or test names, whose new or re-recorded tests, snapshots and golden files assert the behaviour it sets out to introduce; that is the correction's own change. A production edit that fixes a regression this same change introduced, so that an already recorded snapshot passes again without being re-generated, restores the base behaviour and is not a folded correction; a regression left in the code, or recorded in a new or re-generated snapshot, alters the base behaviour. Validator question: **Does this change, whose purpose is to put existing code under tests, also alter, relative to the base, production behaviour its new tests observe, other than repairing a regression the same change introduced?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: CHG-19`, severity major, `file`, `symbol`, `code` = the new pinning assertion and the production line whose behaviour it alters, quoted verbatim from the diff, `fix` = the test asserting the base behaviour, and the production edit moved to a change of its own that updates that expectation, in the file's language, `rationale` = the observed behaviour that differs from the base and the reviewable expectation change a separate correction would give).

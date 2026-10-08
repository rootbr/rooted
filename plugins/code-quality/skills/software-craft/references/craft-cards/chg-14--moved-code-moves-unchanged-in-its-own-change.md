---
title: Code moved from one file to another is moved unchanged in its own change, and any edit to the moved code, a style fix included, goes in a separate change
rule_id: CHG-14
domain: change
step: [refactor, review]
applies_to: [universal]
triggers: ['signal:added_file', '\b(def|fn|func|function|class|struct|interface|trait|enum|impl)\s+[\w(]']
scope: base-compare
check_kind: semantic
severity_default: minor
---

# Code moved from one file to another is moved unchanged in its own change, and any edit to the moved code, a style fix included, goes in a separate change

## Thesis
When a change moves code from one file to another, the moved code stays exactly as it was in that change, its style violations included, and every edit to the moved code goes in a separate change; a bug fix in a moved class goes in a different change from the move.

## Rationale
A move that leaves the moved code untouched clearly delineates the act of moving the code from the edits made to it. That separation greatly aids review of the actual differences and lets tools better track the history of the code itself. Reviewers understand the changes introduced by each change much more easily when the move and the bug fix are separate. The usual check of a change for basic style violations has one significant exception here: the move keeps the moved code's style as it was, and a style fix to it goes in a separate change.

## Example
```go
bad:  // pricing.go: total moved here from order.go, reformatted and fixed in the same change
      func total(items []Item) int {
          return sumPrices(items) - discount(items)
      }
good: // pricing.go: total moved here from order.go as it was; the fix follows in its own change
      func total(items []Item) int { return sumPrices(items) }
```

## Limits
The rule covers the moved code itself, not the lines outside it that the new location needs, such as a package or module declaration, the import list and the references updated at the callers; these keep the system building and working after each change, which every change in a series is expected to do, so they belong to the move. A small cleanup such as fixing a local variable name can be included in a feature change or a bug fix, while code that the change moves stays unmodified even for a style fix. Code reordered within one file and code copied while the original stays in place lie outside the move between files that the rule addresses. The sources do not address an edit inside the moved block that the new location forces for the change to build and that no earlier change can make in place, such as a modifier the new location forbids or the indentation a new nesting depth requires; on the same build ground it belongs to the move.

## Validator
In the diff, find a declaration added in one file, often an added file, that pairs with a declaration removed from another file in the same change: the same name with a mostly identical body, or a mostly identical body under a new name. Open the base version of the source file and set the removed block beside the added one. Compare them line by line, skipping the package or module declaration, the import list, call sites that only point at the new location, and an edit inside the block that the new location forces for the change to build and that no earlier change can make in place, such as a modifier it forbids or the indentation a new nesting depth requires. Count any difference inside the moved block as an edit: whitespace or layout, a renamed identifier, a changed expression, an added or dropped line. Validator question: **Does the change move a block of code from one file to another and, in the same change, alter any line of the moved block that the comparison does not skip?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: CHG-14`, severity minor, `file`, `symbol`, `code` = the added line of the moved block that differs from its base version, quoted verbatim, `fix` = the moved block as the base version had it plus only the edits the new location forces and no earlier change can make in place, with a forced edit that an earlier change can make in place put in a preceding change and the other edits left for a follow-up change, in the file's language, `rationale` = names the move kept apart from the edit so that review sees the actual differences and tools track the code's history).

## Source
- Linux kernel documentation, Documentation/process/submitting-patches.rst, §'Style-check your changes' (fetched): "Check your patch for basic style violations" … "One significant exception is when moving code from one file to another -- in this case you should not modify the moved code at all in the same patch which moves it. This clearly delineates the act of moving the code and your changes. This greatly aids review of the actual differences and allows tools to better track the history of the code itself."
- Same document, §'Separate your changes' (fetched): "take special care to ensure that the kernel builds and runs properly after each patch in the series."
- google/eng-practices, review/developer/small-cls.md, §'Separate Out Refactorings' (fetched): "moving and renaming a class should be in a different CL from fixing a bug in that class. It is much easier for reviewers to understand the changes introduced by each CL when they are separate." … "Small cleanups such as fixing a local variable name can be included inside of a feature change or bug fix CL, though."
- Same document, §'Don't Break the Build' (fetched): "make sure the whole system keeps working after each CL is submitted."
- Caveat: both sources are project guidance without a measured effect size; the move rule is stated for code moved from one file to another; the second source names moving and renaming a class together as the refactoring kept apart from a bug fix, while the first leaves the moved code wholly unmodified, and the rule follows the first, so a rename inside the moved block counts as an edit.

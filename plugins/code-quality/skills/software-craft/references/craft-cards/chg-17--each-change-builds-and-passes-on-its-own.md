---
title: Every change, and every commit of a series that lands as separate commits, leaves the code building and its tests passing on its own, with no later change needed to make it build or pass
rule_id: CHG-17
domain: change
step: [implement, review]
applies_to: [universal]
triggers: ['(?i)\b(follow[- ]?up|next (commit|change|patch|pr|cl)|later (commit|change|patch)|subsequent (commit|change|patch)|temporar(y|ily) (broken|disabled))\b', '^\s*(import\s|from\s+[\w.]+\s+import\s|use\s+[\w:{]+|#include\s|require\()', '\b(def|fn|func|function|class|struct|interface|trait|enum|impl|type)\s+\w+', 'signal:todo_marker', 'signal:added_file']
scope: callers
check_kind: semantic
severity_default: major
---

# Every change, and every commit of a series that lands as separate commits, leaves the code building and its tests passing on its own, with no later change needed to make it build or pass

## Thesis
Every change, and every commit of a series that lands as separate commits, leaves the project building, running and passing its test suite at its own revision, working independently of any later commit. When changes depend on one another, the whole system keeps working after each one is submitted: each relies on no later change to build or pass, and none knowingly breaks something that a later change fixes.

## Rationale
Between the submissions of dependent changes, one that relies on a later change can break the build for every other developer for a few minutes, or longer if something goes wrong unexpectedly with the later submission. Bisection can split a series at any point, so every commit in it is a revision someone may build and run; one that does not build or run properly puts a bug in the middle of the series. When a string of commits cannot be tested and the regression was introduced by one of them, it is not possible to tell for sure which commit introduced it. Splitting work into small logical commits that each work on their own and pass the test suite makes review much easier and the history much more useful for later inspection and analysis, such as line-by-line blame and bisection.

## Example
```python
bad:  # commit 1 of 2 renames the definition; the next commit updates the caller
      def load_items(path): ...            # loader.py
      from loader import load_records      # report.py
      total = load_records(path)
good: # one commit renames the definition and updates every caller
      def load_items(path): ...            # loader.py
      from loader import load_items        # report.py
      total = load_items(path)
```

## Limits
Small or imperfect steps made along the way and edited before they are published, and commits added during review and squashed when the work lands, are outside the rule; the rule applies to each commit as it lands. A reviewer may accept a change on condition of a follow-up change that addresses a particular issue or concern; that follow-up is compatible with the rule provided the accepted change by itself leaves the project unbroken. A project that builds and tests changes after they are merged accepts an occasional broken build, since a contributor cannot reasonably build and test with every possible configuration; the author then fixes the build as soon as possible or reverts the change. That tolerance rests on configurations the contributor could not test and does not extend to a break knowingly left for a later commit to fix.

## Validator
Grep the hunk for removed, renamed or re-signed definitions, for added imports and uses of names, and for comments or messages that promise a follow-up, next or later change or call something temporarily broken. For each removed, renamed or re-signed element, open its callers at this change's revision and check that every reference is updated in the same change. For each added import or use, check that the element exists at this revision rather than arriving in a later change of the series. For each promise of a later fix, check whether this revision builds and passes its tests without it. Leave out commits that are squashed before landing, and a break in a configuration the author could not reasonably test where the project tests after merging. Validator question: **Does this change, at its own revision, keep a reference to an element it removes, renames or re-signs, use an element that only a later change provides, or knowingly leave a build or test failure for a later change to repair?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: CHG-17`, severity major, `file`, `symbol`, `code` = the stale reference, the premature use or the line that leaves the build or a test broken, quoted verbatim from the diff or, for a reference left in a caller the change does not touch, from that caller at this change's revision, `fix` = the change completed so that it builds and passes alone, with every reference updated or the used element added in the same change, in the file's language, `rationale` = which build step or test fails at this revision and which later change it relies on).

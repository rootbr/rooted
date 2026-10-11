---
title: A change that alters behaviour restructures no code beyond small cleanups such as renaming a local variable, and a larger restructuring such as moving or renaming a class goes in a change of its own
rule_id: CHG-12
domain: change
step: [implement, refactor, review]
applies_to: [universal]
triggers: ['\b(def|fn|func|function|class|struct|interface|trait|enum|impl|type)\s+\w+', '\b(def|public|protected|private|internal|static)\s+[\w<>\[\],.? ]*\w+\s*\(', '^\s*(import\s|from\s+[\w.]+\s+import\s|use\s+[\w:{]+|package\s+\w+|#include\s)', 'signal:added_file']
scope: base-compare
check_kind: semantic
severity_default: minor
---

# A change that alters behaviour restructures no code beyond small cleanups such as renaming a local variable, and a larger restructuring such as moving or renaming a class goes in a change of its own

## Thesis
A change that adds a feature or fixes a bug carries no refactoring large enough to make its review more difficult; such a refactoring, for example moving and renaming a class or renaming the methods of a class that is about to change in some other way, goes in a separate change from the feature or the fix. Small cleanups such as fixing a local variable's name may stay inside the feature or bug-fix change. Developer and reviewer judge when a refactoring is large enough to make the review more difficult, and the separation is the usual best practice rather than an absolute.

## Rationale
Reviewers understand the changes each change introduces much more easily when the refactoring and the feature or fix arrive separately. A single patch that fixes a critical security bug, rearranges a few structures and reformats the code has a good chance of being passed over, and the important fix lost. Understanding a review is more difficult when the changeset consists of multiple independent code differences, and over 40% of changes submitted for review at Microsoft could potentially be decomposed into multiple partitions. In five open-source projects, up to 15% of all bug fixes consisted of multiple tangled changes and on average at least 16.6% of all source files were incorrectly associated with bug reports; better change organization is the recommended remedy. In three large open-source projects totalling 26,523 revisions, a large number of refactoring revisions included bug fixes at the same time or were related to later bug-fix revisions, and mistakes in refactoring interleaved with behaviour-modifying edits were frequent. In a controlled experiment with 28 developers, decomposing a change led to fewer wrongly reported issues and more context-seeking, yet affected neither understanding of the change rationale nor the number of defects found.

## Example
```python
bad:  # one change moves Totals into billing/invoice.py as InvoiceTotals and fixes the rounding
      from billing.invoice import InvoiceTotals  # caller
      class InvoiceTotals:  # billing/invoice.py
          def total(self, items): return round(sum(i.price for i in items), 2)
good: # first change only moves and renames Totals, behaviour unchanged
      from billing.invoice import InvoiceTotals  # caller
      class InvoiceTotals:  # billing/invoice.py
          def total(self, items): return sum(i.price for i in items)
      # second change fixes only the rounding in InvoiceTotals.total
```

## Limits
The separating condition is the size of the restructuring, as developer and reviewer judge it. A small cleanup such as fixing a local variable's name may ride inside a feature or bug-fix change, and small spelling-consistency fixes are accepted inside a patch as a side effect of real work in the vicinity; programmers frequently intersperse refactoring with other program changes, which describes practice rather than recommending it. A refactoring large enough to make the review more difficult, with moving and renaming a class or renaming a class's methods as the documented examples, goes in a separate change. A series in which one commit does only the refactoring and the next commit adds the feature satisfies the rule. The rule does not reach the opposite case, a change presented as a refactoring that also alters behaviour, nor reformatting or unrelated fixes on their own.

## Validator
In the hunk, grep for added, removed or renamed declarations of classes, types, routines and methods, changed import or package lines, and added files. Open the base and the head of each touched file at base-compare and pair removed with added declarations to find a class or type that moved or was renamed, methods that were renamed, and routines extracted, inlined or moved between files. Trace whether the same change also alters behaviour: a changed condition, value or return path, a new branch or entry point, or a test asserting a new outcome. When the commits between base and head are available, judge each commit as its own change; a commit that only restructures followed by one that alters behaviour passes. Discount renames of a local variable and renames of a symbol the change itself introduces. Validator question: **Does one commit or change both alter behaviour and move, rename or restructure a class, type or method beyond a small cleanup such as renaming a local variable?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: CHG-12`, severity minor, `file`, `symbol`, `code` = the moved or renamed declaration line and the line whose behaviour changes, quoted verbatim from the diff, `fix` = the split into a change that only restructures followed by a change that only alters behaviour, shown in the file's language, `rationale` = names the restructuring, the behaviour change it is tangled with, and that reviewers understand each more easily when they arrive separately).

## Source
- google/eng-practices review/developer/small-cls.md §'Separate Out Refactorings' (fetched): "It's usually best to do refactorings in a separate CL from feature changes or bug fixes. For example, moving and renaming a class should be in a different CL from fixing a bug in that class. It is much easier for reviewers to understand the changes introduced by each CL when they are separate." … "Small cleanups such as fixing a local variable name can be included inside of a feature change or bug fix CL, though. It's up to the judgment of developers and reviewers to decide when a refactoring is so large that it will make the review more difficult if included in your current CL."
- Linux kernel Documentation/process/5.Posting.rst §'Patch preparation' (fetched): "do not mix different types of changes in the same patch. If a single patch fixes a critical security bug, rearranges a few structures, and reformats the code, there is a good chance that it will be passed over and the important fix will be lost."
- LLVM llvm/docs/CodingStandards.md §Introduction (fetched): "it is reasonable to rename the methods of a class if you're about to change it in some other way. Please commit such changes separately to make code review easier."
- kubernetes/community contributors/guide/pull-requests.md §'Breaking up commits' (fetched): "if you found that Feature-X needed some prefactoring to fit in, make a commit that JUST does that prefactoring. Then make a new commit for Feature-X."
- git Documentation/SubmittingPatches §typofixes (fetched): "with small and easily digestible patches, as a side effect of doing some other real work in the vicinity".
- Microsoft Research, ICSE 2015, https://www.microsoft.com/en-us/research/publication/helping-developers-help-themselves-automatic-decomposition-of-code-review-changesets/ (relayed): "Understanding a code review is more difficult when the changeset consists of multiple, independent code differences"; "over 40% of changes submitted for review at Microsoft can be potentially decomposed into multiple partitions".
- 'The impact of tangled code changes', MSR 2013, https://www.st.cs.uni-saarland.de/publications/files/herzig-msr-2013.pdf (relayed): "up to 15% of all bug fixes to consist of multiple tangled changes"; "on average at least 16.6% of all source files are incorrectly associated with bug reports"; "better change organization to limit the impact of tangled changes".
- DOI 10.1145/1985793.1985815, abstract (fetched): "a large number of refactoring revisions include bug fixes at the same time or are related to later bug fix revisions" … "frequent floss refactoring mistakes observed in this study call for new software engineering tools to support safe application of refactoring and behavior modifying edits together" — the study asks for tooling that makes the combination safe, not for separation.
- DOI 10.7717/peerj-cs.193, arXiv:1805.10978 (relayed): "Change decomposition leads to fewer wrongly reported issues, influences how subjects approach and conduct the review activity (by increasing context-seeking), yet impacts neither understanding the change rationale nor the number of found defects".
- DOI 10.1109/ICSE.2009.5070529, abstract (fetched): "programmers do frequently intersperse refactoring with other program changes".
- Caveat: the research measures tangled changes in general and their review and history costs; none compares defect rates of separated against combined refactoring and behaviour changes.

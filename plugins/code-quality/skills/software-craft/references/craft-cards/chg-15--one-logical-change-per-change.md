---
title: A change holds one logical change, so an independent fix, feature step or performance change that could be reviewed and verified on its own goes in a separate change, while one logical change spread over many files stays in one change
rule_id: CHG-15
domain: change
step: [implement, review]
applies_to: [universal]
triggers: ['\b(def|fn|func|function|class|struct|interface|trait|enum|impl)\s+\w+', '\b(if|elif|else|switch|match|case|for|while|return|throw|raise)\b', '(?i)\b(fix(es|ed)?|bug|workaround|hack|perf|optimi[sz]\w*|unrelated|drive[- ]by|clean[- ]?up)\b', 'signal:added_file']
scope: base-compare
check_kind: semantic
severity_default: minor
---

# A change holds one logical change, so an independent fix, feature step or performance change that could be reviewed and verified on its own goes in a separate change, while one logical change spread over many files stays in one change

## Thesis
Each change addresses just one thing, such as one bug fix, one part of a feature or one performance improvement, and is justifiable on its own merits. A logically independent change made in the same work goes in a separate change: a bug fix and a performance enhancement for the same component become two changes, and fixes for two separate issues become two changes. One logical change made to numerous files is grouped in a single change rather than split by file. One code change that fixes several issues at once counts as one change, and the implementation, documentation and tests of the same change are one logical change.

## Rationale
Combining multiple unrelated changes makes a change harder to review and notifies more people than necessary, and a diff with too many changes keeps the reviewer from seeing the forest for the trees. Understanding a review is more difficult when the changeset consists of multiple, independent code differences, and over 40% of the changes submitted for review at one company could potentially be decomposed into multiple partitions. Tangled changes can also compromise analyses of the version history through noise and bias, because they make all changes to all modules appear related. In five open-source projects up to 15% of all bug fixes consisted of multiple tangled changes, and on average at least 16.6% of all source files were incorrectly associated with bug reports. A logically independent change should be conceptually small and amenable to a one-line description, reviewable on its own and verifiable to do what it says it does; a description that starts to get too long is a sign that the change probably needs splitting into finer-grained pieces. The research measures reviewability and history quality and shows no gain in defect detection: in a controlled experiment with 28 developers, decomposed changes led to fewer wrongly reported issues and more context-seeking, and changed neither understanding of the change rationale nor the number of defects found.

## Example
```rust
bad:  // change 1: fix empty-slice underflow in last_index, and binary-search contains (perf)
      fn last_index(v: &[u32]) -> Option<usize> { if v.is_empty() { None } else { Some(v.len() - 1) } }
      fn contains(sorted: &[u32], k: u32) -> bool { sorted.binary_search(&k).is_ok() }
good: // change 1: fix empty-slice underflow in last_index
      fn last_index(v: &[u32]) -> Option<usize> { if v.is_empty() { None } else { Some(v.len() - 1) } }
      // change 2: binary-search contains (perf)
      fn contains(sorted: &[u32], k: u32) -> bool { sorted.binary_search(&k).is_ok() }
```

## Limits
Split changes may depend on one another, as an interface update and new code that uses that interface do; the dependent change notes the dependency in its description. This check flags only edits whose purposes are independent, so new code kept in one change with the interface update it needs is not flagged. Logical independence, not line count, decides the split: a logically independent change can be small, such as adding a field to a structure, or large, such as adding a significant new component, as long as it is conceptually small. A review unit that addresses one feature or one bug fix may hold several commits; the rule asks that the unit address one thing and that no single commit fix more than one issue. Drive-by reformatting, renames and structural tidying are judged by their own checks on diff minimality and on separating structure from behaviour; this check judges independent fixes, feature steps and performance changes that share one change.

## Validator
Grep the hunk for added or changed definitions and control-flow lines, and grep comments, the commit message and the change description for fix, perf, optimise, cleanup, unrelated or drive-by. Open every hunk of the change and name in one line the purpose each hunk serves. Trace each pair of purposes: whether one hunk calls, tests, documents or is required by the other, or whether one fixes the issue the change describes while the other fixes a different issue, speeds up other code or adds an unrelated feature step. Check whether the change description needs two independent clauses to say what the change does. Validator question: **Does the change carry two or more fixes, feature steps or performance changes with independent purposes, each of which could be reviewed and verified without the other, rather than one logical change with its tests and documentation?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: CHG-15`, severity minor, `file`, `symbol`, `code` = the first line of the hunk that serves the second, independent purpose, quoted verbatim from the diff, `fix` = the separate changes the diff splits into, each with its one-line description and the hunks it keeps shown in the file's language, `rationale` = the independent purposes found and that a tangled change is harder to review and links history to the wrong bug reports).

## Source
- Google Engineering Practices, review/developer/small-cls.md §"What is Small?" (fetched): "The CL makes a minimal change that addresses **just one thing**. This is usually just one part of a feature".
- Linux kernel Documentation/process/submitting-patches.rst §"Separate your changes" (fetched): "Separate each **logical change** into a separate patch. For example, if your changes include both bug fixes and performance enhancements for a single driver, separate those changes"; "if you make a single change to numerous files, group those changes into a single patch"; "Each patch should be justifiable on its own merits"; "If your changes include an API update, and a new driver which uses that new API, separate those into two patches"; "If one patch depends on another patch in order for a change to be complete, that is OK. Simply note **\"this patch depends on patch X\"** in your patch description."
- Linux kernel Documentation/process/5.Posting.rst §"Patch preparation" (fetched): "Each logically independent change should be formatted as a separate patch. These changes can be small (\"add a field to this structure\") or large (adding a significant new driver, for example), but they should be conceptually small and amenable to a one-line description. Each patch should make a specific change which can be reviewed on its own and verified to do what it says it does."
- git Documentation/SubmittingPatches §separate-commits (fetched): "If your description starts to get too long, that's a sign that you probably need to split up your commit to finer grained pieces."
- Python Developer's Guide, getting-started/pull-request-lifecycle.rst (fetched): "Combining multiple unrelated changes makes a pull request harder to review and increases the number of people notified unnecessarily"; "Each feature or bugfix should be addressed by a single pull request, and for each pull request there may be several commits"; "Do **not** fix more than one issue in the same commit (except, of course, if one code change fixes all of them)."
- Kubernetes community, contributors/guide/pull-requests.md §"Open a Different Pull Request for Fixes and Generic Features" (fetched): "Put changes that are unrelated to your feature into a different pull request. [...] Otherwise, your diff will have way too many changes, and your reviewer won't see the forest for the trees."
- GitLab, doc/development/code_review.md §"Participating in code review" (fetched): "Read through the entire diff before your first push. Check for unrelated changes and debug code."
- Node.js, doc/contributing/pull-requests.md §"Commit squashing" (fetched): "It touches the implementation, the documentation, and the tests, but is still one logical change."
- "The Impact of Tangled Code Changes", MSR 2013, abstract at raw.githubusercontent.com/rtholmes/conf-data/master/data/2013MSR.json (fetched): "When analyzing the version history, such tangled changes will make all changes to all modules appear related, possibly compromising the resulting analyses through noise and bias [...] up to 15% of all bug fixes to consist of multiple tangled changes [...] on average at least 16.6% of all source files are incorrectly associated with bug reports."
- "Helping developers help themselves: automatic decomposition of code review changesets", ICSE 2015, microsoft.com/en-us/research/publication/helping-developers-help-themselves-automatic-decomposition-of-code-review-changesets (relayed): "Understanding a code review is more difficult when the changeset consists of multiple, independent code differences [...] over 40% of changes submitted for review at Microsoft can be potentially decomposed into multiple partitions."
- arXiv:1805.10978, DOI 10.7717/peerj-cs.193 (relayed): "a controlled experiment [...] involving 28 software developers [...] Change decomposition leads to fewer wrongly reported issues, influences how subjects approach and conduct the review activity (by increasing context-seeking), yet impacts neither understanding the change rationale nor the number of found defects."
- Caveat: the tangling rates come from five open-source Java projects and the decomposition rate from one company's review data; the one controlled experiment found no effect of decomposition on the number of defects found.

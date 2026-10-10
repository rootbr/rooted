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

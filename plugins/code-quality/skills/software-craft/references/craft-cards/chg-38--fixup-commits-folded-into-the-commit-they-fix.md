---
title: Before a series lands as separate commits, each commit that only fixes an earlier commit of the same series, such as a fixup!, squash! or amend! commit or one addressing review feedback or a typo in it, is folded into the commit it fixes, while independent layered commits stay separate
rule_id: CHG-38
domain: change
step: [implement, review]
applies_to: [universal]
triggers: ['\b(def|fn|func|function|class|struct|interface|trait|enum|impl)\s+\w+', '\b(if|elif|else|switch|match|case|for|while|return|throw|raise)\b', 'signal:added_file']
scope: base-compare
check_kind: semantic
severity_default: minor
---

# Before a series lands as separate commits, each commit that only fixes an earlier commit of the same series, such as a fixup!, squash! or amend! commit or one addressing review feedback or a typo in it, is folded into the commit it fixes, while independent layered commits stay separate

## Thesis
When a series lands as separate commits, each commit in it that only fixes an earlier commit of the same series not yet merged into a branch that others build on (one that fixes a bug in it, addresses review feedback on it, corrects a typo in it, rewrites code it added, or carries a title that starts with `fixup! `, `squash! ` or `amend! `) is folded into the commit it fixes. The series then lands in its final form, not as the path taken to reach it, while independent changes layered toward a single goal stay separate commits.

## Rationale
A commit that only repairs an earlier commit of the same series leaves that earlier commit in history with its mistake, next to a second commit that corrects it. Commit messages are meant to be a record of the what and why of a change, and a message such as "Address review comments" adds no real value in communicating either. Developers reading a series are interested in discrete, self-contained changes, not in the path taken to reach them, and each change is one that can be reviewed on its own and verified to do what it says it does. Folding the repair into the commit it repairs presents a logical progression without the earlier mistakes. The history stays clean and easy to follow, and bisectability is preserved because partial rewrites are gone. A title that starts with `fixup! `, `squash! ` or `amend! ` names the earlier commit it modifies, so the version-control tool's autosquash moves it right after that commit and folds it in automatically. Independent changes layered toward a single goal stay separate, since each logically independent change is formatted as its own commit: writing a code transformer could be one commit, applying it another, and adding a pre-commit check that keeps its output from going out of date a third.

## Example
```java
bad:  // commit 1: Add Invoice.total()
      class Invoice { int sum, discount, tax; int total() { return sum - discount; } }
      // commit 2: fixup! Add Invoice.total()
      int total() { return sum - discount + tax; }
      // commit 3: Call Invoice.total() from Receipt
good: // commit 1: Add Invoice.total()
      class Invoice { int sum, discount, tax; int total() { return sum - discount + tax; } }
      // commit 2: Call Invoice.total() from Receipt
```

## Limits
The rule is contested on when the fold happens. It binds the series as it is set to land; a push made during review falls outside it only where the project states that fix-ups stay separate until landing. One side folds at every posted iteration: early iterations "are expected to be full replacements", and in a pull request "No fixup or merge commits are allowed". The other side keeps fix-ups separate while review runs ("Make the fixups, and don't squash yet"), may ask for the clean-up "at the very end", "typically at the point where the pull request would otherwise be tagged LGTM", or requires that fix-up commits be squashed "before landing the PR". Both sides agree on what lands. So a series still in review under a stated keep-until-landing policy is outside the rule. One project's merge-request check enforces the same end state as soon as a request leaves draft: it fails a fixup commit on a merge request that is not a draft, only warns on a draft, and ignores the commit when the request squashes on merge. A change the project lands by squash merge is outside the rule, because the squash folds the fix-ups. A project configured to always squash lands each pull request as exactly one commit and lands related changes as stacked pull requests. History that others build on is outside the rule as well. Once a topic is merged to an integration branch, further changes go on top "with another commit". History exposed beyond a private system "should usually not be changed", because "Others may have pulled a copy of your tree and built on it"; a branch exposed only for review or testing, whose prospective users "know not to base work on it", stays inside the rule. With few exceptions a broken commit in a tree holding others' history should be "explicitly reverted" rather than removed by rewriting history. The counter-position, from a version-control system that omits rebase by design, holds that "A wish for collapsed, finalized check-ins is a wish for a counterfactual situation", one in which development shows "no false starts, no mistakes", and that rebasing "deliberately omits historical information". A project whose stated policy keeps every commit is outside the rule.

## Validator
List the commits between base and head in order with their titles. Grep each title for `^(fixup|squash|amend)! ` and match the rest of the title to an earlier commit of the series. For every other commit, open its diff and trace each changed line to the commit of the series that added it. A commit whose changes only repair, retouch or rewrite lines an earlier commit of the series added is a fix-up, whether it fixes a bug, applies review feedback or corrects a typo. A commit that adds its own step toward the goal is a layer. Read the change description and the project's contributing guide, and stop without a finding in four cases: the change lands by squash merge; it is still in review under a stated policy that keeps fix-ups separate until landing; the commit it fixes is already merged into a branch that others build on, a branch pushed only for review not counting; or the project's stated policy keeps every commit. Validator question: **Does the series, as it is set to land as separate commits, contain a commit that only fixes an earlier unmerged commit of the same series or whose title starts with `fixup! `, `squash! ` or `amend! `?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: CHG-38`, severity minor, `file`, `symbol`, `code` = the fix-up commit's short hash and title verbatim with the lines it changes, `fix` = the commit it fixes as it lands with the fix-up folded in, its lines shown in the file's language under that commit's title, `rationale` = names the earlier commit of the series that the fix-up repairs and states that the series lands in its final form while layered commits stay separate).

---
title: A change description states the problem that motivates the change and why the change solves it this way, so that a bug number, a link or a phrase such as 'fix bug' does not stand in for that statement
rule_id: DOC-07
domain: docs
step: [document, review]
applies_to: [universal]
triggers: ['\b(def|fn|func|function|class|struct|interface|trait|enum|impl)\s+\w+', '\b(if|elif|else|switch|match|case|for|while|return|throw|raise)\b', 'signal:added_file']
scope: base-compare
check_kind: semantic
severity_default: minor
---

# A change description states the problem that motivates the change and why the change solves it this way, so that a bug number, a link or a phrase such as 'fix bug' does not stand in for that statement

## Thesis
Every change description, beyond its summary line, states the problem the change solves, that is what is wrong with the code without the change, and why the change solves it this way, including decisions that the code does not show. A bug number, a link to a tracker or a discussion, "fix bug" or "version N of the patch" is a reference that may sit beside that statement and does not replace it. The rule holds for a change of any size from a one-line bug fix up, and exempts only an extremely trivial change such as a typo fix.

## Rationale
Source code may show what the software does and still not show why it exists, and the description becomes a permanent part of the version history, where reviewers and later readers look for why the change was made. A reference does not carry that reason to them: a linked resource may be invisible to later readers through access restrictions or retention policies, and some reviewers may never have received the earlier versions of a patch that a "version N" note points back to. In an analysis of developer survey responses and code review comments, missing rationale was the most frequent of 30 reasons for confusion in code review (66 of 507 coded cards, ahead of the non-functional discussion of the solution with 49 and lack of familiarity with existing code with 47), and developers report that confusion delays the merge decision, decreases review quality and results in additional discussions. A survey of software designers, testers and managers in industry found rationale the most important information for understanding a code change, with respondents saying that code changes can be easily understood if a good description is provided. Stating the problem lets the reviewer see that it is worth fixing, and justifying the approach lets the reviewer see why the result with the change is better.

## Example
```go
bad:  func description() string {
          return "store: fix bug\n\nFixes #123"
      }
good: func description() string {
          return "store: retry a write once when the connection drops\n\n" +
              "Without the retry, a dropped connection loses the caller's record.\n" +
              "One retry is safe because each write carries an idempotency key.\n\nFixes #123"
      }
```

## Limits
An extremely trivial change, such as a typo fix, needs no stated rationale; size alone does not exempt a change, since a one-line bug fix also has an underlying problem that motivated it. Where relevant, bug numbers, benchmark results and links to design documents belong in the description as background next to the statement of problem and reason. Linter rules that report a missing commit description (checkpatch COMMIT_MESSAGE, gitlint body-is-missing) or a body shorter than a minimum (gitlint body-min-length, 20 characters by default) test that a body is present and long enough, which a body of references alone can satisfy; whether the body states the problem and the reason takes a reading of the text.

## Validator
Read the change description verbatim: the messages of the commits under review (read-only `git log --format=%B <base>..<head>`), or the body of the review request when the review target is one; a summary of intent supplied with the review, or the task the code was written for, is not a change description. When no commit message or review-request body exists for the diff, as for an uncommitted working tree, there is no description to judge: return no finding. Set aside the description's summary line, its trailers and tags (Fixes, Closes, Link, Signed-off-by), bare bug or issue numbers, URLs, and phrases such as "fix bug", "address comments" or "version N". Read what remains for two statements: what is wrong with the code without the change, and why this change solves it this way. Pass the change when its hunks only correct a typo or similar extremely trivial text. Validator question: **Does the description of a change that does more than correct a typo or similarly trivial text, once its summary line, bug numbers, links and trailers are set aside, lack a statement of the problem the change solves or lack a statement of why it solves it this way?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: DOC-07`, severity minor, `file`, `symbol`, `code` = the first added line of the first matched hunk verbatim, as the finding's anchor in the diff, `fix` = a description body for this change that states what is wrong without it and why this approach solves it, with the bug reference kept as a trailer, `rationale` = the description's summary line and body quoted verbatim, which of the two statements is missing and that a bug number, link or "fix bug" is a reference that does not supply it).

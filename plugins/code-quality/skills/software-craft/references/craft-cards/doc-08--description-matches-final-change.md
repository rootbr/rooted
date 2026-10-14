---
title: A change description describes the change as it is merged, stating nothing its diff does not do and omitting no significant part of what the diff does, after any revision review brought
rule_id: DOC-08
domain: docs
step: [review]
applies_to: [universal]
triggers: ['\b(def|fn|func|function|class|struct|interface|trait|enum|impl)\s+\w+', '\b(if|elif|else|switch|match|case|for|while|return|throw|raise)\b', 'signal:added_file']
scope: base-compare
check_kind: semantic
severity_default: minor
---

# A change description describes the change as it is merged, stating nothing its diff does not do and omitting no significant part of what the diff does, after any revision review brought

## Thesis
Before a change merges, its description — each commit message for the diff of its own commit, and the pull or change request title and body for the diff of the whole change — accurately and fully explains the code change being made in that diff, and still reflects what the change does after review has changed it. Each submission and each resubmission carries the complete description and its justification, self-contained, rather than only saying it is version N of the change. A generated summary that serves as the description is reviewed carefully by the author, who adds the context only the author knows.

## Rationale
A change can undergo significant change during review, so the description is reviewed before the change is submitted, to ensure it still reflects what the change does. Review-thread comments are not represented in the commit history: the commit messages are the permanent record of the change and should describe both what is done and why. A description that says only "version N" expects the maintainer to refer back to earlier versions or referenced URLs to find the description and put it into the change, and some reviewers probably never received those earlier versions; a self-contained description benefits both maintainers and reviewers. Review covers the commit message for correctness and clarity, in addition to the code change in the diff.

## Example
```rust
bad:  // Description: Retry the fetch up to three times with backoff.
      // (v2: see the earlier thread for details)
      fn fetch(url: &str) -> Result<Body, FetchError> {
          fetch_once(url)
      }
good: // Description: Return the first fetch error to the caller, which picks the retry policy.
      fn fetch(url: &str) -> Result<Body, FetchError> {
          fetch_once(url)
      }
```

## Limits
The description also carries supplemental information a reader needs to understand the change holistically — the problem being solved, why the approach is the best one, any shortcomings of the approach, and background such as bug numbers, benchmark results and links to design documents; such context belongs in an accurate description and is not a statement of something the diff does. A description that starts to get long is a sign the change probably needs splitting, which is a question of the change's size rather than of its description. The rule reaches the change's commit messages and its pull or change request title and body; comments in the review thread, which the commit history does not represent, are outside it.

## Validator
Read the change's description at scope base-compare: the message of each commit between base and head, and the pull or change request title and body when the review supplies them; when none is supplied, stop. List each statement the description makes about what the change does. Compare each commit message against that commit's own diff, and the pull or change request title and body against the diff from base to head; for each statement, find the hunks that carry it out, then, for each behaviour the compared diff adds, removes or changes, find the statement that explains it. Read supplemental context — the problem, the reason for the approach, its shortcomings, bug numbers, benchmark results, design-document links — as context, not as a claim to match against hunks. Check whether the description leaves any part of what the change does or why to a version marker or a pointer to an earlier version, a review thread or a URL. Validator question: **Does the description state a change the diff does not make, leave a significant behaviour of the diff unexplained, or rely on an earlier version, thread or URL for its content?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: DOC-08`, severity minor, `file`, `symbol`, `code` = the description sentence the diff does not bear out or that defers content to an earlier version, a review thread or a URL, or the signature line of the change the description leaves out, quoted verbatim, `fix` = the revised description sentence, for the commit message or the pull or change request title and body, that states in full what the diff does and why, shown above the routine's signature in the file's language, `rationale` = the mismatch it names: a stated change absent from the diff, a behaviour of the diff absent from the description, or content deferred to an earlier version, a review thread or a URL).

## Source
- Git project, `Documentation/ReviewingGuidelines.adoc`, "High-level guidance" (fetched): "Remember to review the content of commit messages for correctness and clarity, in addition to the code change in the patch's diff. The commit message of a patch should accurately and fully explain the code change being made in the diff."
- Google Engineering Practices, `review/developer/cl-descriptions.md`, "Review the description before submitting the CL" (fetched): "CLs can undergo significant change during review. It can be worthwhile to review a CL description before submitting the CL, to ensure that the description still reflects what the CL does."; "Body is Informative": "include any supplemental information a reader needs to understand the changelist holistically. It might include a brief description of the problem that's being solved, and why this is the best approach. If there are any shortcomings to the approach, they should be mentioned. If relevant, include background information such as bug numbers, benchmark results, and links to design documents."
- Rust compiler team review policy, `rust-forge src/compiler/reviews.md`, "Checklist for reviewers", "Before merging" (fetched): "Is the PR title and description still accurate?"
- Linux kernel, `Documentation/process/submitting-patches.rst`, "Describe your changes" (fetched): "When you submit or resubmit a patch or patch series, include the complete patch description and justification for it. Don't just say that this is version N of the patch (series). Don't expect the subsystem maintainer to refer back to earlier patch versions or referenced URLs to find the patch description and put that into the patch. I.e., the patch (series) and its description should be self-contained. This benefits both the maintainers and reviewers. Some reviewers probably didn't even receive earlier versions of the patch."; "If your description starts to get long, that's a sign that you probably need to split up your patch."
- Kubernetes community, `contributors/guide/pull-requests.md`, "Commit Message Guidelines" (fetched): "PR comments are not represented in the commit history. Commits and their commit messages are the "permanent record" of the changes being done in your PR and their commit messages should accurately describe both what and why it is being done."
- GitHub Docs, `content/pull-requests/concepts/helping-others-review-your-changes.md`, "Keeping your team informed", "Use GitHub Copilot to generate pull request summaries" (fetched): "A generated summary can help reviewers understand the main changes, but you should review it carefully and add context that only you know."
- Caveat: all six are project contribution and review guidelines that prescribe the practice; none reports a measured defect or cost outcome.

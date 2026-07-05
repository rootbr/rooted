---
title: Cited code or text must be re-checked against the current source before emitting the patch
rule_id: R-46
applies_to_target: [context-file, skill, agent-prompt]
check_kind: semantic
severity_default: info
---

# Cited code or text must be re-checked against the current source before emitting the patch

## Thesis
Before proposing a fix that names a file, class, function, or external section, verify the named entity still exists. A reference to a paper, RFC, or book section passes (you cannot fetch every source mid-audit); a reference to a repo entity must be confirmed by grepping for the symbol before the reference is kept.

## Rationale
Memory recall is not ground truth: "the memory says X exists" is not the same as "X exists now." An audit that proposes "see UserService" when `UserService` was renamed last week is worse than no proposal — it sends the reader to a dead pointer and erodes trust in every other suggestion.

## Example
```
bad:  proposed: "see OrderService#findById"   (symbol no longer in the repo)
good: grep -rn "OrderService" first; absent → severity "info", needs_human, proposed: null
```

## Limits
Applies only to repo-internal pointers, which can be checked with the tools available at audit time. External-source citations are exempt from the existence check because the source cannot be fetched mid-audit; their stability is a separate concern.

## Validator
For every repo-internal pointer the audit *proposes*, search the repo for `<symbol>` with the `Grep` tool. Where the proposed pointer names an entity that no longer exists, downgrade severity to `info` and emit a clarification patch asking the human reviewer to supply the new name. Validator question: does the symbol I am proposing to point at exist in the current repo state?

## Patch output
When a proposed repo-internal pointer names an entity that grep cannot find, emit one patch (`rule_id: R-46`, location of the reference, severity info, `proposed: null`, `needs_human: true`) asking the reviewer to supply the current name.

## Source
Verified hands-on experience: a proposed pointer to a renamed symbol is worse than no proposal; grep before keeping it.

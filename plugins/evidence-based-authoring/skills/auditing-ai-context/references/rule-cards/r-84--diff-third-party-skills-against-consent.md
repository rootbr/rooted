---
title: Third-party skills must be diffed against the last-consented version before re-install
rule_id: R-84
applies_to_target: [skill]
check_kind: semantic
severity_default: medium
---

# Third-party skills must be diffed against the last-consented version before re-install

## Thesis
When a file documents a workflow for installing or updating third-party skills, that workflow must prescribe a diff against the last-consented version before the update is accepted.

## Rationale
Trust binds to identity, not to content: a user consents to a skill at install time, so any content change made after that consent is unconsented and bypasses the original review. A per-edit diff against the last-consented version is the defense — it surfaces the post-install change for a fresh decision instead of letting it ride on the stale consent. A marketplace scan pass does not substitute for the diff: install-time scanners are defeatable — payload-preserving self-extracting packing bypassed all eight scanners tested at over 90% — so "it passed the scan" is not evidence that an update is safe.

## Example
```
bad:  "Pull the latest version of the community skill and enable it."
good: "Diff the new version against the last-consented one; re-review
      changes and re-consent before enabling."
```

## Limits
Applies to files that document installing community skills or accepting skill updates. A file that neither installs nor updates third-party skills is out of scope. The diff surfaces the change for review; it does not by itself judge the change safe.

## Validator
If the file mentions installing community skills or accepting skill updates, look for a diff-against-last-consented-version instruction. If absent, flag. Validator question: before any third-party skill update is accepted, is there an explicit diff against the last version the user consented to?

## Patch output
When auditing an install or update instruction with no consent diff, emit one patch (`rule_id: R-84`, `location.section` = heading, severity medium) proposing the same instruction with an explicit diff against the last-consented version; set `needs_human: true` when accepting the diff requires a human review decision.

## Source
Li 2604.02837 §3.3 (trust binds to identity; post-install content changes bypass consent); Ji 2607.02357 abstract (self-extracting-skill packing bypasses all eight tested scanners at >90% — install-time scanning is defeatable).

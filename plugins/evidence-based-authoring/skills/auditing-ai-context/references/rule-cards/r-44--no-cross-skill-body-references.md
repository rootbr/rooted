---
title: Cross-skill body references must not appear; descriptions must be self-contained
rule_id: R-44
applies_to_target: [context-file, skill, agent-prompt]
check_kind: semantic
severity_default: high
---

# Cross-skill body references must not appear; descriptions must be self-contained

## Thesis
A SKILL.md may not assume another skill's body is loaded. A cross-reference that reads "see <other-skill> for the stable-anchor rules" is inert at routing time — the referenced body is not in context until that other skill's tool fires.

## Rationale
The skill tool lazy-loads each skill's body on its own activation; the router sees only the frontmatter description. Inside a sibling skill's body you cannot rely on a peer's body being available — even if it loaded earlier in the session, compaction or sub-agent forking may have evicted it. A pointer into an unloaded body therefore resolves to nothing when the reader needs it.

## Example
```
bad:  Follow the placeholder rules from <other-skill>.
good: Use generic placeholders for illustrative code (Class#method form, not real names). See ../references/<file>.md for rationale.

bad:  Defer to <other-skill>/SKILL.md on sourcing.
good: Every rule must trace to a peer-reviewed paper, standard, or dated hands-on note. (Self-contained.)
```

## Limits
A description-level mention in frontmatter ("complements <other skill>") is acceptable when the other skill's *existence* is the relevant fact, not its body content. The violation is a body-level claim that depends on the other body's content; such a claim must be inlined or moved to a shared reference file under the calling skill.

## Validator
Grep for "see <skill-name>", "as documented in <skill-name>/SKILL.md", or any reference to another SKILL.md inside instruction prose. Classify each hit: a description-level existence mention is acceptable; a body-level dependency must be inlined or relocated. Validator question: if the reader has only this file in context — never having loaded the cross-referenced skill — can they still apply the rule? If no, inline it or move it into this skill's own references.

## Patch output
When auditing a body-level reference that depends on another skill's body, emit one patch (`rule_id: R-44`, location of the reference, severity high) proposing the inlined rule or a pointer to this skill's own references file.

## Source
Liu 2604.14228 §6.3 (the skill tool lazy-loads each skill's body on its own activation; the router sees only the description).

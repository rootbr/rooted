---
title: The description is self-contained — no cross-file references, deixis, or citations
rule_id: R-04
applies_to_target: [skill, agent-prompt]
check_kind: mechanical
severity_default: high
---

# The description is self-contained — no cross-file references, deixis, or citations

## Thesis
At routing time the `description` is the only text the router sees. It must not contain `see <other-file>`, "as documented in…", "this skill", pronouns referring to absent context, or paper citations — every dangling reference is opaque.

## Rationale
Two failure modes: the router cannot follow a pointer to a file that is not loaded, and "this skill" is meaningless when dozens of descriptions are pasted side by side in the router prompt. A cross-skill body reference is inert until that other skill fires. The description must read as standalone third-person prose.

## Example
```
bad:  "Audits agent files using rules from Yang 2505.13360. See references/ for the set."
good: "Audits CLAUDE.md, SKILL.md, and agent prompts for budget, routing, and sourcing."
```

## Limits
Covers the `description` field; in-body citations are governed by sourcing checks, not this one. A proper-noun product or file the skill genuinely operates on (named, not pointed-to) is allowed.

## Validator
Search the description for `see `, `documented in `, `as described `, `this skill `, `this tool`, `our `, a citation pattern like `(Author 2025)`, or file paths. Each is a candidate. Test: cut the description into a fresh chat — does it still parse as a complete what / when / not-for?

## Patch output
When auditing the `description` of a skill or agent-prompt, emit one patch (`rule_id: R-04`, `location.field: description`, severity high) rewriting it as standalone prose with the dangling reference removed; set `needs_human: true` when removing the reference would drop information the description needs.

## Source
Liu 2604.14228 §6.1, §6.3 (skills lazy-load on activation, so a cross-skill reference is inert until that skill fires); the rest follows from routing mechanics (the router sees only the description, with dozens pasted side by side).

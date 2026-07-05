---
title: A skill description is third-person, within 1024 characters, XML-free, and names both when to trigger and when not to
rule_id: R-02
applies_to_target: [skill, agent-prompt]
check_kind: mechanical
severity_default: high
---

# A skill description is third-person, within 1024 characters, XML-free, and names both when to trigger and when not to

## Thesis
The frontmatter `description` is pasted verbatim into the routing model's prompt. It must read as third-person prose, be non-empty, fit within 1024 characters, contain no XML tags, and explicitly name (a) what the skill does, (b) contexts that should trigger it, and (c) at least one should-not-trigger context.

## Rationale
Third person is the canonical routing voice — "I…" or "you use this to…" degrades routing because routers were trained on third-person descriptors. A description over 1024 characters or containing XML tags is auto-rejected — and markup-like text in an always-loaded field can smuggle unintended instructions into the routing prompt. Negative triggers ("NOT for Vue or Svelte") are the one place where prohibitions help: they shrink the should-trigger basin and stop adjacent skills from stealing activations — the practical safeguard while multi-skill conflict resolution stays underdeveloped.

## Example
```
bad:  "I help you write better SKILL.md files."     (first person)
good: "Audits SKILL.md, CLAUDE.md, and agent prompts; use whenever… NOT for…"
```

## Limits
Covers the `description` field only; body routing vocabulary and body/description scope consistency are separate checks. The 1024-character ceiling is a hard platform constraint; the third-person and trigger guidance is convention.

## Validator
(1) Count characters — empty or over 1024 → flag. (2) XML tags (`<…>`) anywhere in the description → flag. (3) First/second person ("I", "you", "we", "my") → flag. (4) No trigger phrasing ("use when / whenever", an intent list) → flag. (5) No negative trigger ("NOT for", "do not use for") → flag. Test: can a stranger reading only this description decide whether the skill should fire on a given prompt?

## Patch output
When auditing the `description` of a skill or agent-prompt, emit one patch (`rule_id: R-02`, `location.field: description`, severity high) that names the specific failure (too long | first-person | missing trigger list | missing NOT-for) and supplies a rewritten description; set `needs_human: true` when phrasing the triggers needs domain knowledge.

## Source
Anthropic, Agent Skills best practices (frontmatter spec: description non-empty, ≤1024 characters, no XML tags — violations auto-rejected); Dong 2512.14754 §2.2 (reliable@10 — up to 61.8 pp collapse); Xu & Yan 2602.12430 §7 (multi-skill conflict resolution underdeveloped → disjoint descriptions).

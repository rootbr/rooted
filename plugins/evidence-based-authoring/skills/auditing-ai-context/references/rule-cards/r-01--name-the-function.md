---
title: Name the skill by the function it performs, not its topic or asset type
rule_id: R-01
applies_to_target: [skill, agent-prompt]
check_kind: semantic
severity_default: high
---

# Name the skill by the function it performs, not its topic or asset type

## Thesis
The directory name and the frontmatter `name` must name the function performed — a verb + object, or a tool + mode — not the domain or asset type the skill operates on. The name must also satisfy the platform frontmatter spec: at most 64 characters, lowercase letters, numbers, and hyphens only, no XML tags, and no reserved words ("anthropic", "claude").

## Rationale
The `name` spans 3.0% of a skill's tokens but draws 26.3% of router attention, so its per-token influence is outsized: a topic-named skill loses routing duels to a function-named alternative even when its body is more specific. In retrieval studies a surface-topic name lost the task outright (0/12) where the function-named gold skill, once routed, succeeded (9/12; 12/12 in a second case).

## Example
```
bad:  java-skill           good: reviewing-java
bad:  pdf-helper           good: pdf-extraction
```

## Limits
Covers the name / identity only — routing vocabulary in the body is a separate check. A tool+mode name (e.g. `trivy-offline-scanning`) is a function name, not a topic. "Name the function" is an authoring inference from retrieval-quality measurements, not a tested rename — and the measurements come from a large registry with heavy overlap: the same study's negative case shows a topic/vocabulary-matching baseline beating the function-oriented router in highly specialized multi-skill domains (top-1 8/12 vs 4/12), and its limitations note metadata-only routing may be more competitive in smaller catalogs. In a small or highly specialized catalog, treat the rename as a default, not a hard rule.

## Validator
Spec check first: name over 64 characters, characters outside lowercase letters / digits / hyphens, XML tags, or the reserved words "anthropic" / "claude" → flag (hard platform constraint). Then decompose the name: does it carry (a) a verb or gerund (the function) and (b) a disambiguating qualifier (tool, mode, target type)? If it is only domain words ("auditing", "research", "documents") with no function → flag. Test: reading the name alone, can a router infer what action is performed, on what input, and what distinguishes it from a sibling?

## Patch output
When auditing the `name` of a skill or agent-prompt, emit one patch (`rule_id: R-01`, `location.field: name`, severity high) proposing a verb- or tool-anchored name; set `needs_human: true` when the right function word is ambiguous.

## Source
SkillRouter 2603.22455 App. C (`name` = 3.0% of tokens / 26.3% of router attention); App. L.1 (retrieval case studies — they measure retrieval quality, not renames; Case C is the specialized-domain counter-case, 8/12 vs 4/12); its Limitations (claims scoped to large registries with heavy overlap); Anthropic, Agent Skills best practices (frontmatter spec: name ≤64 chars, lowercase/numbers/hyphens only, no XML tags, no reserved words).

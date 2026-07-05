---
title: Topology is rendered as arrow-notation text, not Mermaid or ASCII art
rule_id: R-23
applies_to_target: [context-file, skill, agent-prompt]
check_kind: mechanical
severity_default: low
---

# Topology is rendered as arrow-notation text, not Mermaid or ASCII art

## Thesis
Describe data flow, hierarchies, and process diagrams using compact text notation — `A → B → C[]`, `Hierarchy: parent → child → grandchild`, `Flow: ingest → parse → emit` — rather than Mermaid fences or ASCII boxes.

## Rationale
Mermaid appears in only 2 of 328 surveyed instruction files: it is not the convention, and the model derives less from a rendered diagram than from arrow-notation prose.

## Example
```
bad:  a mermaid fence: graph LR; A --> B --> C
good: Flow: A → B → C
```

## Limits
Covers diagram rendering only. A diagram that is genuinely load-bearing and cannot be linearized may warrant author review rather than a silent rewrite, but arrow notation covers the common flow, hierarchy, and pipeline cases.

## Validator
Search for Mermaid fences (` ```mermaid `) and large ASCII boxes. For each occurrence, propose the equivalent text-arrow notation.

## Patch output
When a Mermaid fence or ASCII diagram appears, emit one patch (`rule_id: R-23`, `location.section` + `line_hint`, `current` = the diagram, severity low) proposing the arrow-notation text equivalent.

## Source
Santos Section 5 (Mermaid found in only 2 of 328 surveyed files).

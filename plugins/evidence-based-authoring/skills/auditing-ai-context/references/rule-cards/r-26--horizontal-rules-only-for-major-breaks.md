---
title: Horizontal rules separate top-level sections only, not every paragraph
rule_id: R-26
applies_to_target: [context-file, skill, agent-prompt]
check_kind: mechanical
severity_default: low
---

# Horizontal rules separate top-level sections only, not every paragraph

## Thesis
A `---` horizontal rule separates top-level sections, not every paragraph or subsection.

## Rationale
Decorative rules consume vertical attention without adding hierarchy beyond what headings already provide.

## Example
```
bad:  ### Sub-A \n --- \n ### Sub-B \n --- \n ### Sub-C
good: ## Section A \n --- \n ## Section B
```

## Limits
Covers `---` horizontal rules only, not headings or emphasis. A rule count at or below the H2 count is within convention; the signal is rules outnumbering top-level sections.

## Validator
Count `---` lines and compare to the number of H2 headings. If the horizontal rules outnumber the H2 headings, flag the ones between H3-level subsections for pruning.

## Patch output
When horizontal rules outnumber H2 headings, emit one patch (`rule_id: R-26`, `location.section` + `line_hint`, `current` = `---`, severity low) deleting the decorative rule and relying on the H2 heading for separation.

## Source
Chatlatanagulchai 2509.14744 (horizontal-rule convention; decorative rules add no hierarchy beyond headings).

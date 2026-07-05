---
title: Header hierarchy stays flat, with two to three levels typical and H4 rare
rule_id: R-20
applies_to_target: [context-file, skill, agent-prompt]
check_kind: mechanical
severity_default: low
---

# Header hierarchy stays flat, with two to three levels typical and H4 rare

## Thesis
Use H1 for major domains, H2 for components, and H3 for details. An H4 or deeper heading is a yellow flag — it usually means a component should be split into its own H2.

## Rationale
Deep nesting fragments the reader's mental model. The empirical median across 253 surveyed instruction files is H1=1, H2=5, H3=9; H4 appears in fewer than 15% (37/253), so deeply nested structures are rare in the wild.

## Example
```
bad:  # Domain / ## Component / ### Detail / #### Sub-detail
good: # Domain / ## Component (promoted) / ### Detail (promoted)
```

## Limits
Covers heading depth only. An occasional H4 is tolerable; the signal is structural drift, not a single deep heading. Whether the parent component truly warrants its own top-level section is an authoring judgement the count only prompts.

## Validator
Count headings by level to build a histogram (`H1=N, H2=N, H3=N, H4=N, ...`). If any H4 or deeper heading appears, examine the parent H3: would it work as a top-level component (H2) with its H4s promoted to H3? Flag each H4+ occurrence.

## Patch output
When an H4 or deeper heading appears, emit one patch (`rule_id: R-20`, `location.section` = the H4 heading, severity low) proposing to promote the parent H3 to H2 and this H4 to H3.

## Source
Chatlatanagulchai 2509.14744 (median across 253 files H1=1, H2=5, H3=9; H4 in 37/253, under 15%).

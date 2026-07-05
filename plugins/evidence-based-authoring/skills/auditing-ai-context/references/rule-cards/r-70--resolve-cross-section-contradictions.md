---
title: Contradictions across sections must be resolved into one rule with explicit conditions
rule_id: R-70
applies_to_target: [context-file, skill, agent-prompt]
check_kind: semantic
severity_default: high
---

# Contradictions across sections must be resolved into one rule with explicit conditions

## Thesis
When two sections of the same file prescribe different actions for what appears to be the same situation, the file is in a contradictory state. Either the situations actually differ and the rules need explicit conditions to make the distinction visible, or one rule is stale and must be deleted.

## Rationale
The model treats both rules as authoritative and oscillates between them, or picks whichever its positional bias favors — a primacy effect that is documented. Reader trust collapses once the rules visibly contradict each other.

## Example
```
bad (A): "All architecture lives in CLAUDE.md."
bad (B): "Architecture details belong in dedicated reference files."
good:    "Cross-cutting architecture → CLAUDE.md; domain detail → references/architecture-<domain>.md."
```

## Limits
Covers conflicts between rules that share the same subject within one file. Two rules that govern genuinely different situations are not a contradiction once their conditions are made explicit; the patch is to add the distinguishing condition, not to delete either rule.

## Validator
From the discovery inventory, retrieve the normative claims grouped by topic. For each cluster sharing the same subject (e.g. "where architecture lives", "how to cite sources"), check whether the prescribed actions are consistent. If two clusters prescribe conflicting actions for the same situation, flag. Validator question: could a reader follow both rules at once, or must they choose?

## Patch output
When two sections prescribe conflicting actions for the same situation, emit one patch (`rule_id: R-70`, location naming both headings, severity high) proposing one unified rule with an explicit conditional, or the deletion of the stale rule.

## Source
Positional/primacy bias in long instructions (Hong 2025), relayed for the oscillation mechanism.

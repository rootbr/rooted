---
title: Long flat lists of if-then edge cases must become 3 to 5 canonical examples plus a heuristic
rule_id: R-72
applies_to_target: [context-file, skill, agent-prompt]
check_kind: semantic
severity_default: medium
---

# Long flat lists of if-then edge cases must become 3 to 5 canonical examples plus a heuristic

## Thesis
A long flat list of edge-case rules ("if X1 then Y1; if X2 then Y2; …") signals missing generalization. Replace it with 3 to 5 representative examples plus the declarative heuristic that generates them.

## Rationale
Each independent if-then rule adds to the instruction bundle and displaces other rules competing for attention. A heuristic plus a few examples expresses the same coverage in roughly one tenth the tokens, with better generalization to edge cases the list never enumerated.

## Example
```
bad:  if .png resize; if .jpg resize; if .gif resize; if .webp resize; … (12 lines)
good: "Resize any raster image to ≤ 2 MB" + examples: .png, .jpg, one animated case
```

## Limits
Targets runs of sequential conditional bullets in the same section (about 8 or more) that share one underlying rule. A short list, or conditionals that genuinely have no common generator, is out of scope and needs no patch.

## Validator
Scan each section for runs of 8 or more sequential conditional bullets of the form "if … then …". For each run, judge whether one declarative heuristic would generate the cases. If it would, flag and propose the heuristic plus 3 to 5 examples. Validator question: do these bullets share a rule that could be stated once?

## Patch output
When a section holds a long flat conditional list reducible to one rule, emit one patch (`rule_id: R-72`, location naming the section, severity medium) replacing the list with a declarative heuristic plus 3 to 5 representative examples.

## Source
Yang 2505.13360 §3.4 (bundling tax — each independent rule displaces others; heuristic + examples is ~1/10 the tokens).

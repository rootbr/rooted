---
title: Control-flow blocks inside a routine nest no more than four levels deep, and logic that would go deeper is flattened by an early exit or a merged condition or moved into a named routine
rule_id: CODE-86
domain: code
step: [implement, refactor]
applies_to: [universal]
triggers: ['signal:deep_nesting', '^(?: {4}){5,}(?:\}\s*)?(?:if|elif|else|for|foreach|while|loop|switch|match|try|with|case|do)\b']
scope: file
check_kind: mechanical
severity_default: minor
---

# Control-flow blocks inside a routine nest no more than four levels deep, and logic that would go deeper is flattened by an early exit or a merged condition or moved into a named routine

## Thesis
Inside one routine, control-flow blocks (if, for, while, loop, switch or match, try, with) nest at most four levels deep, or at most the bound the project's linter configuration states for the depth of all control-flow blocks. A block that would open a deeper level is restructured: special cases are handled first and left with an early return or continue, nested conditions with nothing between them are merged into one condition, or the nested part is moved into its own routine. Depth is counted per routine, so a nested function or closure starts its own count.

## Rationale
When numerous control structures are placed inside one another, the code becomes a tangled, complex web: its readability and maintainability drop significantly and testing gets harder. Shallow nesting of conditions makes code easier to follow and its intent clearer, and keeping the normal path at minimal indentation, with error cases dealt with first, lets a reader scan that path quickly. In a human experiment with 275 participants, minimizing nesting decreased the time developers spent reading and understanding source code. In an fMRI study, a method's maximum nesting depth reached a Kendall correlation of 0.544541 with activation in brain area BA21; nesting depth was one of 41 additional metrics that study explored. An evaluation of 121 code, documentation and developer metrics against 444 human evaluations from 63 developers found that none of them captures code understandability, including those assumed to assess readability and complexity. The bound of four is therefore a linter default, not a measured cut-off: two nesting rules default to 4, others to 3 or 5, two that count nested if statements alone to 3 and 1, and one stays silent until a project sets a threshold. A kernel coding style treats more than 3 levels of indentation as a program to fix, and a project coding standard rates 3 or 4 levels of nesting questionable and 5 or more unacceptable.

## Example
```rust
bad:    for order in orders {
            if order.paid {
                for line in &order.lines {
                    if line.qty > 0 {
                        if line.in_stock { ship(line); } } } } }
good:   for order in orders {
            if !order.paid { continue; }
            for line in &order.lines {
                if line.qty > 0 && line.in_stock { ship(line); } } }
```

## Limits
A project whose linter configuration states another bound on the depth of all control-flow blocks decides, whether a stricter one such as 3 or a looser one such as 5; the finder applies that bound. A bound that counts only nested if statements, or every brace block including the routine body and the blocks around the routine, is counted and enforced by its own tool and does not replace four. Flattening stops where it would obscure intent: essential code moves to the outermost scope unless this obscures intent. Where a project caps return statements or requires a single exit point, each guard clause that returns counts against that cap unless the tool exempts guard ifs at the start of the routine, while a guard that continues a loop adds no return; merging conditions or moving the nested part into its own routine still applies there. Depth counts the routine's own control-flow blocks: a nested function, closure or static block starts its own count, and an else-if continues its chain without adding a level. Removing a redundant else after a branch that returns is a separate fix; this rule counts depth as the code is written, with an else body at the depth of its if body, so a block nested too deep inside such an else is flagged here as well.

## Validator
Take the deep_nesting signal, or grep the hunk for added lines whose control-flow keyword (if, for, while, loop, switch, match, try, with, case, do) sits at deep indentation. Open the file and find the routine that encloses each such line. Count, from the routine's own body, the control-flow blocks that enclose the line plus the block it opens: if (an else-if adds no level), for, while, do, loop, switch or match, try, with; restart the count inside a nested function, closure or static block. Look in the project's linter configuration for a bound on the depth of all control-flow blocks that names the deepest level allowed (max-depth, max-nested-blocks, S134 threshold, max-control-nesting) and apply it in place of four (a linter default that the configuration does not state, such as max-nested-blocks 5, leaves four in place); problemDepth and NestedIfDepth max, which count nested if statements alone, and excessive-nesting-threshold, which counts every brace block including the routine body and the blocks around the routine, are enforced by their own tools and do not replace four. Validator question: **Does an added or changed line open a control-flow block at a depth greater than the project's configured bound on all control-flow blocks, or greater than four when none is configured?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: CODE-86`, severity minor, `file`, `symbol`, `code` = the opening line of the deepest block, quoted verbatim, with the depth counted, `fix` = the routine flattened by an early return or continue, a merged condition, or the nested part moved into its own routine, in the file's language, `rationale` = the depth found against the bound applied and where that bound comes from, the project's linter or the default of four).

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

## Source
- ESLint max-depth, eslint/eslint docs/src/rules/max-depth.md: "This rule enforces a maximum depth that blocks can be nested to reduce code complexity." · "`"max"` (default `4`)"; lib/rules/max-depth.js restarts the count on `FunctionDeclaration`, `FunctionExpression`, `ArrowFunctionExpression`, `StaticBlock` and skips `isElseIf` (fetched)
- Sonar RSPEC S134, sonar-python S134.html: "the default threshold of 4 levels of nesting and one of the potential ways to fix the code smell by introducing guard clauses"; sonar-java S134.html: "When numerous control structures are placed inside one another, the code becomes a tangled, complex web. This significantly reduces the code’s readability and maintainability, and it also complicates the testing process." · "the default threshold of 3 levels of nesting" (fetched)
- PMD AvoidDeeplyNestedIfStmts, AvoidDeeplyNestedIfStmtsRule.java: `.desc("The if statement depth reporting threshold") .require(positive()).defaultValue(3)`; design.xml: "Deeply nested if..then statements are hard to read" (fetched)
- Pylint R1702 too-many-nested-blocks, refactoring_checker.py: "Maximum number of nested blocks for function / method body", `"default": 5` (fetched)
- Checkstyle NestedIfDepth, nestedifdepth.xml: "Restricts nested if-else blocks to a specified depth." · max default `1` (fetched)
- revive max-control-nesting, RULES_DESCRIPTIONS.md: "maximum accepted nesting level of control structures. Default: `5`." (fetched)
- clippy excessive_nesting, excessive_nesting.rs: "Checks for blocks which are nested beyond a certain threshold." · "it will only trigger if a maximum nesting level is defined in the clippy.toml file"; `fn visit_block` runs `self.nest_level += 1` for every brace block, and `visit_item` does the same for `ItemKind::Trait(_) | ItemKind::Impl(_)` and inline `ItemKind::Mod`; lint_configuration.md excessive-nesting-threshold "**Default Value:** `0`" (fetched)
- C++ Core Guidelines F.56: "Shallow nesting of conditions makes the code easier to follow. It also makes the intent clearer. Strive to place the essential code at outermost scope, unless this obscures intent." · "Bad: Still a redundant else." · "Good: Merge conditions + return early" (fetched)
- uber-go/guide style.md, Reduce Nesting: "handling error cases/special conditions first and returning early or continuing the loop"; golang/wiki CodeReviewComments.md, Indent Error Flow: "Try to keep the normal code path at a minimal indentation, and indent the error handling, dealing with it first. This improves the readability of the code by permitting visually scanning the normal path quickly." (fetched)
- Linux kernel Documentation/process/coding-style.rst §1: "if you need more than 3 levels of indentation, you're screwed anyway, and should fix your program."; §6 Functions: "The maximum length of a function is inversely proportional to the complexity and indentation level of that function." · "Use helper functions with descriptive names" (fetched)
- Ghidra GhidraDocs/GhidraCodingStandards.html, Method Complexity: "Methods should avoid deep nesting. 2 or less - good 3 or 4 - questionable 5 or more - unacceptable" (fetched)
- PMD OnlyOneReturn, codestyle.xml: "If the property `allowGuardIfs` is set to true, an unlimited amount of guard ifs at the beginning of the method are allowed."; Sonar S1142: "Having too many return statements in a method increases the method’s essential complexity" (fetched)
- DOI 10.1109/ICSE43902.2021.00056, replication package brains-on-code/fMRI-complexity-metrics-icse2021 Readme.md: "We explored overall 41 additional metrics." · row "NBD | 0.544541" under "BA21_ken"; data/metrics/Metrics.md: "NBD":"Calculates the maximum nesting depth of each method: NEST"; analysis/BrainActivationAnalysis.py: "corr = df[metric].corr(df[ba], method='kendall')" (fetched)
- DOI 10.1109/ICSME.2019.00085: "Minimizing nesting decreases the time a developer spends reading and understanding source code." with "275 participants" (relayed)
- DOI 10.1109/TSE.2019.2901468, abstract as posted at neverworkintheory: "an extensive evaluation of 121 existing as well as new code-related, documentation-related, and developer-related metrics" · "we use 444 human evaluations from 63 developers and we obtained a bold negative result: none of the 121 experimented metrics is able to capture code understandability, not even the ones assumed to assess quality attributes apparently related, such as code readability and complexity." (fetched)
- Caveat: the tools' defaults range from 1 to 5 and one ships with no threshold; the bound of four follows two of them and the fMRI correlation is exploratory, so the number is a convention.

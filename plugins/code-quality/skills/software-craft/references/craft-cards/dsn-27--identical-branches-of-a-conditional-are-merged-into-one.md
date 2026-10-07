---
title: Identical branches of one conditional, switch or match are merged into one when they hold more than one statement or every branch is the same
rule_id: DSN-27
domain: design
step: [implement, review]
applies_to: [universal]
triggers: ['^\s*(\}\s*)?(else\s+if|elif|else)\b|^\s*(case\b|default\s*(:|->))|^\s*[\w:|(){}, -]+(\s+if\s[^=]*)?=>|\?[^:?]+:[^:]|\bif\b.+\belse\b']
scope: file
check_kind: mechanical
severity_default: minor
---

# Identical branches of one conditional, switch or match are merged into one when they hold more than one statement or every branch is the same

## Thesis
Within one if chain, one switch or one match, two branches whose bodies hold the same statements in the same order become one branch when that body holds more than one statement, a following break not counted; a conditional whose every branch carries the same body is merged whatever the body's size, and so is a conditional expression whose two sides are the same. Two branches that need the same logic become one by combining their conditions with a logical or, by listing their case values in one case label, by letting one case fall through to the other, or by joining their patterns into an or-pattern. A conditional that ends in an else or a default and whose every branch carries the same body is removed and its body kept once, or the branch that was meant to differ is corrected.

## Rationale
The same code in two branches of one conditional can make the code harder to understand and maintain, and it can introduce a bug when one copy is changed and the other is not: at best it is duplicate code, at worst a coding error. Identical code in both branches of an if-else or a conditional expression is usually a bug, a typo or a copy-and-paste slip in a branch that was meant to hold different logic, and a conditional with a final else or default whose every branch is the same is either such a slip or a conditional that should be removed. When the sameness is intended, one branch under a combined condition, case list or or-pattern states that intent in the code and leaves one copy to maintain. A body of a single statement is left out unless every branch carries it, because repeating one line in separate branches is usually done on purpose, to increase readability.

## Example
```java
bad:  if (kind == Kind.A) {
          audit(order);
          ship(order);
      } else if (kind == Kind.B) { refund(order);
      } else if (kind == Kind.C) {
          audit(order);
          ship(order);
      }
good: if (kind == Kind.A || kind == Kind.C) { audit(order); ship(order); }
      else if (kind == Kind.B) { refund(order); }
```

## Limits
Two identical single-statement bodies in a conditional whose other branches differ are outside the rule; some checkers report that case as well, as a probable copy-and-paste slip or as arms a combined condition would state more clearly. Two identical branches with other branches between them merge only when one of them can move past those branches without changing which branch runs: when the earlier one overlaps a branch between them, some input satisfying both, and the later one also overlaps a branch between them, the same branch or another, the pair cannot be merged and is outside the rule. Match arms whose guards differ, or whose bodies use pattern bindings of different types, cannot always be merged and are outside the rule too. Branches that share only their leading or trailing statements are outside the rule; those statements can move out of the branches. A tolerance the project context states for identical branches, such as one for generated code, rejects the finding.

## Validator
Grep the added lines for an else-if, elif or else line, a case or default label, a match arm, a conditional expression and an if-else written on one line. Open the file, read the whole conditional, switch or match each hit belongs to, and list its branches with their bodies: the statements in order, whitespace ignored, a case's trailing break set aside. Compare every pair of bodies. For a pair with the same statements, count them: go on when the body holds two or more, or when every branch of the conditional carries that body, both sides of a conditional expression included; skip a one-statement pair whose siblings differ. For an identical pair with branches between them, check whether the earlier member overlaps a branch between them, some input satisfying both, and whether the later member overlaps a branch between them, the same branch or another, and skip the pair when both do; skip match arms whose guards differ or whose bodies use bindings of different types. Validator question: **Does a conditional, switch or match the change adds or edits hold two branches with the same body of two or more statements that can be merged without changing which branch runs, or have every one of its two or more branches carry the same body?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: DSN-27`, severity minor, `file`, `symbol`, `code` = the duplicating branch with its condition, case label or pattern, quoted verbatim from the diff, `fix` = the two branches merged under one combined condition, case label list, fall-through case or or-pattern, placed where the earlier one stands when the later one overlaps no branch between them and where the later one stands otherwise, or, when every branch is the same and the conditional ends in an else or default, the conditional replaced by its body kept once, preceded, when a condition has a side effect, by the conditions joined in their original order with the short-circuit or, in the file's language, `rationale` = naming the branch whose body is duplicated and asking whether the two were meant to differ).

## Source
- SonarSource S1871 "Two branches in a conditional structure should not have exactly the same implementation" (sonar-java, sonar-python and sonar-go rule descriptions) — "it can make the code harder to understand, maintain, and can potentially introduce bugs if one instance of the code is changed but others are not"; "at best duplicate code, and at worst a coding error"; "in an if chain they should be combined"; "for a switch, one should fall through to the other"; "for a switch, the values should be put in the case expression list"; "Unless all blocks are identical, blocks in an if chain that contain a single line of code are ignored. The same applies to blocks in a switch statement that contains a single line of code with or without a following break"; "usually this is done on purpose to increase the readability"; the sonar-java check `IdenticalCasesInSwitchCheck` counts statements, `body.size() == 1 || (body.size() == 2 && body.get(1).is(Tree.Kind.BREAK_STATEMENT))`, while the sonar-python check `SameBranchCheck` (`isOnASingleLine`) and the eslint-plugin-sonarjs check (`hasRequiredSize`) measure the lines a body spans (fetched)
- SonarSource S3923 "All branches in a conditional structure should not have exactly the same implementation" (sonar-java) — "Either there is a copy-paste error that needs fixing or an unnecessary switch or if chain that should be removed"; "This rule does not apply to if chains without else, nor to switch without a default clause"; `int b = a > 12 ? 4 : 4;  // Noncompliant` (fetched)
- eslint-plugin-sonarjs `no-duplicated-branches` — "Having two cases in a switch statement or two branches in an if chain with the same implementation is at best duplicate code, and at worst a coding error." (fetched)
- Error Prone `DuplicateBranches`, severity WARNING, enabled by default — "Repeating identical code in both branches is usually a bug"; "this usually indicates a typo where one of the branches was supposed to contain different logic"; `condition ? same : same` (fetched)
- clippy `if_same_then_else` (style, warn), `match_same_arms` (pedantic, allow), `branches_sharing_code` (nursery, allow) — "This is probably a copy & paste error."; "If arm bodies are the same on purpose, you can factor them [using `|`]"; "Checks if the blocks of an if/else, or the arms of a match, contain shared code that can be moved out of the branches"; "Duplicate code is less maintainable."; `clippy_lints/src/matches/match_same_arms.rs`: "Arms with different guard are ignored, those can't always be merged together", "If both arms overlap with an arm in between then these can't be merged either.", the merge test `!(backwards_blocking_idxs[max_index] > min_index && forwards_blocking_idxs[min_index] < max_index)`, a binding in two arm bodies counts as the same only when `a_typeck_results.expr_ty(a) == b_typeck_results.expr_ty(b)` (fetched)
- Ruff SIM114 `if-with-same-arms` — "If multiple arms of an `if` statement have the same body, using `or` better signals the intent of the statement." (fetched)
- Caveat: no source measures how often identical branches are faults; the rule rests on tool documentation, the exemption is the SonarSource rule's alone, and its statement unit is the sonar-java check's, where the rule descriptions and the sonar-python and eslint-plugin-sonarjs checks use a single line, and the overlap condition is clippy's for match arms, applied to an if chain, which also tests its conditions in order.

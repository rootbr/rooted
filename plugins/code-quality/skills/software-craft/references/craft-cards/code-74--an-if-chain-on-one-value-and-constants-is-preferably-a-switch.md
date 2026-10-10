---
title: An if-else-if chain that tests one value against several constants, with two or more else-if branches, is preferably written as the language's switch or match
rule_id: CODE-74
domain: code
step: [implement, refactor]
applies_to: [universal]
triggers: ['\belse\s+if\b.*(==|[.]equals\()|^\s*elif\b.*(==|\bin\b|\bis\b)']
scope: hunk
check_kind: mechanical
severity_default: suggestion
---

# An if-else-if chain that tests one value against several constants, with two or more else-if branches, is preferably written as the language's switch or match

## Thesis
An if followed by two or more else-if branches, whose conditions each compare one and the same value with a constant or with several constants, is preferably written as a switch or match on that value: the value stated once, one case per branch, the constants that one branch tested together in one case, and the final else as the default case. The count is of conditional branches: the if and two else-ifs reach it, a final else does not count, and a branch that tests several constants counts as one; an if with a single else-if falls below the count and outside this rule's check. The rule holds where the language, at the version the code targets, has a switch or match that takes the value and its constants as case labels.

## Rationale
A chain that compares one value with constants repeats the condition-checking expression once in each if. Besides the redundancy, the repetition is a potential source of bugs: one condition in the chain can unintentionally differ slightly from the others. The chain also reads the value once per branch, so a value read through a getter can differ from branch to branch, where a switch reads it once. A switch is useful when many cases depend on the value of the same expression, and against several ifs with simple equality comparisons it is easier to read and usually shorter; for just one or two cases an if reads better, and too many else-ifs can clutter the code, so with more than one else-if the writer might want to refactor. A switch also enables some heuristic consistency checking of its cases, such as whether every value of an enumeration is covered and, if not, whether there is a default; where the switch has no default case and is checked for exhaustiveness, adding a value to the enumeration raises a compile-time error at the switch, while the chain would have to be found and edited by hand. The guidance states a preference, not a defect: writing the chain as a switch is called possible and idiomatic, and the match statement one the writer may also find useful. Two checkers that report the pattern start at three conditional branches by default, the final else not counted; a third starts at five and leaves shorter chains alone, since they may be more readable as they are.

## Example
```java
bad:  if (code == 1) { ... }
      else if (code == 2 || code == 3) { ... }
      else if (code == 4) { ... }
      else { ... }
good: switch (code) {
          case 1 -> { ... }
          case 2, 3 -> { ... }
          case 4 -> { ... }
          default -> { ... }
      }
```

## Limits
A chain whose conditions test different values, ranges, types or other predicates is outside this rule's check, which reaches only conditions that compare one value with constants. In a language or language version that has no switch or match taking the value's type and its constants as case labels, the if-else-if sequence is the language's substitute for a switch, and the rule does not reach it. The rewrite keeps the chain's behaviour on a null subject: where the switch throws on a null subject that the chain let through, the switch takes a null case, or the chain stays. A chain that compares by a looser equality than the one the switch or match applies to its cases is outside the check, since the rewrite would send a value of another type to a different branch. Where the compared value is a member access or a getter call, the switch's single read can change what a chain of repeated reads did, so the finding is a suggestion to confirm, not a mechanical rewrite. A project context that sets a higher minimum branch count for this check, as one checker does by default with five, rejects a finding below that count.

## Validator
In the hunk, find each added else-if line and the if that opens its chain, and read the whole chain in the hunk context. For each conditional branch, the if and every else-if, read what its condition compares: go on only when every one compares the same value (the same variable, field or expression) with a constant, a named constant or an enumeration member, by equality, an equals call, an identity test against a constant, or membership in a literal set, and only where that comparison is the one the language's switch or match applies to its case labels. Count the conditional branches, a branch testing several constants of that value as one and the final else as none, and go on only at three or more. Skip where the language, at the version the file targets, has no switch or match that takes the value's type and those constants as case labels, and where the project context sets a higher minimum branch count. Where the compared value is a member access or a call, note that the switch reads it once. Validator question: **Does the hunk add or extend an if-else-if chain of three or more conditional branches, a final else not counted, each comparing the same value with constants, in a language whose switch or match can take that value and those constants as cases?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: CODE-74`, severity suggestion, `file`, `symbol`, `code` = the chain's if line and its else-if lines quoted verbatim from the diff, `fix` = the chain rewritten as a switch or match on the compared value, one case per branch with the constants a branch tested together in one case and the final else as the default case, keeping the chain's behaviour on a null subject and writing each named constant in the form the construct compares rather than binds, in the file's language, `rationale` = the value the chain dispatches on, its count of conditional branches, the comparison the chain repeats in each condition and, where the value is a member access or a call, that the switch reads it once).

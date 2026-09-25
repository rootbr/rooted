---
title: An if statement nests at most two deep, and a third level becomes a guard clause or an extracted method
rule_id: MNT-07
domain: maintainability
triggers: ['^\s{8,}if\s*\(', '^\t{3,}(if|for|while)\b', 'else\s*\{', '^\s{14,}(for|while|switch|try)\b']
scope: file
check_kind: mechanical
severity_default: minor
---

# An if statement nests at most two deep, and a third level becomes a guard clause or an extracted method

## Thesis
Within a method, an `if` sits inside at most one other `if`; a third nested level is flattened by a guard clause that returns, continues or throws early, by extracting the inner block into a named method, or by combining the conditions.

## Rationale
Each level of nesting adds a condition the reader must hold in mind for every line below it, so the innermost statement is understood only with the whole stack; that is why cognitive-complexity counting charges one increment per level. A guard clause discharges a condition at the top and lets the remaining code run at the method's own level; an extracted method names the inner block and starts its nesting from zero. The Java analyzers agree on the bound: PMD reports an `if` at depth three, and Checkstyle allows one nested `if` by default.

## Example
```java
bad:  if (order != null) {
          if (order.isOpen()) {
              if (order.total() > limit) { escalate(order); }
          }
      }
good: if (order == null || !order.isOpen()) { return; }
      if (order.total() > limit) { escalate(order); }
```

## Limits
An `else if` ladder is one level, not nested. A lambda or an anonymous class body starts its own count. A nesting of mixed statements — a loop containing a `try` containing an `if` — is tolerated to three levels. A depth declared in the project context replaces two.

## Validator
On the triggered hunk find each added `if`; open the file and count the `if` statements that enclose it within the same method body, ignoring lambdas. Validator question: **is this `if` enclosed by two or more `if` statements of the same method?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: MNT-07`, severity minor, `file`, `symbol`, `code` = the nested `if` chain quoted verbatim from the diff, `fix` = the guard clause or the extracted method, `rationale` naming the conditions the reader must stack).

## Source
PMD `AvoidDeeplyNestedIfStmts` — "Avoid creating deeply nested if-then statements since they are harder to read and error-prone to maintain", `problemDepth` default 3 (the third nested `if` is reported). Checkstyle `NestedIfDepth` — default `max = 1` nested `if`. SonarSource `java:S134` "Control flow statements should not be nested too deeply" — nested `if`, `for`, `while`, `switch` and `try` statements "are key ingredients for making what's known as 'Spaghetti code'. Such code is hard to read, refactor and therefore maintain"; default threshold 3 for the mixed case (rule text from the `sonar-java` 6.15.1 plugin resources).

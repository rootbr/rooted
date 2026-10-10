---
title: A boolean expression with more than three logical and/or operators gives its parts names, as boolean variables or predicate routines, and keeps in short-circuit order any operand whose evaluation depends on an earlier one
rule_id: CODE-85
domain: code
step: [implement, refactor]
applies_to: [universal]
triggers: ['(?:&&|\|\||\band\b|\bor\b)(?:.*?(?:&&|\|\||\band\b|\bor\b)){3}', '^\s*(?:&&|\|\||and\b|or\b)\s*\S|(?:&&|\|\||\band|\bor)\s*\\?$']
scope: hunk
check_kind: mechanical
severity_default: minor
---

# A boolean expression with more than three logical and/or operators gives its parts names, as boolean variables or predicate routines, and keeps in short-circuit order any operand whose evaluation depends on an earlier one

## Thesis
A boolean expression that combines more than three logical operators (short-circuit and/or in symbol or keyword form, and the non-short-circuit and, or and exclusive-or applied to boolean operands, counted across every line of a wrapped expression) names its sub-conditions: local boolean variables whose names state what each part means, or a predicate routine whose name states what the combination tests, until no expression combines more than three. An operand that relies on the short-circuit of an earlier operand stays after that operand, inside the expression or inside a predicate routine that keeps the order.

## Rationale
Too many conditions in one expression make code difficult to read and hence to debug and maintain; an if statement with many boolean operands is harder to understand and maintain, and code that is too complex is, usually, code that readers cannot understand quickly. The advised remedy is to assign the expression, or any of its sub-expressions, to a variable; extracting a condition that mixes operators into a routine with an appropriate name reduces cognitive load. Named parts are one way to write a condition in a more explicit fashion: a negation in the middle of a condition line is very easy to miss. The bound of three is the default of linters that count the and/or operators of one expression; linters that count the operands of an if statement allow five by default. How many operators make an expression complicated is an open question, and writing each operation as a statement of its own is also confusing. In an experiment with 220 professional programmers, some but not all negations made a predicate harder, and more ranges also led to higher error rates, but this was not significant after Bonferroni correction. A variable assigned ahead of the condition evaluates its operand whether or not an earlier operand holds, so operands are extracted directly only where the short-circuit behaviour is not required; an operand guarded by an earlier one, such as a dereference after a null check, keeps its place after its guard.

## Example
```go
bad:  if u != nil && u.Active && !u.Locked && (u.Admin || u.Owner) &&
          !u.Suspended {
          grant(u)
      }
good: usable := func(u *User) bool { return u.Active && !u.Locked && !u.Suspended }
      privileged := func(u *User) bool { return u.Admin || u.Owner }
      if u != nil && usable(u) && privileged(u) {
          grant(u)
      }
```

## Limits
An expression of three or fewer operators is outside the rule, and naming the two sides of a range check such as 0 <= x && x < max is unnecessarily verbose. The field-by-field comparison inside an equality method is exempt, because comparing all the fields of a type there is common. Where the project's linter configuration sets another maximum, that maximum replaces three; a maximum that counts the operands of a condition rather than its operators allows one operator fewer than its value. A predicate routine that hides critical logic or an important edge case can make it easy for a future change to fail to account for it; such a part stays visible, in the expression or as a named local variable. Operator precedence and the parenthesizing of mixed and/or expressions are outside the rule.

## Validator
Grep the added lines for four or more logical and/or operators on one line, and for a line that begins or ends with one, which marks a wrapped condition. Read the whole expression within the hunk and count its logical operators across its lines: short-circuit and/or in symbol or keyword form, and non-short-circuit and, or and exclusive-or on boolean operands; leave out bitwise operators on integers and the conditional operator. Use a maximum that a linter configuration in the diff or the inventory states in place of three, less one where that linter counts operands rather than operators. Skip the field-by-field comparison of an equality method. For each operand, trace whether it dereferences, indexes or calls something that an earlier operand guards, so that the fix keeps it after its guard. Validator question: **Does an added or changed boolean expression combine more logical operators than its bound, which is three unless the project's linter configuration sets another maximum?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: CODE-85`, severity minor, `file`, `symbol`, `code` = the whole boolean expression as the diff shows it, across its lines, `fix` = the condition with its parts named as boolean variables or a predicate routine and every guarded operand kept after its guard, in the file's language, `rationale` = the operator count against the bound and the short-circuit dependency the fix preserves).

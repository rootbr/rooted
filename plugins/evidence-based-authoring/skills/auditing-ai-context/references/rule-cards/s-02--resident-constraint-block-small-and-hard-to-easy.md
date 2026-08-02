---
title: A resident constraint block stays small and ordered hard-to-easy, with the long form one hop away
rule_id: S-02
applies_to_target: [context-file]
check_kind: semantic
severity_default: medium
---

# A resident constraint block stays small and ordered hard-to-easy, with the long form one hop away

## Thesis
A block of constraints that loads on every turn keeps only the rules that govern every turn, states each in its operative form, orders the hardest and most load-bearing first, and leaves the full statement one file read away.

## Rationale
Residency buys presence, not obedience, and each resident rule is paid for out of the compliance of the others. Instruction-following accuracy falls as a conversation grows longer, with drops exceeding 11%; the fall is far steeper when several constraints must hold at once, reducing accuracy by over 40%; and adding or replacing a constraint partway through a conversation costs more than 9%. A large resident block sits in exactly that regime — many constraints, held simultaneously, across a long session. Order is a second lever with the same target: performance fluctuates when the order of constraints changes, and constraints presented hard-to-easy are followed better than the same set in another order.

## Example
```
bad:  every house rule resident and stated in full, grouped by topic
good: the hard rules first and in brief; the full statement one file read away
```

## Limits
Covers a block that loads on every turn. A rule governing every answer has no event to route on, so residency is forced for that class and the check is the block's size and order rather than whether it should exist at all. The over-40% figure is reported without saying whether it is absolute or relative and carries no per-model breakdown, and the ordering effect is reported with no numeric spread. Which rule counts as hard is a judgement about the target's own work.

## Validator
Count the constraints the block holds simultaneously and read its order. Check that the hardest and most load-bearing sit first, that each rule appears in operative form rather than in full exposition, and that the long form is reachable by one file read instead of inlined. Flag a resident block ordered by topic or alphabetically, and a block that inlines the full statement of a rule its core only needs to name. Validator question: is every rule here worth the compliance it costs the others?

## Patch output
When auditing a context file whose resident block is oversized, topic-ordered, or carries the long form inline, emit one patch (`rule_id: S-02`, `location` set to the heading and line hint, severity medium) proposing the reduced core, the hard-to-easy order, and the pointer to the long form. Ranking rules by difficulty and load requires knowing the target's work, so set `proposed: null` and `needs_human: true`.

## Source
SEQUOR 2605.06353 (multi-turn constraint following: >11% accuracy drop as the conversation grows; >40% reduction under multiple simultaneous constraints; >9% when constraints are added or replaced mid-conversation — the abstract does not state absolute vs relative and gives no per-model breakdown); Order Matters 2502.17204 (performance fluctuates with constraint order; hard-to-easy ordering is the more performant one; no numeric spread in the abstract).

---
title: A loop can both stop and repeat, so its condition can become false through its counter's direction or a variable the loop changes, and its body does not leave unconditionally on the first pass
rule_id: CODE-76
domain: code
step: [implement]
applies_to: [universal]
triggers: ['^\s*(?:\}\s*|\S+:\s+)?(?:while|for|loop)\b|^\s*do\s*\{?\s*$']
scope: file
check_kind: semantic
severity_default: major
---

# A loop can both stop and repeat, so its condition can become false through its counter's direction or a variable the loop changes, and its body does not leave unconditionally on the first pass

## Thesis
A loop can both stop and repeat. It can stop: the update of a counted loop moves the counter toward the bound its condition tests, and a loop condition built from local variables reads at least one variable that the loop changes. A loop meant to run until a statement in its body ends it is written in the language's unconditional loop form — a loop with no condition where the language's own lints prefer it to a while loop on the literal true, and a while loop on the literal true elsewhere — placed under an if on the entry condition when the loop must not start while that condition is false, rather than as a counted loop whose counter moves away from its bound or as a condition loop whose condition nothing in the loop changes. It can repeat: at least one path through its body reaches the end of the body or a continue of the same loop, so not every path ends in a break of that loop, a return, a throw or panic, or a jump to an outer loop; a block meant to run at most once is written as an if.

## Rationale
A loop whose stop condition can never be reached, such as one whose counter moves in the wrong direction, runs infinitely; when the counter's type is bounded, the loop ends only once the counter overflows, which can take a long time depending on that type — about 2 billion passes in one documented example — and a counter used as an index steps outside the range, failing at index -1 in a second documented example. A condition whose variables nothing in the loop changes stays unchanged from pass to pass: entering the body leads to an endless loop, and otherwise the loop never runs; one check's own message asks whether the wrong variable is being incremented. An endless loop is sometimes intended, and the convention for it is the unconditional form, which expresses that intent directly and makes it clear to the reader, whereas an endless counted loop is more typically a bug; a condition loop whose condition nothing changes and whose body ends it with a break or a return is rewritten as the unconditional loop under an if on that condition. A loop in which every path through the body ends in a break, a return or a throw never reaches its second iteration, whatever its condition says: it is equivalent to an if, it obscures the code and can confuse its reader, and it can come from a jump statement misplaced inside the body, such as a break meant to sit inside the branch written before it. The checks that report these forms treat each as a possible or likely mistake rather than a style choice.

## Example
```go
bad:  for i := len(items) - 1; i >= 0; i++ { visit(items[i]) }
      for node != nil { visit(node) }
      for _, item := range items { if item.ready { use(item) }; break }
good: for i := len(items) - 1; i >= 0; i-- { visit(items[i]) }
      for node != nil { visit(node); node = node.next }
      for _, item := range items { if item.ready { use(item); break } }
```

## Limits
A constant condition, such as the literal true or false, reads no variable and is outside the unchanged-condition check; a condition that calls a routine or reads a field or property is outside the rule: a call can return different values, a property can be a getter with side effects, and a call in the body can change the field. A counter whose step has no sign known at the loop is outside the direction check. A loop that runs at most once because of its condition — false from the start, false after the first pass, a bound of one — rather than because its body leaves is outside the second-pass check, which follows the body's exits and does not evaluate conditions or values. A single pass whose body has no branch and only takes one element, the first of a sequence or a string or an arbitrary entry of a map, is a pattern one checker accepts as valid and another lets a project exempt by loop kind, while two checks still report it, one suggesting a conditional on the iterator's first element in its place; the finder skips it unless the project context asks for that conditional form.

## Validator
Grep the added lines for a loop header: a while or do-while condition, a counted loop with an initializer, a condition and an update, a loop with no condition, an iteration over a collection. Open the file and read each matched loop whole. For a counted loop, compare the update's direction with the comparison in the condition: a counter that grows while the condition requires it to stay above or at a bound, or shrinks while the condition requires it to stay below or at one, moves away from that bound; skip a step whose sign the file does not fix. For a loop with a condition, list the local variables the condition reads and search the loop's header and body for an assignment, an increment, or a use that can change one of them, such as passing it by reference or calling or passing a nested routine or closure that assigns it; skip a condition that calls a routine or reads a field or property, and a constant condition, such as the literal true or false, which reads no variable. A condition none of whose variables changes is flagged whether the body runs forever or leaves through a break or a return; when the body leaves through a break or a return, or the loop is meant to run forever, its fix is the unconditional loop form, under an if on the condition when the loop must not start while the condition is false, and otherwise its fix is a body that changes a variable the condition reads. For every loop, follow each path through the body to its end: when every path ends in a break of this loop, a return, a throw or panic, or a jump to an outer loop, the loop never reaches its second pass; skip a single pass whose body has no branch and only takes the first element of a sequence or a string or an arbitrary entry of a map, unless the project context asks for the conditional form. Validator question: **Does an added loop have a counter that moves away from the bound its condition tests, a condition whose local variables nothing in the loop changes, or a body whose every path leaves the loop on the first pass?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: CODE-76`, severity major, `file`, `symbol`, `code` = the loop header together with the update, the unchanged condition or the unconditional exit that defeats it, quoted verbatim from the diff, `fix` = the same loop with its counter moving toward the bound, with the body changing a variable its condition reads, rewritten in the unconditional loop form under an if where it must not start on a false condition, or with the exit moved into its branch or the loop replaced by an if, in the file's language, `rationale` = which of the three forms the loop shows and its consequence: an endless loop, a counter that overflows or indexes outside its range, a loop that never runs, or a loop that runs at most once).

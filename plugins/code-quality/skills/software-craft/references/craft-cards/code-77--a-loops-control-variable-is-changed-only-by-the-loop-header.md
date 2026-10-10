---
title: A loop variable the loop header advances is changed only by that header, never inside the body to skip elements or to end the loop
rule_id: CODE-77
domain: code
step: [implement]
applies_to: [universal]
triggers: ['^\s*for\s*\(\s*(?:let|var|int|long|short|byte|size_t|auto|final)?\s*\w+\s*=\s*[^;]*;', '^\s*for\s+\w+\s*:=\s*[^;{]*;', '^\s*for\s+[\w\s,()&]+?\s+in\b', '^\s*for\s*\(\s*[^;=]*?(?:\sof\s|\w\s*:\s*\w)', '^\s*for\s+[\w\s,]*:?=\s*range\b', '(?:^|[;{):])\s*(?:(?:\+\+|--)\s*(?:i|j|k|idx|index|pos|n)\b|(?:i|j|k|idx|index|pos|n)\s*(?:\+\+|--|[-+*/]=|=(?!=)))']
scope: file
check_kind: semantic
severity_default: major
---

# A loop variable the loop header advances is changed only by that header, never inside the body to skip elements or to end the loop

## Thesis
In a loop whose header initializes, tests and advances a counter, only the header changes the counter: the body does not assign to it, increment or decrement it, or hand it to code that updates it. The body skips an element with a test, or with a separate flag that the next pass checks before it continues; it ends the loop early with break, or with a return from a routine that holds the loop; and the header's termination test compares the counter against a bound that does not change while the loop runs. A counter that must be updated in the body belongs in a while loop instead. In a loop that visits each element of a collection or a range, the body does not reassign the loop variable either, and where loops open no scope of their own, an inner loop does not reuse an enclosing loop's variable name.

## Rationale
The loop control in the header is there to let a reader reason correctly about what happens inside the loop: where the counter starts, the bound that ends the loop, and the step between passes. Modifying the counter both in the header's advance and in the body is a perennial source of surprises and bugs: in a counted loop the next pass starts from the value the body left, so an assignment in the body changes the step for one pass, or ends the loop from inside, without the header showing it, and the program flow becomes more difficult to follow. A termination test that compares the counter against an invariant value, one that does not change during the execution of the loop, makes the program logic easier to understand and maintain; a bound the body reassigns, or a call or a property whose value the body changes, such as the length of a collection the body adds to or removes from, moves the end of the loop out of the header. A loop over each element takes its next value from the iterator at the head of every pass, whatever the body assigned, so reassigning the loop variable neither skips an element nor ends the loop: the variable differs from the element being visited for the remainder of that pass, in a way that will likely cause bugs, and a body written to skip an element that way visits it anyway. Where loops open no scope of their own, an inner loop that reuses the enclosing loop's variable name reuses the same variable, and the inner loop's last value leaks into the remainder of the enclosing body. A separate flag for the element to skip keeps two concepts in two variables, a break is typically better than modifying the counter to end the loop, and a while loop is the form for a counter the body must update.

## Example
```rust
bad:  for mut i in 0..items.len() {
          if items[i].is_escape() { i += 1; }
          emit(&items[i]);
      }
good: let mut escaped = false;
      for item in &items {
          if !escaped && item.is_escape() { escaped = true; continue; }
          escaped = false;
          emit(item);
      }
```

## Limits
A loop whose header has no advance step, and a while loop, leave the advance to the body by design and are outside the rule; they are the form for a counter whose step varies. A variable the header neither advances nor compares the counter against, such as a skip flag, a second index or an accumulator updated in the body, is outside the rule, and so is a new variable declared under the loop variable's name, by an inner loop or a declaration in the body, where loops and blocks open their own scope, since it leaves the loop variable untouched. A change made through the loop variable to the element it holds or refers to, such as a method that mutates the element in place or a write through a reference the loop yields, is outside the rule as well, since the variable still holds the element being visited. A bound read through a call or a property, such as a collection's length, meets the rule when the body changes neither the bound nor what it reads; a project that adopts the stricter tool reading, which treats every such bound as possibly varying, hoists the bound into a local before the loop. Rule sets make the strictness configurable: a project may allow a conditional increment or decrement of the counter, allow the loop variable to be reassigned as the body's first statement to normalize the element, such as trimming it, or leave the for-each variable unchecked; a project context that states one of these tolerances rejects the finding for that form.

## Validator
Grep the added lines for a loop header — a three-part counted header, a for-each over a collection, an iterator or a range — and for an increment, a decrement, a compound assignment or a plain assignment to a common counter name. Open the file and, for each loop whose header or body the diff adds or changes, find its loop variable and, for a counted loop, the variable, call or property its termination test compares the counter against. Trace the body, nested blocks included, for a write to the loop variable: an assignment, an increment or decrement, a compound assignment, or, for a counted loop's counter, a hand-off by mutable reference or pointer to code that updates it; for a counted loop, trace also a write to the bound variable and an addition to or removal from the collection whose length the test reads. Where loops open no scope of their own, check each inner loop for the enclosing loop's variable name. Skip a header with no advance step, a while loop, a variable the header neither advances nor compares the counter against, a new variable declared under the same name where blocks open their own scope, and a form the project context tolerates: a conditional increment, a first-statement normalization, an unchecked for-each variable. Validator question: **Does the body of a loop the diff adds or changes write to the loop's own control variable, change the bound its termination test reads, or, where loops open no scope of their own, reuse an enclosing loop's variable name for an inner loop?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: CODE-77`, severity major, `file`, `symbol`, `code` = the loop header and the body line that writes the control variable or the bound, quoted verbatim from the diff, `fix` = the same loop with that write removed — a skip flag tested before the body continues, a break or a return to end early, the bound held in a local, a renamed inner loop variable, or a while loop for a counter the body must update — in the file's language, `rationale` = which variable the body changes, what the header states about it, and what the loop does instead: an element skipped or revisited, an end moved from the header into the body, or a variable that no longer holds the element being visited).

---
title: A loop that reads each element of a collection in order iterates over the elements, not over an index with a hand-written bound, unless it needs the position for more than reading that element
rule_id: CODE-78
domain: code
step: [implement, refactor]
applies_to: [universal]
triggers: ['\bfor\s*\(\s*(?:let|var|int|long|auto|size_t|usize)?\s*\w+\s*=\s*\w+\s*;\s*\w+\s*<=?\s*[\w.]+[.](?:length|size\(\)|len\(\)|count\(\)|Count|Length)', '\bfor\s+\w+\s+in\s+range\s*\(\s*(?:\w+\s*,\s*)?len\s*\(', '\bfor\s+\w+\s+in\s+\(?\w+\s*[.][.]=?\s*[\w.]+[.]len\(\)', '\bfor\s+\w+\s*:=\s*\w+\s*;\s*\w+\s*<=?\s*len\(', '\bfor\s+\w+\s*:=\s*range\s+len\(', '\bwhile\b\s*\(?\s*\w+\s*<=?\s*(?:len\(\s*[\w.]+\s*\)|[\w.]+[.](?:length|size\(\)|len\(\)|count\(\)))']
scope: file
check_kind: mechanical
severity_default: minor
---

# A loop that reads each element of a collection in order iterates over the elements, not over an index with a hand-written bound, unless it needs the position for more than reading that element

## Thesis
A loop that visits every element of an array, list, slice or other indexed sequence once, from the first to the last, uses its counter only to read the current element of that sequence, and neither adds, removes or replaces an element of that sequence nor assigns the variable that holds it in its body iterates with the element loop the language provides for the sequence, not with a counter whose bound the loop writes out.

## Rationale
A counter loop over a sequence writes out its index and its test, and either can be wrong: an incorrect index value or test condition can take the loop beyond the end of the sequence, or stop it short so that it misses items, and a test written against a fixed count fails when the number of elements changes and the test is not updated with it. Iterating the elements themselves eliminates the chance of the overrun and of the missed items, needs no other edit when the number of elements changes, and makes the intent clearer to read.

## Example
```java
bad:  for (int i = 0; i < orders.size(); i++) {
        total += orders.get(i).amount();
      }
good: for (Order order : orders) {
        total += order.amount();
      }
```

## Limits
The counter loop stays where the loop does more with the position than read the current element of one sequence: it reads two elements in one step, such as the current and the previous one; it reads a second sequence at the same position; it acts only on some positions, such as the odd ones; or its counter has more than one update, is changed in the body other than by the one step that ends the body of a loop without an update clause, or is read after the loop. A loop that writes into the sequence through the index, adds or removes its elements or assigns the variable that holds it in the body, or passes the sequence, an element's address or the position to a call that may change the sequence, is outside the rule, which covers loops that only read the sequence: an element loop over a sequence its body changes may visit other elements than the counter loop or fail at run time. A loop that uses the position beside reading the element, for example to print it, is outside what the rule flags: two linters propose the form that yields each position with its element where the language has one, while a third linter keeps the explicit counter there and a style guide accepts either the explicit counter or that form. A sequence type for which the language or its configuration provides no element loop is outside the rule. A higher-order call that visits each element is an accepted alternative to the element loop, and the choice between the two is outside the rule. A text string whose element loop yields decoded characters while its index reads bytes or code units is outside the rule, because the two loops visit different elements.

## Validator
Grep the added lines for a counting loop over a sequence: a three-part loop header or a loop test whose bound is the sequence's length or size, or a range over that length. Read the whole loop, opening the file where the added lines cut it off, and the declaration of the iterated sequence when the added lines do not show its type; list every use of the counter: reading the current element of the iterated sequence, reading at an offset such as the previous or next position, reading a second sequence, arithmetic on the counter, printing or storing it, assigning through it, passing it or an element's address to a call, any change to the counter inside the body other than the one step that ends the body of a loop without an update clause, and any read of the counter after the loop. List as well every use of the iterated sequence in the body other than that read: an element added, removed or replaced, the variable that holds it assigned, or the sequence passed to a call that may change it. Check that the counter starts at the first position, stops after the last and steps by one, and that the sequence's type has an element loop in the file's language that yields the same element the indexed read returns. Validator question: **Does an added loop step one by one from the first to the last position of a sequence whose element loop yields the element its index reads, and use its counter, besides stepping it, for nothing but reading the current element of that sequence, and neither add, remove or replace an element of that sequence nor assign the variable that holds it?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: CODE-78`, severity minor, `file`, `symbol`, `code` = the loop header and the indexed read of the current element, quoted verbatim from the diff, `fix` = the loop rewritten as the language's element loop with the indexed read replaced by the loop variable, in the file's language, `rationale` = the written bound the element loop removes and the confirmation that the counter is used only to read the current element).

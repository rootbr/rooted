---
title: A routine whose result is a collection or array returns an empty one, not null, when it has nothing to return
rule_id: ERR-10
domain: errors
step: [design, implement]
applies_to: [universal]
triggers: ['\breturn\s+(null|None|nil|undefined)\s*(;|$|//|#)', '(\[\]|\bList<|\bArray<|\bMap<|\bSet<|\bCollection<)[^|=]*\|\s*(null|undefined)\b', '->\s*Optional\[(list|List|dict|Dict|set|Set|Sequence|tuple|Tuple)\b|->\s*(list|List|dict|Dict|set|Set)\[.*\]\s*\|\s*None', '->\s*Option<\s*(Vec|VecDeque|HashMap|HashSet|BTreeMap|BTreeSet)\b']
scope: file
check_kind: mechanical
severity_default: minor
---

# A routine whose result is a collection or array returns an empty one, not null, when it has nothing to return

## Thesis
A routine whose declared or inferred result is a collection, an array or a map returns an empty one of that type when it has no elements to return. It gives its callers a null reference, or the language's other absent value, only where the routine's contract states that this value means the question has no answer, as distinct from an answer with no elements. The rule holds wherever the absent value and the empty one behave differently for the caller. It does not govern a routine whose result is a single value, such as a lookup that finds nothing, or a path on which the routine failed to compute its result.

## Rationale
When a routine returns an absent value where an empty one would do, every caller has to test for it before it iterates, counts or reads. That test makes each caller longer and harder to read. A caller that leaves the test out fails with a null dereference, and it fails on the very call where there was nothing to return. In many cases the absent value is used as a synonym for empty. It then tells the caller nothing that the empty one would not, so the test gains nothing. An empty result lets every caller iterate, count and read without a guard. It need not cost an allocation per call either: a shared immutable empty instance can serve every call whose callers only read the result.

## Example
```java
bad:  List<Order> openOrders() {
          if (orders.isEmpty()) return null;
          return filterOpen(orders);
      }
good: List<Order> openOrders() {
          if (orders.isEmpty()) return List.of();
          return filterOpen(orders);
      }
```

## Limits
In some types the absent value already behaves as an empty one on every operation the callers perform: its length is zero, it iterates zero times and a read finds nothing. Returning that absent value is returning empty, and the rule does not reach it. The rule reaches it again where the two differ. One case is when the absent value serializes to a JSON `null` and the empty one to `[]`, and a caller or a wire contract sees the difference. Another is when a caller adds elements to the result and the absent value cannot take them. A caller that compares the result against the absent value does not bring the rule back: for such a type the language's own guidance is to draw no distinction between the absent value and the empty one, so the comparison is what changes, not the return.

An absent result is accepted where it means "this question has no answer" rather than "the answer is none", and the routine's contract says so. An example is a directory listing that returns an empty array for an empty directory, and an absent value when the path is not a directory.

The rule does not reach a path on which the routine failed to compute its result, such as a return inside an exception handler or in the branch that handles a failed call's error: that routine has a failure to report, not an answer with no elements, and an empty result there would read as the latter.

The project context can reject the finding by stating a framework or wire contract that requires the absent value for "none".

## Validator
In the hunk, find each return of a null reference or of the language's absent value. Also find each declared result type that joins a collection, an array or a map with an absent value. Open the file and read the declared or inferred result type of the routine that contains the return. Go on only when that type is a collection, an array, a map or another container of elements. Skip the case where the language gives the absent value of that type the length, iteration and reads of an empty one, and no caller in the file serializes the result or adds elements to it that the absent value cannot take; a caller that compares the result against the absent value does not end the skip. Skip a return on a path where the routine failed to compute its result, such as inside an exception handler or in the branch that handles a failed call's error. Read the routine's doc comment and contract. Skip the case where they state that the absent value means the question has no answer, as distinct from an answer with no elements. Validator question: **Does this routine, whose result is a collection, an array or a map, return an absent value that its callers must test for where an empty one would mean the same?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: ERR-10`, severity minor, `file`, `symbol`, `code` = the return statement or the result-type declaration quoted verbatim from the diff, `fix` = the return rewritten to yield an empty collection, array or map of the declared type and, where `code` is the result-type declaration, that declaration without the absent value, in the file's language, `rationale` = the null test that the empty result spares every caller, and the dereference risked by a caller that leaves the test out).

## Source
PMD `ReturnEmptyCollectionRatherThanNull` (category errorprone) — "For any method that returns an collection (such as an array, Collection or Map), it is better to return an empty one rather than a null reference. This removes the need for null checking all results and avoids inadvertent NullPointerExceptions." (fetched); SonarSource RSPEC-1168 "Empty arrays and collections should be returned instead of null" — "Returning null instead of an actual array, collection or map forces callers of the method to explicitly test for nullity, making them more complex and less readable. Moreover, in many cases, null is used as a synonym for empty." (fetched); SpotBugs `PZLA_PREFER_ZERO_LENGTH_ARRAYS` — "using null to indicate "there is no answer to this question" is probably appropriate. For example, File.listFiles() returns an empty list if given a directory containing no files, and returns null if the file is not a directory." (fetched); .NET Framework Design Guidelines, "Guidelines for Collections" — "DO NOT return null values from collection properties or from methods returning collections. Return an empty collection or an empty array instead." (fetched); `java.util.Collections#emptyList` Javadoc, Java SE 21 — "Implementations of this method need not create a separate List object for each call." (fetched); The Go Programming Language Specification, "Length and capacity" and "Map types" — "The length of a nil slice, map or channel is 0.", "A nil map is equivalent to an empty map except that no elements may be added." (fetched); Go wiki CodeReviewComments, "Declaring Empty Slices" — "a `nil` slice encodes to `null`, while `[]string{}` encodes to the JSON array `[]`", "When designing interfaces, avoid making a distinction between a nil slice and a non-nil, zero-length slice, as this can lead to subtle programming errors." (fetched). Caveat: the three analyzer rules are written for Java and the design guideline for .NET, so the rule's reach beyond those two ecosystems rests on the language-neutral mechanism they describe.

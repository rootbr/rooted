---
title: A call to a standard routine whose documented behaviour differs from what its name suggests or from its namesake in another language, such as half-even rounding, a default sort that compares numbers as strings, a set-of-characters trim, a first-match-only string replace or a regex replaceAll, is used for what its documentation states
rule_id: DOC-01
domain: docs
step: [implement]
applies_to: [universal]
triggers: ['\b[Rr]ound\s*\(', '[.](sort|toSorted)\(\s*\)', '\bTrim(Left|Right)?\(\s*[^,]+,\s*"[^"]{2,}"|[.][lr]?strip\(\s*[\x27"][^\x27"]{2,}[\x27"]|[.]trim_(start_|end_)?matches\(', '[.]replace(All)?\(\s*[\x27"\x60]']
scope: hunk
check_kind: semantic
severity_default: major
---

# A call to a standard routine whose documented behaviour differs from what its name suggests or from its namesake in another language, such as half-even rounding, a default sort that compares numbers as strings, a set-of-characters trim, a first-match-only string replace or a regex replaceAll, is used for what its documentation states

## Thesis
Where a standard-library routine's documented behaviour differs from what its name suggests or from a same-named routine of another standard library, the call's arguments and surrounding code rely on the documented behaviour: the documented tie rule of a rounding routine, a default sort that converts elements to strings before comparing them, a trim whose argument is a set of characters or a pattern removed repeatedly rather than one prefix or suffix, a replace whose string pattern replaces only the first occurrence, and a replace-all whose pattern is a regular expression.

## Rationale
Standard libraries document different behaviour under the same routine name, and the difference shows only on particular inputs. Rounding routines document different tie rules, among them these three: to the even neighbour, so 0.5 and -0.5 both round to 0 and 1.5 rounds to 2; toward positive infinity; and away from zero. The rules apply only to a value exactly halfway between the two results it could round to, and the rule toward positive infinity gives a different result from the rule away from zero for negative numbers with a fractional part of exactly 0.5. A default sort that converts elements to strings and compares them in UTF-16 code unit order puts "80" before "9", where a numeric sort puts 9 before 80. A trim documented to take a set of characters strips all combinations of those characters, not a prefix or suffix; a trim documented to remove all prefixes or suffixes that match a pattern removes them repeatedly; and the routine that removes a prefix or a suffix exactly once is a separate routine in each of these libraries. A replace given a string pattern replaces only the first occurrence in one library and all occurrences in another. A replace-all documented to take a regular expression reads its pattern as one, so a dot meant as a literal matches any character, not only a dot. The documentation names the difference itself: it notes that its rounding differs from many languages' round functions, and it points from the set trim to the routine that removes a prefix or a suffix.

## Example
```java
bad:  String key = name.replaceAll(".", "_");
      long whole = Math.round(delta);  // -2.5 must give -3, as 2.5 gives 3
good: String key = name.replace(".", "_");
      long whole = BigDecimal.valueOf(delta).setScale(0, RoundingMode.HALF_UP).longValue();
```

## Limits
A call that wants the documented behaviour is correct: a set of characters meant as a set, a default sort over strings, half-even rounding chosen for its tie rule, a regular expression meant as one, a single replacement meant to happen once. The same name is correct where the library documents the behaviour the call wants: a replace documented to replace all occurrences, a replace-all documented to take a string, and a default sort that compares numbers by their own ordering. A rounding call whose input is never exactly halfway between the two results it could round to gets the nearest result under every tie rule, and a sort given a comparison function sorts by that function's return value rather than by string conversion. A default sort over strings is correct where code-unit order is the order wanted, as for keys and identifiers; a list of strings sorted for display to a user wants the user's locale collation.

## Validator
Grep the hunk for a rounding call, a sort called with no arguments, a trim or strip whose argument is a pattern or holds two or more characters, and a replace or replace-all whose pattern is a string literal. For each hit, open the documentation of that routine in the file's standard library and read what it states about ties, default ordering, set or prefix trimming, first or all replacement, and literal or regular-expression patterns. Trace what the call relies on from its arguments and the code around it in the hunk: the element type a sort receives, a regular-expression metacharacter such as a dot in a pattern meant literally, a trim argument that spells a word, a value that can lie exactly halfway between two results, of either sign, a string that can hold the pattern more than once, an expected value in a test, a comment or a name. Validator question: **Do the call's arguments or surrounding code rely on a behaviour that differs from the one the routine's documentation states?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: DOC-01`, severity major, `file`, `symbol`, `code` = the call with its arguments quoted verbatim from the diff, `fix` = the call rewritten in the file's language to the routine or argument whose documented behaviour is the one the code relies on — a literal replace, an all-occurrences replace, a prefix-removal routine, an explicit comparison function or an explicit tie rule, `rationale` = names the routine's documented behaviour, the behaviour the code relies on, and an input on which the two differ).

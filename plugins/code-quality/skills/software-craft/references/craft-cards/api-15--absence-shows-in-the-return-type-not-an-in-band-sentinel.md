---
title: An operation that may find no result for a valid input shows the absence in its return type instead of returning an in-band sentinel value
rule_id: API-15
domain: interface
step: [design, implement]
applies_to: [universal]
triggers: ['\breturn\s+(-1|0|""|'''')\s*;?\s*(//.*|#.*)?$', '\breturn\s+(null|None|nil|undefined)\s*;?\s*(//.*|#.*)?$', '(=>|\?\?|\b(unwrap_or|map_or|orElse)\()\s*(-1\b|0\b|""|'''')|\b(getOrDefault|get)\([^()]*,\s*(-1\b|0\b|""|'''')', '\b(indexOf|lastIndexOf|find|rfind|search|IndexOf|Index)\s*\([^)]*\)\s*(>|<=)\s*0\b', '\b(Optional|Option|Maybe)\s*<[^>]*>\s*(\w+\s*)?=\s*(null|nil|undefined)\b']
scope: file
check_kind: semantic
severity_default: major
---

# An operation that may find no result for a valid input shows the absence in its return type instead of returning an in-band sentinel value

## Thesis
An operation for which having no result is an expected outcome of a call it accepts, such as a lookup of a key with no mapping or a search with no match, declares that absence in its result type: an optional type, a result type written as a union with a null or undefined type, or an additional result, placed last, that says whether the other results are valid, a boolean or, when the caller needs an explanation, an error. For that outcome it does not return a value of its ordinary result type that means absence by convention: -1, an empty string, the type's zero value where the caller needs to tell a missing entry from a zero, or a null that the declared result type does not mark, a null returned in place of an absence wrapper included: the wrapper's empty value is the absent result.

## Rationale
An in-band value requires every caller to check for it, and a caller can pass it on to the next operation without checking. Failing to check for it can lead to bugs and can attribute errors to the wrong function: a parse of the -1 returned for a key with no mapping reports that the parse failed, whereas the failure was that the key had no mapping. A zero value returned for a missing entry leaves the caller no way to tell a missing entry from an entry whose value is zero. A test against the sentinel can itself be wrong: a search index is positive only when the match occurs somewhere other than the beginning, so a test for a positive result treats a match at the start as no match. Where null and undefined values go unchecked, the lack of checking tends to be a major source of bugs. A result type that shows the absence puts the check in the type: where the types are checked, most operations are not allowed on a value that may be absent until the caller tests for the absence or matches on it, accounting for the absent case. An additional result that says whether the others are valid prevents the unchecked use too: where the types are checked, passing the call straight to another operation that takes one argument is rejected, since the call has two outputs. A wrapper return type means that a null return was not desired by design, so a null wrapper is a contract violation that will most likely break client code.

## Example
```rust
bad:  fn port_of(&self, name: &str) -> i32 {
          self.ports.get(name).copied().unwrap_or(-1)
      }
good: fn port_of(&self, name: &str) -> Option<i32> {
          self.ports.get(name).copied()
      }
```

## Limits
Some standard library string functions return in-band values, such as a substring search that returns -1 when the substring is not present, which greatly simplifies string-manipulation code at the cost of requiring more diligence from the programmer. A call to such a function is outside the rule; the guidance that records this trade-off still asks its own code, in general, to return the additional result.

Where a missing entry and the zero value mean the same to every caller, as in a set held as a map to booleans where a missing member reads as false, the zero value is the answer rather than a sentinel, and the rule does not reach it.

Which absent value marks the absence, null or undefined, is not part of the rule: neither is preferred in general, and the appropriate one depends on the context, such as the APIs the code works with.

A result that is a collection, an array or a map with no elements, and a path on which the operation failed rather than found nothing, are outside the rule.

An operation that implements or overrides a declaration it does not own keeps the result type and the absent value that the declaration's contract fixes, such as a stream read that returns -1 at the end of the stream or a queue poll that returns null when the queue is empty; the rule judges the declaration that sets the contract.

A routine already published with an in-band result keeps its signature; the absence-typed form is added beside it, and the rule judges only a result type that the change introduces.

## Validator
Grep the added lines for a return of -1, an empty string, a zero or a null value; a default of -1, an empty string or a zero supplied where a lookup or a wrapper finds nothing; a comparison of a search result against zero; and a wrapper-typed variable set to null. Open the file. For a return or a default, read the enclosing routine's declaration and doc comment, and go on only when the value stands for "no result" on a call the routine accepts, such as a missing key or no match, and not for a failure. Skip it when the declared result type already marks the absence (an optional type, a union with null, undefined or None, an additional ok or error result); when the value is the null error that signals success; when the routine's result is a collection, an array or a map; when the routine implements or overrides a declaration it does not own whose contract fixes that value; and when a missing entry and the zero value mean the same to every caller. For a comparison of a search result against zero, open the called routine: skip a library string function, and judge a routine the file declares as above. For a null returned or assigned where the declared type is an absence wrapper, the null wrapper is the finding. Validator question: **Does a routine the diff adds or changes answer a call that finds no result with a value of its ordinary result type that means absence by convention, or return or store a null in place of an absence wrapper?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: API-15`, severity major, `file`, `symbol`, `code` = the return, default or assignment quoted verbatim from the diff, `fix` = the routine's signature with the absence shown in its result type, as an optional type, a union with a null or undefined type or an additional final ok or error result, and the no-result path returning that type's absent value, in the file's language, `rationale` = the in-band value a caller can pass on unchecked and the operation where its misuse would surface).

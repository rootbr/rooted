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

## Validator
Grep the added lines for a return of -1, an empty string, a zero or a null value; a default of -1, an empty string or a zero supplied where a lookup or a wrapper finds nothing; a comparison of a search result against zero; and a wrapper-typed variable set to null. Open the file. For a return or a default, read the enclosing routine's declaration and doc comment, and go on only when the value stands for "no result" on a call the routine accepts, such as a missing key or no match, and not for a failure. Skip it when the declared result type already marks the absence (an optional type, a union with null, undefined or None, an additional ok or error result); when the value is the null error that signals success; when the routine's result is a collection, an array or a map; when the routine implements or overrides a declaration it does not own whose contract fixes that value; and when a missing entry and the zero value mean the same to every caller. For a comparison of a search result against zero, open the called routine: skip a library string function, and judge a routine the file declares as above. For a null returned or assigned where the declared type is an absence wrapper, the null wrapper is the finding. Validator question: **Does a routine the diff adds or changes answer a call that finds no result with a value of its ordinary result type that means absence by convention, or return or store a null in place of an absence wrapper?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: API-15`, severity major, `file`, `symbol`, `code` = the return, default or assignment quoted verbatim from the diff, `fix` = the routine's signature with the absence shown in its result type, as an optional type, a union with a null or undefined type or an additional final ok or error result, and the no-result path returning that type's absent value, in the file's language, `rationale` = the in-band value a caller can pass on unchecked and the operation where its misuse would surface).

## Source
- Google Go Style Guide, Decisions §In-band errors (google/styleguide `go/decisions.md`) — "it is common for functions to return values like -1, null, or the empty string to signal errors or missing results"; "Failing to check for an in-band error value can lead to bugs and can attribute errors to the wrong function."; "The following line returns an error that Parse failed for the input value, whereas the failure was that there is no mapping for missingKey."; "a function should return an additional value to indicate whether its other return values are valid. This return value may be an error or a boolean when no explanation is needed, and should be the final return value."; "This API prevents the caller from incorrectly writing `Parse(Lookup(key))` which causes a compile-time error, since `Lookup(key)` has 2 outputs."; "Some standard library functions, like those in package `strings`, return in-band error values. This greatly simplifies string-manipulation code at the cost of requiring more diligence from the programmer. In general, Go code in the Google codebase should return additional values for errors." (fetched)
- Effective Go §Multiple return values, §Maps (golang/website `_content/doc/effective_go.html`) — "in-band error returns such as `-1` for `EOF`"; "Sometimes you need to distinguish a missing entry from a zero value. Is there an entry for "UTC" or is that 0 because it's not in the map at all?"; "A set can be implemented as a map with value type `bool`.", "will be false if person is not in the map" (fetched); Go `strings.Index` (golang/go `src/strings/strings.go`) — "Index returns the index of the first instance of substr in s, or -1 if substr is not present in s." (fetched)
- `java.util.Optional` class documentation and @apiNote, OpenJDK jdk-21-ga — "If no value is present, the object is considered *empty*"; "primarily intended for use as a method return type where there is a clear need to represent "no result," and where using null is likely to cause errors. A variable whose type is Optional should never itself be null" (fetched)
- `java.io.InputStream.read()` and `java.util.Queue.poll()` documentation, OpenJDK jdk-21-ga — "the next byte of data, or `-1` if the end of the stream is reached"; "the head of this queue, or `null` if this queue is empty" (fetched)
- SpotBugs `NP_OPTIONAL_RETURN_NULL` — "The usage of Optional return type ... always means that explicit null returns were not desired by design. Returning a null value in such case is a contract violation and will most likely break client code."; SpotBugs `RV_CHECK_FOR_POSITIVE_INDEXOF` — "checks to see if the result is positive or non-positive. It is much more typical to check to see if the result is negative or non-negative. It is positive only if the substring checked for occurs at some place other than at the beginning of the String." (fetched)
- TypeScript Handbook, Everyday Types §`null` and `undefined` — "The lack of checking for these values tends to be a major source of bugs"; "when a value is `null` or `undefined`, you will need to test for those values before using methods or properties on that value." (fetched)
- Google TypeScript Style Guide §Undefined and null — "there is no general guidance to prefer one over the other"; "the appropriate absent value depends on the context" (fetched)
- mypy documentation, Kinds of types §Optional types and the None type (python/mypy `docs/source/kinds_of_types.rst`) — "Most operations will not be allowed on unguarded `None` or *optional* values"; "Instead, an explicit `None` check is required." (fetched)
- Rust `core::option` module documentation (rust-lang/rust `library/core/src/option.rs`) — "Return values for functions that are not defined over their entire input range (partial functions)"; "commonly paired with pattern matching to query the presence of a value and take action, always accounting for the `None` case." (fetched)
- Caveat: no source measures a defect rate for in-band results; the rule rests on official and style documentation, one type checker's documentation and two analyzer rules written for one language.

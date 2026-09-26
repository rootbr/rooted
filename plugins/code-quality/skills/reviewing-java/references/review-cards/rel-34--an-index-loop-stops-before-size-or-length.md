---
title: An index loop over a list, array or string stops before size or length, and a substring end index is at most length
rule_id: REL-34
domain: reliability
triggers: ['<=\s*\w+[.]size\(\)', '<=\s*\w+[.]length\b', '<=\s*\w+[.]length\(\)', 'size\(\)\s*-\s*1', 'length\(\)\s*-\s*1', 'substring\(', 'charAt\(']
scope: hunk
check_kind: mechanical
severity_default: major
---

# An index loop over a list, array or string stops before size or length, and a substring end index is at most length

## Thesis
A loop of the form `for (int i = 0; i < n; i++)` over a list, array or string uses `<` against `size()`, `length` or `length()`, not `<=`; an index derived as `size() - 1` is used only for the last element; and `substring(begin, end)` receives `end` no greater than `length()`, with `length() - 1` only when the last character is meant to be dropped.

## Rationale
Valid indices run from 0 to `size() - 1`; `get(index)` throws `IndexOutOfBoundsException` "if the index is out of range (index < 0 || index >= size())", and arrays and strings behave the same. A loop bounded by `<=` reads one past the end on its last iteration and fails on every non-empty input, or silently skips the last element when the body guards the access. `substring(0, s.length() - 1)` drops the final character rather than taking the whole string, which corrupts every value that passes through it while looking like a copy. These are the two classic off-by-one forms and each is decided by one comparison.

## Example
```java
bad:  for (int i = 0; i <= items.size(); i++) process(items.get(i));
      String name = raw.substring(0, raw.length() - 1);      // meant to copy the whole value
good: for (int i = 0; i < items.size(); i++) process(items.get(i));
      String name = raw.substring(0, raw.length());          // or simply raw
```

## Limits
A `<=` loop whose body accesses `i - 1`, or a loop over `size()` inclusive that inserts at positions (`add(i, x)` accepts `size()`), is correct. A `length() - 1` that intentionally strips a trailing character — a separator, a newline — is correct with the intent visible in a name or comment. An index computed for a bounds-checked accessor such as `getOrDefault` is out of scope.

## Validator
On the triggered hunk find each loop condition comparing an index with `size()`, `length` or `length()`, and each `substring`, `charAt` or `get` whose argument is `size()` or `length()` with an offset. Read the body to see which element the index reaches. Validator question: **does this expression treat `size()`/`length()` as a valid index, or `length() - 1` as the exclusive end of the whole value?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: REL-34`, severity major, `file`, `symbol`, `code` = the loop condition or index expression quoted verbatim from the diff, `fix` = `<` in place of `<=`, or the corrected end index, `rationale` naming the element read past the end or dropped).

## Source
`java.util.List#get(int)` Javadoc, Java SE 21 — `@throws IndexOutOfBoundsException if the index is out of range (index < 0 || index >= size())`; `java.lang.String#charAt(int)` — "An index ranges from 0 to length() - 1"; `java.lang.String#substring(int, int)` — `endIndex` exclusive, `IndexOutOfBoundsException` if `endIndex` is larger than the length.

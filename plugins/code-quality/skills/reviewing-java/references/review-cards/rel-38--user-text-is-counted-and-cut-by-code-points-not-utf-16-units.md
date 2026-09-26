---
title: User-facing text is counted, limited and truncated by code points, not by the UTF-16 units that length and charAt report
rule_id: REL-38
domain: reliability
triggers: ['[.]length\(\)\s*[<>=]', '[.]substring\(', '[.]charAt\(', 'maxLength', 'MAX_LENGTH', 'truncate', 'codePointCount\(', 'codePoints\(\)']
scope: hunk
check_kind: semantic
severity_default: minor
---

# User-facing text is counted, limited and truncated by code points, not by the UTF-16 units that length and charAt report

## Thesis
When a limit, a count shown to a user, or a truncation applies to text that can contain emoji, CJK extension characters or other supplementary characters, the code uses `codePointCount`, `codePoints()`, `offsetByCodePoints` or a `BreakIterator`, not `length()`, `charAt` and `substring` on raw indices, so a limit of N characters admits N characters and a cut never splits a surrogate pair.

## Rationale
`String.length()` "is equal to the number of Unicode code units in the string", and a supplementary character occupies two units; `charAt` returns one unit and "If the char value specified by the index is a surrogate, the surrogate value is returned" — half a character. A limit of 100 measured with `length()` rejects a 60-character message with 41 emoji, and `substring(0, 100)` on such text can end between the two halves of a pair, producing an invalid string that fails to encode, renders as a replacement character, or is rejected downstream. `codePointCount` counts characters as the user sees them.

## Example
```java
bad:  if (name.length() > 50) throw new TooLongException();
      String preview = body.substring(0, Math.min(140, body.length()));
good: if (name.codePointCount(0, name.length()) > 50) throw new TooLongException();
      int end = body.offsetByCodePoints(0, Math.min(140, body.codePointCount(0, body.length())));
      String preview = body.substring(0, end);
```

## Limits
Text that is ASCII by construction — identifiers, hex, base64, a fixed enum of codes — is correctly measured with `length()`. A limit that is a storage bound in UTF-16 units or bytes, stated as such, is out of scope. A truncation followed by a check that the cut did not split a pair is correct.

## Validator
On the triggered hunk find each `length()` comparison, `substring` cut or `charAt` walk and read what the text is: free text from a user or a document, or a constrained ASCII value. Validator question: **does this count, limit or cut apply UTF-16 unit indices to text that can hold supplementary characters?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: REL-38`, severity minor, `file`, `symbol`, `code` = the length check or cut quoted verbatim from the diff, `fix` = `codePointCount`/`offsetByCodePoints` or a `BreakIterator`, `rationale` naming the miscounted limit or the split surrogate pair).

## Source
`java.lang.String#length()` Javadoc, Java SE 21 — "The length is equal to the number of Unicode code units in the string"; `#charAt(int)` — "If the char value specified by the index is a surrogate, the surrogate value is returned"; `#codePointCount(int, int)` — "the number of Unicode code points in the specified text range"; `#offsetByCodePoints(int, int)`.

---
title: A fixed-text equality, prefix, suffix, containment or replacement is written with the string type's own operations rather than a regular expression that uses no regex feature
rule_id: INP-15
domain: input
step: [implement, refactor]
applies_to: [universal]
triggers: ['\bre[.](search|match|fullmatch|sub|compile)\(\s*r?["''][\w ,:/@=^$-]*["'']', '\bRegex::new\(\s*r?#*"[\w ,:/@=^$-]*"', '\bregexp[.](MustCompile|Compile|MatchString)\(\s*[`"][\w ,:/@=^$-]*[`"]', '(Pattern[.](compile|matches)|[.](replaceAll|matches))\(\s*"[\w ,:/@=^$-]*"', 'new RegExp\(\s*["''][\w ,:/@=^$-]*["'']|/[\w ,:^$-]+/[gimsuy]*[.]test\(']
scope: hunk
check_kind: mechanical
severity_default: suggestion
---

# A fixed-text equality, prefix, suffix, containment or replacement is written with the string type's own operations rather than a regular expression that uses no regex feature

## Thesis
A regular expression whose pattern is only literal text, anchored at the start of the input, at its end, at both or at neither, with no flag, and that tests equality, a prefix, a suffix or containment, or, unanchored, replaces every occurrence of one fixed string with another, is written with the string type's own operation for that job, taking as its arguments the literal text the pattern matches and, for a replacement, the literal text it inserts, with anchors and escapes removed.

## Rationale
When the text to match is a fixed string and the match uses no pattern feature, the full power of a regular expression may not be required: the string type has operations for fixed strings, and each of these jobs has one — equality, starts-with, ends-with, contains, replace every occurrence. Where those operations are implemented as a single small loop optimised for the purpose, they are usually much faster than the large, more generalised regular-expression engine. The fixed-string replacement keeps the literal pattern's behaviour inside words: replacing `word` with `deed` turns `swordfish` into `sdeedfish` with either tool.

## Example
```java
bad:  boolean isIndex = name.matches("index");
      String flat = text.replaceAll("--", "-");
good: boolean isIndex = name.equals("index");
      String flat = text.replace("--", "-");
```

## Limits
One compiled pattern applied to multiple inputs is outside the rule: the precomputation done when the pattern is built can give significantly better performance than any of the string operations. A match that uses a pattern feature, such as a case-insensitive flag, is outside the rule, and so is a replacement that must spare parts of words: it needs a word boundary on either side of the text, which takes the job beyond the fixed-string replacement. An end anchor that the engine also matches just before a final newline does not mark the end of the input: on input that ends in a newline the pattern matches where the suffix or equality test fails, so a pattern ending in such an anchor is outside the rule unless the call's whole-input match already ties the pattern to the end of the input. A replacement of only the first occurrence, or of an anchored prefix or suffix, is outside the rule: the string type need not have one operation for that job.

## Validator
Grep the hunk for a call that builds or applies a regular expression from a string-literal or regex-literal pattern, including a string method whose pattern argument is a regular expression. Open the pattern: each character is a literal or an escaped metacharacter, at most a start anchor and an end anchor surround it, an end anchor counting only when the engine matches it at the end of the input alone or the call's whole-input match ties the pattern to that end, and the call passes no flag; count the call's implicit anchoring (a whole-input match anchors both ends, a start-only match anchors the start). Read the job the call does: an equality, prefix, suffix or containment test, or an unanchored replacement of every occurrence whose replacement text is fixed. Trace the compiled pattern: when the same compiled pattern is applied to multiple inputs (a constant, a field, a value built outside a loop), answer no. Validator question: **Does the hunk use a regular expression of only literal text, at most anchored at the start or the end of the input and with no flag, for an equality, prefix, suffix or containment test or an unanchored fixed-string replacement of every occurrence, other than one compiled pattern applied to multiple inputs?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: INP-15`, severity suggestion, `file`, `symbol`, `code` = the regular-expression call with its literal pattern, verbatim from the diff, `fix` = the same job written with the string type's equality, prefix, suffix, containment or replacement operation, in the file's language, `rationale` = that the pattern is fixed text using no pattern feature, so a string operation for fixed strings does the job and is usually faster).

## Source
- Python documentation, Regular Expression HOWTO, Common Problems > Use string methods (python/cpython main Doc/howto/regex.rst) (fetched): "If you're matching a fixed string, or a single character class, and you're not using any re features such as the IGNORECASE flag, then the full power of regular expressions may not be required. Strings have several methods for performing operations with fixed strings and they're usually much faster, because the implementation is a single small C loop that's been optimized for the purpose, instead of the large, more generalized regular expression engine."; "replace() will also replace word inside words, turning swordfish into sdeedfish, but the naive RE word would have done that, too. (To avoid performing the substitution on parts of words, the pattern would have to be \bword\b, in order to require that word have a word boundary on either side. This takes the job beyond replace()'s abilities.)"
- rust-clippy lint `trivial_regex` (rust-lang/rust-clippy master clippy_lints/src/regex.rs) (fetched): "Matching the regex can likely be replaced by `==` or `str::starts_with`, `str::ends_with` or `std::contains` or other `str` methods."; Known problems: "If the same regex is going to be applied to multiple inputs, the precomputations done by `Regex` construction can give significantly better performance than any of the `str`-based methods."; `is_trivial_regex` maps start anchor + literals + end anchor to "consider using `==` on `str`s", start anchor + literals to "consider using `str::starts_with`", literals + end anchor to "consider using `str::ends_with`", literals alone to "consider using `str::contains`".
- rust-clippy README.md, lint groups (fetched): "`clippy::nursery` | new lints that are still under development | allow".
- Python documentation, Regular Expression HOWTO, More Metacharacters (python/cpython main Doc/howto/regex.rst) (fetched): "$ Matches at the end of a line, which is defined as either the end of the string, or any location followed by a newline character.", with print(re.search('}$', '{block}\n')) printing a match; OpenJDK java.util.regex.Pattern (openjdk/jdk master src/java.base/share/classes/java/util/regex/Pattern.java) (fetched): "When not in multiline mode, the $ can only match at the very end of the input, unless the input ends in a line terminator in which it matches right before the last line terminator."; rust-lang/regex (master src/lib.rs) (fetched): "$ the end of a haystack (or end-of-line with multi-line mode)"; golang/go regexp/syntax (master src/regexp/syntax/doc.go) (fetched): "$ at end of text (like \z not \Z) or line (flag m=true)".
- OpenJDK java.lang.String (openjdk/jdk master src/java.base/share/classes/java/lang/String.java) (fetched): `replace(CharSequence target, CharSequence replacement)`: "Replaces each substring of this string that matches the literal target sequence with the specified literal replacement sequence."; `replaceFirst(String regex, String replacement)`: "Replaces the first substring of this string that matches the given regular expression with the given replacement."
- Caveat: the speed comparison is stated for one runtime's string methods and engine, and the reuse exception for one engine's construction-time precomputation; the tool check sits in a lint group that is allowed by default.

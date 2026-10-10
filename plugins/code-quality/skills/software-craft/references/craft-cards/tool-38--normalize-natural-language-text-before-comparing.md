---
title: Natural-language text from different sources is normalized to one Unicode form, and case-folded for a caseless match, before it is compared or searched
rule_id: TOOL-38
domain: tooling
step: [implement]
applies_to: [universal]
triggers: ['[.](lower|upper|casefold|toLowerCase|toUpperCase|to_lowercase|to_uppercase)\(\)\s*(==|===|!=|!==|in\b|[.](includes|contains|startsWith|startswith|starts_with|indexOf|find)\()', '(==|===|!=|!==)\s*[\w.]+[.](lower|upper|casefold|toLowerCase|toUpperCase|to_lowercase|to_uppercase)\(\)', '\b(equalsIgnoreCase|EqualFold|eq_ignore_ascii_case|localeCompare|ToLower|ToUpper|to_lowercase|to_uppercase|lower|upper|casefold|toLowerCase|toUpperCase|toLocaleLowerCase|toLocaleUpperCase)\(']
scope: hunk
check_kind: semantic
severity_default: minor
---

# Natural-language text from different sources is normalized to one Unicode form, and case-folded for a caseless match, before it is compared or searched

## Thesis
When natural-language text that may come from different sources is compared for equality, looked up by key or searched, both sides are first normalized to the same canonical normalization form with the language's normalization API. A caseless match case-folds the normalized text and normalizes the folded result again before comparing. The normalized form is computed as a comparison key inside the match, so the match rewrites none of the text the program stores, and compatibility forms are applied only when the end user specifically requests them.

## Rationale
The same set of characters can be represented by different sequences of code points: 'ê' is either the single code point U+00EA or U+0065 followed by U+0302, a combining circumflex accent. Both print the same, yet one sequence is one code point long and the other two, and a comparison of code points or bytes treats them as unequal. The Unicode Standard calls such sequences canonically equivalent and holds that they should be treated as equal, and to a user both are the same character, so a search or a comparison has to treat the two sequences as equivalent. Two canonically equivalent strings normalized to the same normal form have the same byte representation, so a comparison of the normalized keys no longer falsely reports inequality when the strings use combining characters differently. Case folding converts text to a case-insensitive form by the algorithm the Unicode Standard describes, with special handling such as 'ß' becoming 'ss'; a few characters make case folding return a non-normalized string, so the folded result is normalized again. Content authors and applications can represent the same semantic values in many different ways when inputting or exchanging text, and normalization can remove distinctions that users applied intentionally, which is why the normalization stays internal to the matching. The compatibility forms change the structure and lose the meaning of the text in important ways.

## Example
```rust
bad:  fn same_name(a: &str, b: &str) -> bool {
          a.to_lowercase() == b.to_lowercase()
      }
good: use unicode_normalization::UnicodeNormalization;
      fn match_key(s: &str) -> String {
          let folded = caseless::default_case_fold_str(&s.nfd().collect::<String>());
          folded.nfd().collect()
      }
      fn same_name(a: &str, b: &str) -> bool { match_key(a) == match_key(b) }
```

## Limits
Identifiers and syntactic content, such as the keywords, enumerated values and other identifiers of a format or protocol, are matched by the rule their format defines, by default with no case folding and no normalization; those default comparisons are sensitive to case and normalization-form differences, and the authors of that content are expected to use consistent case and consistent character sequences. The rule is contested: language documentation holds that text handled inside one program generally needs no normalization package and that 99.98% of the web's HTML page content is in the composed form (NFC), and the string-matching standard adds that almost all legacy data transcoded one-to-one to a Unicode encoding, data created by current software and text entered on most but not all keyboards is already in that form. The separating condition is what is matched and where its forms can differ: natural-language text that reaches the comparison from different authors, applications or keyboards is normalized for the match, while identifiers and syntactic content are matched by their format's rule, by default as they are. A collation or search routine that works correctly on unnormalized strings needs no prior normalization; outside such a routine, normalization may be necessary for consistent results. Whether text is also written out in a normal form is a separate interchange decision on which the sources diverge: the string-matching standard forbids altering the normalization form of content being exchanged, read, parsed or processed except as a side effect of a transformation such as transcoding or case folding, while language documentation names normalizing output as useful for compacting text, for an external interface that expects a normal form, or to match the rest of the world. The second normalization guards against case folding that returns a non-normalized string; a match that normalizes to the decomposed form before folding may omit it, since there an additional normalization changes no comparison result, and the string-matching standard makes post-case-fold normalization optional for strings that are only compared. Normalization performed while validating untrusted input is outside this rule.

## Validator
Grep the hunk for case-mapped text compared with an equality operator or passed to a contains, starts-with or index search, and for a case-mapping, case-insensitive equality or locale comparison call. Open the hunk around each hit and decide what the operands are: natural-language text that may come from different sources (user input, a file, the network, a database, another application) or identifiers and syntactic content (keywords, enumerated values, protocol fields, internal ids). For natural-language operands, trace each side back within the hunk and check whether both pass through the same canonical normalization and, for a caseless match, through case folding followed by a second normalization, which a match that normalizes to the decomposed form before folding may omit; skip a call into a collation or search routine documented to work correctly on unnormalized strings. Validator question: **Does the hunk compare, look up or search natural-language text that may come from different sources without first normalizing both sides to the same canonical form, with case folding and, unless that first normalization is to the decomposed form, a second normalization for a caseless match?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: TOOL-38`, severity minor, `file`, `symbol`, `code` = the comparison, lookup or search expression quoted verbatim from the diff, `fix` = the same match made on keys computed by normalizing both sides to one canonical form, with case folding and a second normalization for a caseless match, leaving the stored text unchanged, in the file's language, `rationale` = names the two code-point sequences of one visible character that the current comparison treats as different).

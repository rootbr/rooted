---
title: A regular expression whose complexity score exceeds 20, with alternations, quantifiers and lookarounds weighted by nesting, is split into smaller patterns or replaced in part by code that parses and checks the pieces
rule_id: INP-16
domain: input
step: [implement, refactor]
applies_to: [universal]
triggers: ['(re[.]compile|Pattern[.]compile|new RegExp|regexp[.]MustCompile|regexp[.]Compile|Regex::new)\((\s*r?(\x22{3}|\x27{3}|\x60)?\s*$|.{40,})', '(re[.](match|search|fullmatch|sub|findall)|[.]matches|[.]replaceAll)\((\s*$|\s*r?[\x22\x27].{40,})', '[=(,:]\s*/(?![*/])(?:[^/\\\n]|\\[^\n]){40,}/[dgimsuyv]*', '@Pattern\((\s*$|\s*regexp\s*=.{40,})']
scope: hunk
check_kind: mechanical
severity_default: minor
---

# A regular expression whose complexity score exceeds 20, with alternations, quantifiers and lookarounds weighted by nesting, is split into smaller patterns or replaced in part by code that parses and checks the pieces

## Thesis
A regular expression whose complexity score exceeds 20 is split into several smaller patterns, or has the whole or parts of it replaced by ordinary code that parses and checks the pieces. The score starts at 0 and the nesting level at 1. The first `|` of an alternation, each quantifier (`*`, `+`, `?`, `{n,m}`, `{n,}`, `{n}`), each non-capturing group that sets or clears flags and each lookahead or lookbehind adds the current nesting level and raises the nesting level by one for its operands. Each further `|` of the same alternation, each bracketed character class and each back-reference adds 1 regardless of nesting; where the engine supports character-class intersection, the first `&&` of an intersection adds the nesting level its class sits at and each further `&&` adds 1; an escape class such as `\d` and the dot add nothing.

## Rationale
Overly complicated regular expressions are hard to read and to maintain and can easily cause hard-to-find bugs. A regular expression that defines a complex language can become error-prone even for authors experienced in writing grammars, and regular expressions are recommended for simple, structured fields. The score turns "too complicated" into a count: each nesting-weighted operator adds the nesting level it sits at, so the same operator costs more the deeper it is nested. The remedies named for a pattern above the threshold are to replace it, or parts of it, with regular code, or at least to split it into several patterns; the matching mitigation is to determine whether several smaller expressions simplify one large expression. The compliant form keeps a short pattern for the shape of the value, then splits the value into its parts and validates the integer parts in code.

## Example
```python
bad:  SLOT = re.compile(r"(?:[1-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|250)-(?:[1-9]|[1-5][0-9]|6[0-4])-(?:[1-9]|1[0-2])(?:-[A-H])?")
      slot_ok = SLOT.fullmatch(text) is not None
good: SLOT = re.compile(r"([1-9][0-9]{0,2})-([1-9][0-9]?)-([1-9][0-9]?)(-[A-H])?")
      match = SLOT.fullmatch(text)
      limits = (250, 64, 12)
      slot_ok = match is not None and all(
          int(part) <= limit for part, limit in zip(match.groups(), limits))
```

## Limits
The maximum of 20 is a default exposed as a setting, the maximum authorized complexity; a project that documents another maximum is checked against that maximum. Plain capturing groups, named groups and non-capturing groups without flags add nothing to the score, so a pattern that is long only because of literal text and such groups can score 20 or less and stays outside the rule. The score counts operators, character classes and back-references only; matching the entire value and avoiding excessive backtracking are separate requirements on a pattern, and the score measures neither.

## Validator
Grep the hunk for a regular-expression constructor, compile call, match call, literal or pattern annotation, including one whose pattern argument starts on the next line. For each added or changed pattern, read the pattern text from the hunk and count its score: start at 0 with the nesting level at 1; for the first `|` of an alternation, each quantifier, each non-capturing group that sets or clears flags and each lookahead or lookbehind, add the current nesting level and count its operands one level deeper; add 1 for each further `|` of the same alternation, each bracketed character class and each back-reference; for the first `&&` of a character-class intersection add the nesting level its class sits at, and 1 for each further `&&`; plain, named and flag-free non-capturing groups add nothing, and neither do escape classes such as `\d` or the dot. Open the project's linter configuration for a documented maximum other than 20 and use it in place of 20. Validator question: **Does an added or changed regular expression in the hunk score above the project's documented maximum, or above 20 where the project documents none?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: INP-16`, severity minor, `file`, `symbol`, `code` = the line that builds or applies the pattern, quoted verbatim from the diff, `fix` = the pattern split into smaller patterns, or a short pattern for the value's shape followed by code that converts and checks its parts, in the file's language, `rationale` = names the computed score against the maximum and the operators that contribute most to it).

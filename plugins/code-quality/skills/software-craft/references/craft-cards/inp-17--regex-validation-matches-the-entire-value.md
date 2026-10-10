---
title: A regular expression that checks a whole value matches the entire value, through a full-match call or anchors at both ends that admit no trailing newline, with alternatives grouped inside the anchors
rule_id: INP-17
domain: input
step: [implement]
applies_to: [universal]
triggers: ['[\w/)\]][.](test|match|search)\(|\bre[.]compile\(|\b(MatchString|is_match)\(|[.]matcher\(.*\)[.]find\(\)', '["''/`]\^[^"''/`|()]*\|[^"''/`]*\$["''/`]']
scope: hunk
check_kind: semantic
severity_default: major
---

# A regular expression that checks a whole value matches the entire value, through a full-match call or anchors at both ends that admit no trailing newline, with alternatives grouped inside the anchors

## Thesis
A regular expression that decides whether a whole value has a format matches the entire value. It runs through the engine's full-match call where one exists, or it carries a start anchor and an end anchor with every alternative between them: the alternatives are grouped inside the anchors, so `^a|b$` is written `^(?:a|b)$`, or each alternative is anchored at both ends. The end anchor matches only at the end of the input in the engine that runs the pattern: no multiline flag is set, and where the engine's end anchor also matches just before a final line terminator, the pattern uses the engine's end-of-input anchor or the full-match call.

## Rationale
A pattern without anchors accepts substrings that match it, which produces a partial comparison with the target, and untrusted input can bypass such a check by embedding one of the allowed patterns in an unexpected location. Anchors bind more tightly than alternation: in `^alt1|alt2|alt3$` the first alternative is anchored only at the start, the last only at the end and the middle one not at all, so the host check `^www\.example\.com|beta\.example\.com` accepts `evil.beta.example.com`. An end anchor that also matches just before a newline at the end of the input lets `^\d+$` accept `123` followed by a newline, and a multiline flag makes both anchors match at line terminators as well, so `^abc$` under that flag finds a match in `abc`, a newline and `evil`. Where the check guards nothing security-critical, an accidental match may still cause undesirable behaviour. A full-match call asks the engine whether the whole input matches the pattern, so `a|b` fully matched against `ab` and `\d+` fully matched against `123` and a newline both fail.

## Example
```typescript
bad:  const isCode = (s: string) => /^\d+|none$/.test(s);
      const isHost = (s: string) => /www\.example\.com/.test(s);
good: const isCode = (s: string) => /^(?:\d+|none)$/.test(s);
      const isHost = (s: string) => /^www\.example\.com$/.test(s);
```

## Limits
A pattern that finds occurrences inside a larger text, such as a search or an extraction, is outside the rule, as is a test meant to check only a prefix, a suffix or a contained character of a value, such as a file extension or a required character class, and a pattern whose anchor is meant for one alternative alone, written with the anchor grouped with that alternative, as in `(?:^a)|b|(?:c$)`, to make the intent explicit. In an engine whose end anchor matches only at the end of the input when no multiline flag is set, a pattern anchored at both ends with its alternatives grouped already meets the rule without a full-match call. A call that anchors the match at the start of the input stands in for the start anchor.

## Validator
Grep the hunk for a regular-expression call whose result accepts or rejects a value: a test, exec, match, matches, search, find or is-match call in a condition, a guard or a validation routine. Open the pattern and its flags at the hunk. Note whether the call is a full-match call; if it is not, check that the pattern begins with a start anchor, or the call anchors the match at the start of the input, and that it ends with an end anchor, that a top-level `|` sits inside a group between the anchors or that every alternative carries both anchors, that no multiline flag is set, and whether the engine's end anchor also matches before a final line terminator. Trace the matched value to its source and skip a pattern that searches a larger text for occurrences, one meant to check only a prefix, a suffix or a contained character, and one that anchors a single alternative through a group as in `(?:^a)|b|(?:c$)`. Validator question: **Does a regular expression that decides whether a whole value has a format leave part of the value unmatched, through a missing anchor at either end without a full-match call, an alternative outside the anchors, a multiline flag, or an end anchor that matches before a final line terminator?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: INP-17`, severity major, `file`, `symbol`, `code` = the pattern with its flags and the call that applies it, verbatim from the diff, `fix` = the full-match call, or the pattern anchored at both ends with its alternatives grouped, without a multiline flag, and with the engine's end-of-input anchor where its end anchor admits a final line terminator, in the file's language, `rationale` = an input that passes the check while embedding an allowed value or carrying an extra line or a trailing line terminator).

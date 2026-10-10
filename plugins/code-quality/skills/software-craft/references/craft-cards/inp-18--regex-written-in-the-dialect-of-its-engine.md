---
title: A regular expression is written in the dialect of the engine that runs it, so it compiles there and its anchors, escapes, groups and classes mean there what the author intends
rule_id: INP-18
domain: input
step: [implement]
applies_to: [universal]
triggers: ['\(\?<?[=!]', '(Regex::new|RegexBuilder::new|RegexSet::new|regexp[.]MustCompile|regexp[.]Compile|regexp[.]Match(String|Reader)?|Pattern[.]compile|\bre[.](compile|match|fullmatch|search|sub|subn|split|findall|finditer)|new RegExp)\(']
scope: file
check_kind: semantic
severity_default: major
---

# A regular expression is written in the dialect of the engine that runs it, so it compiles there and its anchors, escapes, groups and classes mean there what the author intends

## Thesis
A regular expression is written in the syntax of the engine that compiles and runs it. Each construct it uses (anchor, escape, group, back-reference, look-around, character class) is one that engine accepts, and each carries in that engine the meaning the surrounding code relies on, rather than the meaning the same notation has in another engine's dialect.

## Rationale
Regular-expression notation is not a common language across engines. In a corpus of 537,806 regexes from 193,524 projects in eight programming languages, 76% were valid in every language; though most regexes compiled across language boundaries, 15% exhibited semantic differences across languages (in whether an input matches, in the matched substring or in the captures) and 10% exhibited performance differences. Notation that one engine defines and another does not is, in the other engine, a syntax error, a run of literal characters, or a different construct such as a character class of those characters. Two engines that guarantee matching time linear in the size of the input lack look-around and back-references; one documents them as features not known how to implement efficiently. A pattern compiled from a string at run time surfaces a syntax error only when that code executes, as an exception, a returned error or a panic. Notation that two engines both define can name different features: what one engine reads as a back-reference another reads as an octal escape, and a caret anchors at the start of input in most engines and at the start of a line in one. An escape pair that one engine reads as anchors another reads as the literal letters, so a pattern whose author probably intended anchors matches those letters; among the modules of one package registry from which the corpus was drawn, 31 used that notation, and linter-style checks for features unavailable in the target language found hundreds of modules with potential semantic regex bugs. Character classes and newline behaviour are checked in the running engine rather than assumed to behave identically across languages. Linters that compile each literal pattern with the target engine's own parser report a syntax error before the code runs; a construct that compiles with a different meaning passes them, and is found by checking each construct against the features the running engine defines.

## Example
```go
bad:  re := regexp.MustCompile(`(?<=\$)\d+`)
      amount := re.FindString(input)
good: re := regexp.MustCompile(`\$(\d+)`)
      amount := ""
      if m := re.FindStringSubmatch(input); m != nil {
          amount = m[1]
      }
```

## Limits
A pattern that runs in several engines meets the rule in each of them, not only in the one it was written for. The dialect is that of the engine version the project builds against: one linear-time engine rejects named groups written `(?<name>...)` in the version the corpus study tested and accepts them in later versions. Code that deliberately compiles an invalid pattern, such as a test of the regex compiler itself, is outside the rule; one linter leaves the general compile call unchecked because many of its callers are deliberately testing the regex compiler or using a vacuously true regex. Linters check literal patterns, so a pattern assembled from variable parts reaches its engine unchecked until the code runs. Whether a pattern must match the whole value, how its matching time grows with the input, and how its classes treat characters made of several code points are separate questions; the rule covers whether each construct exists in the running engine with the intended meaning.

## Validator
Grep the hunk for a pattern passed to a regular-expression constructor or written as a regex literal, and within it for notation whose support or meaning varies between engines: look-around `(?=`, `(?!`, `(?<=`, `(?<!`; atomic groups `(?>`; named groups `(?<name>`; back-references `\1` to `\9`; the anchors `\A`, `\Z`, `\z`; POSIX bracket classes such as `[[:digit:]]`; possessive quantifiers. Identify the engine from the call or import that compiles the pattern, and its version from the build file when the construct is version-dependent. For each such construct, check in that engine's syntax reference that it is accepted and that its meaning there is the one the surrounding code relies on: a boundary where the code expects an anchor, a match of the same text the group captured where it expects a back-reference. Validator question: **Does the hunk compile a pattern containing a construct that its engine rejects, or reads with a meaning other than the one the surrounding code relies on?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: INP-18`, severity major, `file`, `symbol`, `code` = the pattern literal and the call that compiles it, quoted verbatim from the diff, `fix` = the pattern rewritten in the engine's own syntax, such as a capture group in place of an unsupported look-around or the engine's own anchor in place of a foreign one, in the file's language, `rationale` = the construct, the engine that compiles it, and whether that engine rejects it at run time or reads it with another meaning).

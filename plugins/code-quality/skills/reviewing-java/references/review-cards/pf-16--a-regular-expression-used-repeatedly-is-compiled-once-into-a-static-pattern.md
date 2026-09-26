---
title: A regular expression used repeatedly is compiled once into a static final Pattern, never recompiled by String.matches, replaceAll, split or Pattern.compile on each call
rule_id: PF-16
domain: performance
triggers: ['Pattern[.]compile\(', '[.]matches\(', '[.]replaceAll\(', '[.]replaceFirst\(', '[.]split\(', 'Pattern[.]matches\(']
scope: hunk
check_kind: mechanical
severity_default: minor
---

# A regular expression used repeatedly is compiled once into a static final Pattern, never recompiled by String.matches, replaceAll, split or Pattern.compile on each call

## Thesis
A regex that a method applies on every call — through `Pattern.compile` inside the method body, `String.matches`, `String.replaceAll`, `String.replaceFirst`, `String.split` with a multi-character or metacharacter pattern, or `Pattern.matches` — is compiled once into a `private static final Pattern` and used through `PATTERN.matcher(input)`, `PATTERN.split(input)` or `matcher.replaceAll`.

## Rationale
A regular expression must first be compiled into a `Pattern` before it can match; the compilation parses the expression and builds the matcher program, work that depends only on the expression text. `String.matches(regex)` is specified to yield the same result as `Pattern.matches(regex, input)`, which compiles the expression on every invocation; `replaceAll` and `replaceFirst` are specified as `Pattern.compile(regex).matcher(this)…`, and `split` compiles unless the pattern is a single literal character. A `Pattern` is immutable and safe for use by multiple concurrent threads, and all the state of a match lives in the `Matcher`, so one static instance serves every call and every thread, and the per-call cost drops to the match itself.

## Example
```java
bad:  boolean ok(String s) { return s.matches("[A-Z][a-z]+(-[a-z]+)*"); }
      String[] parts(String line) { return line.split("\\s*,\\s*"); }
good: private static final Pattern NAME = Pattern.compile("[A-Z][a-z]+(-[a-z]+)*");
      private static final Pattern COMMA = Pattern.compile("\\s*,\\s*");
      boolean ok(String s) { return NAME.matcher(s).matches(); }
      String[] parts(String line) { return COMMA.split(line); }
```

## Limits
A regex built from a runtime value (a user-supplied filter) cannot be static; it is compiled once per distinct value and cached when the same value recurs on a hot path. `String.split` on a single literal character that is not a regex metacharacter takes a fast path without compiling and is fine. A one-off call at startup or in a test needs no hoisting. A `Matcher` is not safe for concurrent use; the `Pattern` is the shared object, the `Matcher` is per call.

## Validator
On the triggered hunk find each `Pattern.compile` inside a method body (not a static field initializer) and each `matches`, `replaceAll`, `replaceFirst`, `split` (multi-character or metacharacter argument) or `Pattern.matches` on a `String` with a constant regex. Confirm the enclosing method is called repeatedly (a request handler, a parser, a loop body). Validator question: **does this method compile the same constant regular expression on every call?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PF-16`, severity minor, `file`, `symbol`, `code` = the call quoted verbatim from the diff, `fix` = the `static final Pattern` and its use, `rationale` naming the recompilation per call).

## Source
`java.util.regex.Pattern` class Javadoc, Java SE 21 — "A regular expression, specified as a string, must first be compiled into an instance of this class... All of the state involved in performing a match resides in the matcher, so many matchers can share the same pattern"; "Instances of this class are immutable and are safe for use by multiple concurrent threads. Instances of the Matcher class are not safe for such use"; `Pattern#matches(String, CharSequence)` — "If a pattern is to be used multiple times, compiling it once and reusing it will be more efficient than invoking this method each time." `java.lang.String#matches`, `#replaceAll`, `#replaceFirst` Javadoc — each "yields exactly the same result as" the corresponding `Pattern.compile(regex)…` expression; `#split` — the single-character fast path, otherwise `Pattern.compile(regex)` (JDK 21 source).

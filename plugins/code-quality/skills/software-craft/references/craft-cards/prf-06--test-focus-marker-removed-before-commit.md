---
title: A focus or exclusive-run marker added to a test to run only that test while debugging is removed before the change lands, so the whole suite runs on the build system
rule_id: PRF-06
domain: performance
step: [test, review]
applies_to: [tests]
triggers: ['(?:(?<![.\w])f(?:describe|context|it)|(?<!\w)F(?:Describe(?:Table(?:Subtree)?)?|Context|When|It|Specify|Entry))\s*(?:\(|[.]\s*(?:each|failing)\b)', '\b(?:describe|context|suite|it|test|specify)(?:\s*[.]\s*concurrent)?\s*(?:[.]\s*only|\[\s*[''"]only[''"]\s*\])\s*(?:\(|[.]\s*(?:each|failing)\b)|[,(]\s*(?:\w+\s*[.]\s*)?Focus\s*[,)]']
scope: file
check_kind: mechanical
severity_default: major
---

# A focus or exclusive-run marker added to a test to run only that test while debugging is removed before the change lands, so the whole suite runs on the build system

## Thesis
A marker that focuses a test or a test group so that the framework runs only the marked tests of the suite or file that carries it (an only modifier on the test or group call, an f or F prefix on its name, a Focus decorator among its arguments) is removed after the failing test it was added for is fixed and before the change is committed, so that every test is executed on the build system. Every such marker is removed, since running all tests requires removing all of them.

## Rationale
While a focus marker is present, the framework skips the other tests of the suite or file that carries it and runs only the focused ones. That is what makes the marker useful in debugging: a failing test is rerun rapidly while the code is iterated on, without executing all the other tests. Once committed, the same marker restricts the run on the build system as well, and running every test there again requires going back and removing every marker. Committing a focused test by accident is a documented pain point, and tools guard against it. One framework, by default, makes a suite that passes with programmatically focused tests exit with a non-zero status code, which most continuous-integration systems catch and flag. One lint rule raises a warning whenever the exclusivity feature is used and is enabled in its plugin's recommended configuration. Another linter states its purpose as preventing temporary statements, such as focused test nodes, from being left in the code.

## Example
```go
bad:  var _ = Describe("Parser", func() {
          FIt("rejects empty input", func() { /* ... */ })
          It("rejects oversized input", Focus, func() { /* ... */ })
      })
good: var _ = Describe("Parser", func() {
          It("rejects empty input", func() { /* ... */ })
          It("rejects oversized input", func() { /* ... */ })
      })
```

## Limits
Focus chosen from the command line, by a filter on test descriptions or on source files, is outside the rule: the rule concerns focus declarations programmed into the source. A skip marker is outside the rule as well; the focused-test lint rule lists skip forms among the patterns it does not warn on. A marker reached through an alias escapes a match on the source text: one lint rule documents an alias of the only form as an edge case it cannot detect, and another documents that its patterns, by default, match the expression as it appears in the source, so a renamed import escapes them. The rule reaches only frameworks that offer an in-source focus marker.

## Validator
Grep the hunk's added lines for a focus marker: an only modifier on a suite or test call, in member or index form; an f-prefixed suite or test call; an F-prefixed container, subject or table-entry node; a Focus decorator in a node's argument list. Open the hunk and confirm that the match is the test framework's focus form in a test file, not a same-named helper such as a curve-fitting `fit` function or a query builder's `only`, and not text inside a string or a comment. Where the hunk binds a focus form to a new name, trace that name to its calls. Validator question: **Does the hunk add a focus or exclusive-run marker to a test or a test group?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PRF-06`, severity major, `file`, `symbol`, `code` = the line that carries the marker, quoted verbatim, `fix` = the same test or group call with the marker removed, in the file's language, `rationale` = names that the marker makes the framework run only the focused tests of its suite or file, so the build system no longer executes every test).

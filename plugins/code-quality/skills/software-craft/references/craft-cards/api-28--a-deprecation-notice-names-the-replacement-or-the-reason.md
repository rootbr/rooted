---
title: A deprecation notice names the replacement to use, or states the reason when there is no replacement
rule_id: API-28
domain: interface
step: [implement, document]
applies_to: [public-api, library, prose]
triggers: ['@[Dd]eprecated\b', '#!?\[deprecated\b', '^\s*//\s*Deprecated:', 'DeprecationWarning|FutureWarning|[.]deprecated\(|[.][.]\s+(?:version-)?deprecated::', 'util[.]deprecate\(|process[.]emitWarning\(']
scope: hunk
check_kind: mechanical
severity_default: minor
---

# A deprecation notice names the replacement to use, or states the reason when there is no replacement

## Thesis
The text attached to a deprecation marker names what callers use or do instead (a replacement element, or the change to make at the call site), or, where no replacement exists, states the reason the element should no longer be used. That text is the deprecation tag's text in a doc comment, a doc-comment paragraph that opens with the documentation convention's deprecation keyword, the body of a documentation directive that marks a deprecation, the note or message of a deprecation attribute, or the message of a deprecation decorator or of a warning emitted at run time. A marker with no text, or with text that only repeats that the element is deprecated, does neither.

## Rationale
Tools show this text to the caller of a deprecated element: a compiler, type checker or linter that warns on each use can include it in the warning and issues a generic message when the marker carries none, and a documentation generator shows it with the element's deprecation. Wherever the caller reads it, the text tells the caller what to use or do instead, or why the element should no longer be used, and a generic message tells neither. In a documentation format that supports links, the notice links the replacement. A replacement often has subtly different semantics, so a notice that names one also says where they differ.

## Example
```typescript
bad:  /** @deprecated */
      export function parseDate(text: string): Date { ... }
good: /** @deprecated Use {@link parseInstant}; it rejects text with no time zone. */
      export function parseDate(text: string): Date { ... }
      export function parseInstant(text: string): Date { ... }
```

## Limits
The documented conventions differ on how much a notice carries. One strongly recommends the reason in every case, together with the replacement where there is one; another asks for the reason, the replacement or both; a third asks for the alternatives, or for the reason when no clear alternative is available. What all three require at the least is a replacement or a reason, so a notice that has either one is not a finding, and the finder flags only a notice that has neither.

A member that carries no deprecation marker of its own is outside the rule. A member's own marker is checked even inside a deprecated type or module: a marker without text gives the generic message at that member's use, whatever the enclosing notice says.

A longer explanation can live in the release notes; the notice itself still carries the replacement or the reason.

The rule reaches the text of the notice, not the release in which it is added. For a replaced element, one standard library's documented policy adds the notice no earlier than the release after the one that first carries the replacement, so that callers see the element as deprecated only when every supported release includes the replacement and they can easily switch.

## Validator
In the hunk, find each added deprecation marker: a deprecation annotation, attribute or decorator, a deprecation tag in a doc comment, a doc-comment paragraph that opens with the documentation convention's deprecation keyword, a documentation directive that marks a deprecation, and a call that emits a deprecation warning at run time. Read the text attached to it: the tag's or the paragraph's text, the attribute's note or message, the directive's body, or the message argument of the decorator or of the warning call. Where the marker carries no text of its own, read the doc comment of the same element and take its deprecation tag's text as the notice. Skip a marker whose text lies outside the hunk and its context, or whose message is a value built elsewhere. Skip a mention of the warning category that emits nothing, such as a test that expects the warning or a filter that silences it. Count a notice as complete when it names what to use or do instead (an element, as a link or in plain words, or the change to make at the call site), or gives a reason the element should no longer be used. Validator question: **Does the text attached to this deprecation marker name neither what to use or do instead nor a reason the element should no longer be used?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: API-28`, severity minor, `file`, `symbol`, `code` = the deprecation marker and its attached text quoted verbatim from the diff, `fix` = the same marker with text that names what to use or do instead, linked where the documentation format allows, or, where there is none, the reason the element should no longer be used, in the file's language, `rationale` = the warning or documentation each caller reads at its use of the element, which without that text gives no directions for fixing the call site).

## Source
`java.lang.Deprecated` Javadoc, `@apiNote`, OpenJDK `jdk-21-ga` — "It is strongly recommended that the reason for deprecating a program element be explained in the documentation, using the {@code @deprecated} javadoc tag. The documentation should also suggest and link to a recommended replacement API, if applicable. A replacement API often has subtly different semantics, so such issues should be discussed as well." (fetched); Go Doc Comments, "Deprecations" — "Paragraphs starting with `Deprecated: ` are treated as deprecation notices. Some tools will warn when deprecated identifiers are used.", "Deprecation notices are followed by some information about the deprecation, and a recommendation on what to use instead, if applicable." (fetched); The Rust Reference, "The `deprecated` attribute" — "`rustc` will issue warnings on use of `#[deprecated]` items.", "`deprecated` --- Issues a generic message.", "`rustdoc` will show item deprecation, including the `since` version and `note`, if available.", "`note` --- Specifies a string that should be included in the deprecation message. This is typically used to provide an explanation about the deprecation and preferred alternatives.", "When applied to an item containing other items, such as a module or implementation, all child items inherit the deprecation attribute." (fetched); Rust RFC 1270 "Deprecation", `note` field — "`note` should contain a human-readable string outlining the reason for deprecating the item and/or what to use instead." (fetched); PEP 702 "Marking deprecations using the type system" — "contains a message that should be shown by the type checker when it encounters a usage of the decorated object", "Type checkers should produce a diagnostic whenever they encounter a usage of an object marked as deprecated.", "For users who encounter deprecation warnings in their IDE or type checker output, the messages they receive should be clear and self-explanatory." (fetched); Google TypeScript Style Guide, "Deprecation" — "A deprecation comment must include simple, clear directions for people to fix their call sites." (fetched); NumPy NEP 23, "Implementing deprecations and removals" — "shall include information on alternatives to the deprecated functionality, or a reason for the deprecation if no clear alternative is available. Note that release notes can include longer messages if needed.", "shall use ``DeprecationWarning`` by default", "shall be mentioned in the documentation for the functionality. A ``.. deprecated::`` directive can be used for this." (fetched); Go wiki "Deprecated", "Deprecations in the Go standard library" — "an official deprecation notice for `F1` should not be added until Go 1.N+1. This ensures that Go developers only see `F1` as deprecated when all supported Go versions include `F2` and they can easily switch." (fetched); SonarSource RSPEC-1123 "Deprecated elements should have both the annotation and the Javadoc tag" — "the tag can be used to explain when it was deprecated, why, and how references should be refactored" (fetched); Checkstyle `MissingDeprecated` — "The @deprecated javadoc tag is used to document why something is deprecated and what, if any, alternatives exist." (fetched); typescript-eslint `no-deprecated` — messages "`{{name}}` is deprecated." and "`{{name}}` is deprecated. {{reason}}" (fetched); staticcheck SA1019 — "%s is deprecated: %s" (fetched). Caveat: the rule rests on the documented conventions of these ecosystems; no fetched or relayed study measures what a notice without a replacement or a reason costs its callers, and the release-timing policy in the Limits is stated for one standard library only.

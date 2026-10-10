---
title: A change adds no new use of an element marked deprecated in non-deprecated code outside the element's own package
rule_id: API-32
domain: interface
step: [implement]
applies_to: [universal]
triggers: ['@SuppressWarnings\(.*\b(deprecation|removal)\b|@Suppress\(.*\bDEPRECATION\b|#!?\[(allow|expect)\(.*\bdeprecated(_in_future)?\b|(?i:(eslint-disable\S*|nolint\S*|lint:ignore|noqa|type:\s*ignore|pyright:\s*ignore)\b.*\b(no-deprecated|(report)?deprecat\w*|SA1019)\b)|#pragma\s+(warning\s+disable\b.*\b(CS)?0?6(18|12)\b|(clang|GCC)\s+diagnostic\s+ignored\s+"-Wdeprecated)|\b(filterwarnings|simplefilter)\(.*\b(Pending)?DeprecationWarning\b', '(?i)\bdeprecat', '(::|[.])\w+\(']
scope: callers
check_kind: semantic
severity_default: minor
---

# A change adds no new use of an element marked deprecated in non-deprecated code outside the element's own package

## Thesis
A line a change adds, in code that is not itself deprecated and that lies outside the package or module defining the element, uses the replacement the deprecation notice names in place of any call, reference, import, subclass, implementation or override of an element marked deprecated. The mark is the language's deprecation annotation, attribute or doc tag, or a doc-comment paragraph that begins "Deprecated:". Where the notice names no replacement, the added line is written to avoid the element. A suppression written on the new use (a suppression annotation, an allow attribute, a lint-disable or ignore comment, a warning pragma, a warnings filter) silences the diagnostic and leaves the use in the code, so the use still counts.

## Rationale
An element marked deprecated is one programmers are discouraged from using, for one of several reasons, for example: its use is likely to lead to errors, it may be changed incompatibly or removed in a future version, or a newer, usually preferable alternative supersedes it. A new use that arrives while old ones are being removed makes the amount of work to remove the element grow, and a use of an element already marked for removal blocks upgrading the dependency that defines it. One secure-coding standard rates the use of deprecated or obsolete methods as able to lead to erroneous behaviour, at severity low, likelihood unlikely, priority P2, level L3; one analyzer rates a use of a deprecated element Minor and a use of one marked for removal Major, each with a 15-minute remediation estimate. Default tool settings can let a new use through unflagged: one compiler reports no type error for deprecated code on its own; another prints only a summary of the source files that use or override deprecated members unless its detail option is set; one type checker leaves the diagnostic off in every mode but strict; another reports it only when its deprecated error code is enabled; one linter ships the check in its strict configuration and needs type information; and one runtime keeps its deprecation warning silenced for packaged code distributed as an importable module. The rule therefore judges the added use itself, whether or not a configured check reports it.

## Example
```java
bad:  // Client.fetchAll carries @Deprecated; its notice names fetch as the replacement
      @SuppressWarnings("deprecation")
      Result result = client.fetchAll(query);
good: Result result = client.fetch(query);
```

## Limits
The sources split on three placements, which the rule leaves to the project's own convention: a use inside code that is itself deprecated, a use inside the package or module that defines the element, and a use in that package's own tests. One compiler's annotation contract warns on uses in non-deprecated code, and one checker exempts deprecated functions, the defining package and its external test package; the type-checker specification asks for a diagnostic on uses in the defining module, and one compiler applies the mark both inside and outside the defining library and skips only a use inside an item that carries that same deprecation. An element deprecated in a version later than the one the project targets is outside the rule: one checker compares the targeted version with the version that deprecated the element and stays silent when the target is older. An element deprecated only in prose is outside the rule, which keys on a marker: a soft deprecation, which issues no warning and is only mentioned in the documentation; an API whose documentation simply points to a preferred one without a formal mark; and an obsolete method, which has no automatic means of detection. A portion of the project that the project context declares will stay on a deprecated API, with no plan for moving off it, is a documented tolerance: one linter suggests disabling its check in such portions, and the type-checker specification notes that application developers targeting one specific version may not care about deprecations. Existing uses the change does not add are outside the rule, which judges added lines only.

## Validator
Grep the hunk's added lines for a deprecation suppression (a suppression annotation, an allow or expect attribute, a lint-disable, nolint or ignore comment naming a deprecation check, a warning pragma, a warnings filter) and for the stem deprecat. For each name an added line calls, references, imports, extends, implements or overrides, open its declaration at scope callers and read the declaration and its doc comment for a deprecation annotation, attribute or doc tag, or a doc-comment paragraph that begins "Deprecated:". For a marked element, confirm that no declaration enclosing the added line (its function, its type or its module) carries a deprecation mark, that the added file lies outside the element's defining package or module and that package's tests, that the version the project targets is at or after the version that deprecated the element, and that the project context declares no tolerance for that portion of the code. Validator question: **Does a line the change adds, outside deprecated code and outside the element's defining package or module and that package's tests, call, reference, import, subclass, implement or override an element that carries a deprecation mark in the version the project targets, with no declared project tolerance for that code?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: API-32`, severity minor, `file`, `symbol`, `code` = the added line that uses the deprecated element, with any suppression written on it, `fix` = the same line rewritten to the replacement the deprecation notice names, or rewritten to avoid the element where the notice names none, in the file's language, `rationale` = the deprecated element, its notice and named replacement, and whether it is marked for removal).

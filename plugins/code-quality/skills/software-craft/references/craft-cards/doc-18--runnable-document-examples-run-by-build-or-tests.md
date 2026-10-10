---
title: A runnable code example added to a document is compiled or executed by the project's build or tests
rule_id: DOC-18
domain: docs
step: [document, test]
applies_to: [prose]
triggers: ['^\s*(```|~~~)\s*((python|py|pycon|go|golang|rust|rs|java|ts|typescript|js|javascript|sh|bash|console|shell)\b.*)?$', '^\s*//\s*Output:']
scope: callers
check_kind: semantic
severity_default: minor
---

# A runnable code example added to a document is compiled or executed by the project's build or tests

## Thesis
A code example that a change adds to a document, and that the document presents as runnable (a usage block, a quick start, a tutorial step, an example with its stated output), is compiled or executed by the project's build or tests, and executed with its output compared when the document states one: a documentation-test runner reads it, or it is copied from a source file that the build compiles or the tests execute, under a check that fails when the document's copy no longer matches.

## Rationale
Among documentation correctness issues, code examples were the documentation type most often affected: 50% of the cases with a labelled documentation type, ahead of installation guidelines at 20%. Bugs can affect code examples as they can affect production code, and a recommended mitigation is to apply testing techniques to code examples as to production code. Surveyed practitioners indicated erroneous code examples (59%) and outdated examples (51%) as important documentation issues. Example code is often copied verbatim by users. The documentation toolchains carry the test: one runner executes documentation examples as tests so that they stay up to date and working, one compiles example routines and compares their standard output with a concluding expected-output comment, one verifies that interactive examples in docstrings and in standalone text files still work as documented, and an embedding tool's verify mode checks in continuous integration that re-embedding would change no document.

## Example
```rust
bad:  // README.md, a quick start that no test target reads:
      ~~~rust
      let sum = demo::add(2, 3);
      // Output: 5
good: // README.md: assert_eq!(demo::add(2, 3), 5);
      // src/lib.rs: the README's code blocks run with the doctests
      #[doc = include_str!("../README.md")]
      #[cfg(doctest)]
      pub struct ReadmeDoctests;
```

## Limits
An incomplete snippet that the document shows as a fragment, such as a call on one routine that cannot be compiled and run as shown, is outside the rule; testing such snippets might not be trivial. Compilation alone satisfies the rule for an example that states no output: an example runner compiles such an example without executing it. An example copied into the document from a source file that the build compiles or the tests execute satisfies the rule when a continuous-integration check verifies that re-embedding changes no document. An installation instruction is outside the rule: the study that recommends testing code examples counts installation guidelines as a separate documentation type.

## Validator
Grep the hunk for a code block added to a document: an opening fence with or without a language tag, a concluding expected-output comment. Read the prose around the block to decide whether the document presents it as runnable (a usage step, a quick start, an example with its stated output) or as a fragment. Open the document's callers: the build and test configuration, every file that includes, embeds or doctests the document, and the continuous-integration steps. Trace whether any of them compiles or executes the block, executing it and comparing the output when the document states one, or verifies it against a source file that the build compiles or the tests execute. Validator question: **Does the change add a code example that the document presents as runnable and that no build, test or embedding check compiles, executes or verifies, or whose stated output no test compares?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: DOC-18`, severity minor, `file`, `symbol`, `code` = the example's opening fence and first code line, quoted verbatim from the diff, `fix` = the wiring that makes the project's documentation-test runner or build read the example and compare any output the document states, in the file's language, `rationale` = names code examples as the documentation type most often hit by correctness issues and the test that keeps this one working).

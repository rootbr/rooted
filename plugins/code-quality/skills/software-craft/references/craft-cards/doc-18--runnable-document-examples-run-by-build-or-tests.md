---
title: A runnable code example added to a document is compiled or executed by the project's build or tests
rule_id: DOC-18
domain: docs
step: [document, test, review]
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

## Source
- DOI 10.1109/ICSE.2019.00122, 'Software Documentation Issues Unveiled', § IV.A Correctness and 'Discussion and Implications' (fetched): "The type of documentation most frequently impacted by correctness issues was code examples (e.g., [66]), accounting for 50% of the cases in which we labeled a documentation type, followed by installation guidelines (20%, e.g., [66])." / "as it happens with production code, bugs can affect code examples as well. A recommendation to mitigate this problem is to apply testing techniques on code examples as done on production code. However, this might not be trivial since documentation often reports incomplete examples rather than entirely runnable programs (e.g., a snippet of code on how to use an API is shown, but the snippet cannot be actually compiled and run)."
- DOI 10.1145/3377811.3380405, 'Software Documentation: The Practitioners' Perspective', § 4 Correctness and Figure 2 (fetched): "Erroneous code examples were also recognized as an important issue by the surveyed participants (59% of them)." / Figure 2, Up-to-dateness, % important: "Outdated example 51%"
- rustdoc, 'Documentation tests' (rust-lang/rust src/doc/rustdoc/src/write-documentation/documentation-tests.md) (fetched): "`rustdoc` supports executing your documentation examples as tests. This makes sure that examples within your documentation are up to date and working." / "you could write this into your `lib.rs` to test your README as part of your doctests"
- Go package testing, '# Examples' (golang/go src/testing/testing.go) (fetched): "Example functions may include a concluding line comment that begins with "Output:" and is compared with the standard output of the function when the tests are run." / "Example functions without output comments are compiled but not executed."
- Python doctest (python/cpython Doc/library/doctest.rst) (fetched): "verifying that all interactive examples still work as documented" / "Another simple application of doctest is testing interactive examples in a text file."
- embedme README, 'CI Checks' and 'Why?' (zakhenry/embedme) (fetched): "Simple utility to embed source files into markdown code blocks" / "If you're using continuous integration, you can pass the flag `--verify` to `embedme` to check that there are no changes expected to your files" / "you really should be writing unit tests on your example code"
- Rust API Guidelines C-QUESTION-MARK (rust-lang/api-guidelines src/documentation.md) (fetched): "Like it or not, example code is often copied verbatim by users."
- Caveat: testing code examples is the study's recommendation, not a measured effect; the practitioners' survey reports "Testing activities on code examples, however, were not mentioned by the surveyed developers."

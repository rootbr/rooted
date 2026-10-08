---
title: Every test is declared the way its runner discovers tests, with the runner's test marker, name pattern and signature, so that the runner collects and runs it
rule_id: TST-26
domain: tests
step: [test, review]
applies_to: [tests]
triggers: ['^\s*public\s+void\s+test\w*\s*\(\s*\)', '^\s*func\s+(Test[a-z]\w*\s*\(|Test\w*\s*\((?!\s*\w+\s+\*testing[.][TM]\s*\)))', '^\s*(async\s+)?def\s+(?!test)\w*test\w*\s*\(\s*self\b', '^\s*(pub\s+)?fn\s+(test_\w+|\w+_test|it_\w+|should_\w+)\s*\(\s*\)', 'signal:added_file', 'signal:test_file']
scope: file
check_kind: mechanical
severity_default: major
---

# Every test is declared the way its runner discovers tests, with the runner's test marker, name pattern and signature, so that the runner collects and runs it

## Thesis
A function or method written as a test carries what its runner needs to collect and run it: the runner's test annotation or attribute where the runner requires one, the test-name pattern and the file-name pattern where the runner discovers tests by name, and a visibility, static-ness, return type and parameter signature the runner accepts. A test meant to be disabled keeps that declaration and adds the runner's own skip or ignore construct.

## Rationale
A test runner tells tests apart from the other functions in a test file by its discovery convention: a marker attribute or annotation, a name prefix inside a file whose name matches a pattern, a signature the runner accepts, or several of these together. A function that misses the convention can be left out of the run: one runner does not run a test unless it carries the test annotation, and another ignores a private method, a static method, a method returning a value unless it is a test-factory method, and a private nested test class, whose entire nested suite is then skipped. One toolchain's test command runs an analyzer that reports common mistakes in test declarations, such as malformed names and incorrect signatures, some of which may cause tests not to run. A test switched off on purpose keeps the runner's marker and adds the runner's skip or ignore construct, which makes clear that the disabling is intended and leaves the test in the run's ignored or skipped count, with a reason where the construct takes one. The rule restores what the convention exists for: every function written as a test is one the runner knows to treat as a test.

## Example
```rust
bad:  fn it_adds_two() {
          assert_eq!(add(2, 2), 4);
      }
good: #[test]
      fn it_adds_two() {
          assert_eq!(add(2, 2), 4);
      }
      #[test]
      #[ignore = "slow"]
      fn it_adds_many() { assert_eq!((0..1000).fold(0, add), 499500); }
```

## Limits
Each runner has its own convention, and a runner may let a project customize its test discovery; the declaration is checked against the runner and the discovery configuration the project uses. A runner that accepts several visibilities, or static methods, accepts each of them, so only a declaration the runner ignores is a finding. A function in a test module that sets up common scenarios or performs common operations is a helper, not a test, and needs no test marker; a helper that a checker could take for an unmarked test can have its visibility reduced to non-public where possible. The rule reaches the declaration only: what a collected test asserts is outside it.

## Validator
Grep the hunk for function and method declarations in test files, and for files added under a test directory. Open the file and identify its runner from the imports, the attributes or annotations in use, and the test configuration. For each function that carries a test marker, whose name reads as a test (a test-like prefix or suffix), or whose body holds assertions, check against that runner: the test marker where the runner requires one; the function name and the file name against the runner's discovery patterns, as the project configures them; the visibility, static-ness, return type and parameters against what the runner accepts; and any enclosing nested test group for the same. Trace each candidate that misses one of these: a function called from other tests or fixtures is a helper and is not a finding. Validator question: **Does a function written as a test, called by no other code, miss the marker, name pattern, file-name pattern, visibility, static-ness, return type or parameter signature its runner needs to collect it?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: TST-26`, severity major, `file`, `symbol`, `code` = the test's declaration line with its attributes or annotations, quoted verbatim from the diff, `fix` = the same declaration with the runner's marker, name, file name, visibility, return type or signature corrected, or with the marker plus the runner's skip or ignore construct and a reason where the test is meant to be disabled, in the file's language, `rationale` = names the part of the declaration the runner requires and states that the test, as declared, is not collected).

## Source
- Error Prone bug pattern `JUnit4TestNotRun`, google/error-prone docs/bugpattern/JUnit4TestNotRun.md (fetched): "JUnit 4 tests will not be run unless annotated with @Test." / "If you intend for this test method not to run, please add both an @Test and an @Ignore annotation to make it clear that you are purposely disabling it. If this is a helper method and not a test, consider reducing its visibility to non-public, if possible."
- SonarSource RSPEC S5810, sonar-java rules/java/S5810.html (fetched): "JUnit5 supports default package, public and protected visibility" / "But JUnit5 ignores without any warning: private methods static methods methods returning a value without being a TestFactory @Nested classes with private visibility (the entire nested test suite is silently skipped)".
- `go vet` analyzer `tests`, golang/website _content/doc/go1.24.md, Vet (fetched): "reports common mistakes in declarations of tests, fuzzers, benchmarks, and examples in test packages, such as malformed names, incorrect signatures [...] Some of these mistakes may cause tests not to run. This analyzer is among the subset of analyzers that are run by `go test`."
- Go package `testing` documentation, golang/go src/testing/testing.go, package comment (fetched): "func TestXxx(*testing.T) where Xxx does not start with a lowercase letter. The function name serves to identify the test routine." / "give that file a name ending in \"_test.go\"".
- Python `unittest` documentation, python/cpython Doc/library/unittest.rst, Basic example and Skipping tests (fetched): "individual tests are defined with methods whose names start with the letters ``test``. This naming convention informs the test runner about which methods represent tests." / "skip(reason) Unconditionally skip the decorated test. *reason* should describe why the test is being skipped." / example run output "OK (skipped=4)"
- pytest documentation, pytest-dev/pytest doc/en/explanation/goodpractices.rst, Conventions for Python test discovery (fetched): "search for ``test_*.py`` or ``*_test.py`` files" / "``test`` prefixed test functions or methods inside ``Test`` prefixed test classes (without an ``__init__`` method). Methods decorated with ``@staticmethod`` and ``@classmethods`` are also considered." / "how to customize your test discovery".
- Rust official documentation, rust-lang/book src/ch11-01-writing-tests.md and src/ch11-02-running-tests.md (fetched): "This attribute indicates this is a test function, so the test runner knows to treat this function as a test. We might also have non-test functions in the `tests` module to help set up common scenarios or perform common operations, so we always need to indicate which functions are tests." / "It’s possible to mark a test as ignored so that it doesn’t run [...] Because we haven’t done that here, the summary shows `0 ignored`." / "After `#[test]`, we add the `#[ignore]` line to the test we want to exclude."
- Caveat: the evidence is each runner's own documentation and checkers; which declaration parts a runner requires differs per runner, and the count of tests lost to undiscoverable declarations is not measured by these sources.

---
title: A test passes or fails the same whether it runs alone, in any order or in parallel with the other tests, because it relies on no state that another test sets or leaves in shared variables, files, the working directory or environment variables
rule_id: TST-21
domain: tests
step: [test]
applies_to: [tests]
triggers: ['@(TestMethodOrder|Order|FixMethodOrder|TestClassOrder)\b|\bMethodOrderer\b|pytest[.]mark[.](order|dependency)\b|\b(os[.](environ\[|putenv|chdir|Setenv|Chdir|Unsetenv)|process[.](env[.]\w+\s*=|chdir\()|(std::)?env::(set_var|remove_var|set_current_dir)|System[.]setProperty\()|^\s*(private\s+|protected\s+|public\s+)?static\s+(?!final\b)[\w<>\[\],? ]+\s+\w+\s*(=|;)|^\s*(pub(\([\w:]+\))?\s+)?static\s+(mut\b|\w+\s*:\s*(Atomic\w+|Mutex|RwLock|LazyLock|OnceLock|Lazy)\b)|^var\s+\w+|^(export\s+)?let\s+\w+|^[a-z_]\w*\s*(:\s*[\w\[\], ]+)?\s*=\s*(\[\]|\{\}|dict\(|list\(|set\(|defaultdict\()|\b(setUpClass|setUpModule|beforeAll)\b|@(BeforeAll|BeforeClass)\b|scope\s*=\s*[\x22\x27](module|session|class|package)[\x22\x27]', '(?i)[\x22\x27\x60]([^\x22\x27\x60]*(/tmp/|tmp_|test[-_]?out(put)?)[^\x22\x27\x60]*|[^\x22\x27\x60]*[.](txt|json|db|sqlite|csv|log))[\x22\x27\x60]']
scope: file
check_kind: semantic
severity_default: major
---

# A test passes or fails the same whether it runs alone, in any order or in parallel with the other tests, because it relies on no state that another test sets or leaves in shared variables, files, the working directory or environment variables

## Thesis
A unit test is self-contained, so it gives the same result run alone, in any order or in parallel with the other tests: it sets up the state it needs and depends neither on another test having run first nor on what another test leaves in shared state — mutable static or module-level variables, files at fixed paths, the current working directory or environment variables. A test that must change such state works on a per-test resource such as a file of its own, or initializes the state before and clears it after each test and runs one at a time, not in parallel with other tests.

## Rationale
When tests run in parallel and write and read the same file, one test can overwrite it between another test's write and read, and the second test then fails not because the code is incorrect but because the tests interfered with each other. Initializing and clearing shared state around each test does not protect tests that run at the same time: a framework helper that sets an environment variable or the working directory and restores it after the test cannot be used in parallel tests, because it affects the whole process, and the documented remedies for a shared file are a different file for each test or running the tests one at a time. A test that often fails as part of a larger suite but not when run alone is a good bet that something from a different test is interfering with it. Tests that allocate resources also used by other tests might cause resource interference that makes a test's outcome non-deterministic; in a study of flaky tests, test methods sharing resources this way showed a strong relationship (Kendall's τ = 0.62) with flaky tests caused by concurrency issues, and to remove that sharing the study duplicated the files used by different tests under unique identifiers, so that each test worked on independent resources. Dependent tests do exist in practice, and a random order of test executions can effectively detect such dependencies; test runners offer a randomized execution order and report its seed for reproducibility, and one documented reason to run test classes in a random order is to ensure there are no accidental dependencies between them. Cases are expected to be able to run individually through a test filter, which is why they do not depend on the execution of other cases for success or initial state, and three of the experts interviewed on unit-test quality named the independence of unit tests, one of them because it reduces the risk of interference of some tests toward others, which can cause forms of test flakiness.

## Example
```rust
bad:  #[test] fn saves_report() {
          env::set_current_dir(temp_dir()).unwrap();
          save_report("test-output.txt", "a");
          assert_eq!(read_to_string("test-output.txt").unwrap(), "a");
      }
good: #[test] fn saves_report() {
          let path = temp_dir().join(format!("saves_report-{}.txt", process::id()));
          save_report(&path, "a");
          assert_eq!(read_to_string(&path).unwrap(), "a"); std::fs::remove_file(&path).unwrap();
      }
```

## Limits
Unit tests typically should not rely on the order in which they run; there are times when enforcing an execution order is necessary, for example in integration or functional tests where the sequence of the tests is important. The documented alternative to a file of each test's own is to run the tests one at a time. Fixtures shared at class or module level are to be used with care, since they do not play well with test parallelization and they break test isolation. The rule's scope is the state a unit test touches; tests against a real shared dependency such as a database, and tests of thread interleavings, fall outside it.

A per-test file written to a directory that outlives the run, such as the system's temporary directory, is still removed when the test ends, by a cleanup the framework manages or by the test itself, unless it sits in a per-test temporary directory the framework removes.

## Validator
Grep the hunk for an execution-order annotation or marker, writes to environment variables or process-wide properties, changes of the working directory, mutable static or module-level variables, class-, module- or session-scoped fixtures, and string literals naming a fixed file path. Open the test file and, for each hit, trace which tests write the state and which tests read it: whether a test modifies it without a per-test copy and either without initializing and clearing it around each test or while other tests run in parallel with it, whether a test reads a value that only another test sets, whether two tests use the same fixed path, and whether the file enforces an order between unit tests. Validator question: **Does a unit test in the file depend on another test having run first, or change shared state — a mutable static or module-level variable, a file at a fixed path, the working directory or an environment variable — without working on a per-test copy of it, and either without clearing it after itself or while other tests can run in parallel with it?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: TST-21`, severity major, `file`, `symbol`, `code` = the line that writes or reads the shared state or declares the order, verbatim from the diff, `fix` = the test working on a uniquely named per-test resource, or setting up its own state and clearing it per test while running one at a time, in the file's language, `rationale` = which shared state couples which tests and how the outcome then depends on run order or parallel timing).

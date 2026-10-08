---
title: A long-running test carries the selection marker the project's runner filters on, so the routine run can exclude it and a deliberate run includes it
rule_id: TST-28
domain: tests
step: [test, review]
applies_to: [tests, build-config]
triggers: ['(?i)[\x22\x27\x60][\w./-]*(postgres|mysql|mariadb|mongo|redis|kafka|rabbitmq|localstack|elasticsearch|selenium)[\w./-]*:[\w.-]+[\x22\x27\x60]', 'signal:test_file']
scope: file
check_kind: semantic
severity_default: minor
---

# A long-running test carries the selection marker the project's runner filters on, so the routine run can exclude it and a deliberate run includes it

## Thesis
A time-consuming test (integration and other high-level tests tend to be slower than unit tests) carries the selection mechanism the project's test runner filters on: a registered marker or tag, a size attribute, a skip under the runner's short mode, an ignore attribute, or a place in a separate suite. The routine run can then deselect it, and a deliberate run includes it when there is time to wait for its results.

## Rationale
Test runners document this selection as a feature of their own. A short-mode flag tells long-running tests to shorten their run time, so that a sanity-check run does not spend time running exhaustive tests, and a test checks that mode and skips itself. An ignore attribute excludes time-consuming tests from most runs, one flag runs only the ignored tests, and another runs all tests whether ignored or not. A registered slow marker is deselected with a not-slow expression, tags filter test discovery and execution, and a size filter tests only targets of the listed sizes, with a minus sign excluding a size. Without the mark, excluding the time-consuming test means listing as arguments every test that should run instead. Controlling which tests run keeps the routine results quick to return, and splitting the suite into unit and integration parts helps keep build times manageable because high-level tests tend to be slower. In an observational study of test runs in the IDE, developers frequently selected a specific set of tests to run, in most cases one test, and those runs took a very short amount of time.

## Example
```python
bad:  def test_order_roundtrip():
          with PostgresContainer("postgres:16") as db:
              assert OrderRepo(db.get_connection_url()).roundtrip()
good: @pytest.mark.slow  # registered marker; routine run: -m "not slow"
      def test_order_roundtrip():
          with PostgresContainer("postgres:16") as db:
              assert OrderRepo(db.get_connection_url()).roundtrip()
```

## Limits
Splitting off the slow suite has a documented cost: when only the fast suite gates merges, code that breaks the build can be merged, so the slow suite's results need extra vigilance. Where the mechanism is off by default, as a short mode or a size filter is, the mark deselects nothing until the routine run passes the filter. The condition is run time, since the mechanisms target long-running, time-consuming tests; a test that touches a dependency yet runs as fast as the routine suite is outside the rule, and a test that only starts a process or reaches a database or local service counts as such a test unless the file or the project documents it as slow. The rule claims only that a long test can be selected out: in the IDE study, fast tests did not correlate with more frequent test execution. Which pipeline runs each suite, and how often, is outside this rule.

## Validator
Grep the hunk for a test that starts a container, a browser or another process, or connects to a database URL or a localhost port. Open the file and the project's test configuration (registered markers or tags, size attributes, short-mode skips, ignore attributes, separate suite directories or targets) and note which selection the project already uses. Trace whether the added test carries that mark or sits in the suite the routine run excludes; where the project has no mechanism yet, any one the runner documents answers. Count as long-running a test that starts a container or a browser, unless the file or the project documents it as fast; count a test that only starts a process or makes a round trip to a database or network service as long-running only where the file or the project documents it, or tests like it, as slow, by a slow or size mark on its neighbours, a raised timeout, or a duration note. Validator question: **Does the hunk add a test that starts a container or a browser and is not documented as fast, or that the file or the project documents as slow, and that carries no selection mark the project's runner filters on and sits outside any suite the routine run already excludes?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: TST-28`, severity minor, `file`, `symbol`, `code` = the test's signature line and the line that starts the container, process or browser or opens the connection, `fix` = the test carrying the project's selection mark (a marker or tag, a size attribute, a short-mode skip, an ignore attribute) or moved into the suite the routine run excludes, in the file's language, `rationale` = names the long-running dependency the test starts and the runner's deselection the mark enables).

## Source
- Go command documentation, `go test` testing flags, `-short` (golang/go `src/cmd/go/alldocs.go`) (fetched): "Tell long-running tests to shorten their run time. It is off by default but set during all.bash so that installing the Go tree can run a sanity check but not spend time running exhaustive tests."
- Go package `testing`, §Skipping (golang/go `src/testing/testing.go`) (fetched): `func TestTimeConsuming(t *testing.T) { if testing.Short() { t.Skip("skipping test in short mode.") } ... }`
- Rust project documentation, rust-lang/book `src/ch11-02-running-tests.md`, §Ignoring Tests Unless Specifically Requested (fetched): "Rather than listing as arguments all tests you do want to run, you can instead annotate the time-consuming tests using the `ignore` attribute to exclude them"; "By controlling which tests run, you can make sure your `cargo test` results will be returned quickly. When you're at a point where it makes sense to check the results of the `ignored` tests and you have time to wait for the results, you can run `cargo test -- --ignored` instead. If you want to run all tests whether they're ignored or not, you can run `cargo test -- --include-ignored`."
- pytest documentation, `doc/en/how-to/mark.rst`, §Registering marks (fetched): `slow: marks tests as slow (deselect with '-m "not slow"')`
- JUnit User Guide, §Tagging and Filtering (fetched): "Test classes and methods can be tagged via the `@Tag` annotation. Those tags can later be used to filter test discovery and execution."
- Bazel user manual, `--test_size_filters` (bazelbuild/bazel `docs/docs/user-manual.mdx`) (fetched): "Bazel will test [...] only test targets with the given size. [...] optionally preceded with '-' sign used to denote excluded test sizes"; "By default, test size filtering is not applied."
- pytest documentation, `doc/en/explanation/flaky.rst`, §Split up test suites (fetched): "It can be common to split a single test suite into two, such as unit vs integration, and only use the unit test suite as a CI gate. This also helps keep build times manageable as high level tests tend to be slower. However, it means it does become possible for code that breaks the build to be merged, so extra vigilance is needed for monitoring the integration test results."
- doi:10.1145/2786805.2786843 (relayed): "Tests run in the IDE take a very short amount of time. Developers frequently select a specific set of tests to run in the IDE. In most cases, developers execute one test."; "Fast tests don't correlate with more frequent test execution". Caveat: an observational study of IDE sessions; it bounds the claim and does not measure the effect of selection marks.

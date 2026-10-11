---
title: A hand-written fake is checked by a contract test suite that runs the same public-API tests against the fake and against the real implementation
rule_id: TST-05
domain: tests
step: [test]
applies_to: [tests]
triggers: ['(?i)\b(class|struct|type|record)\s+(fake|inmemory|in_memory|stub)\w*', '\bimpl\b.*\bfor\s+(Fake|InMemory|Stub)\w*', '(?i)\bnew\s+(Fake|InMemory)\w*\(', '\b(class|struct|type|record)\s+\w+(Fake|InMemory|Stub)\w*']
scope: callers
check_kind: semantic
severity_default: minor
---

# A hand-written fake is checked by a contract test suite that runs the same public-API tests against the fake and against the real implementation

## Thesis
A hand-written fake (a working implementation of an interface that keeps state or computes results and stands in for the real implementation in tests) is covered by a suite of tests written against the shared public interface and run against both the fake and the real implementation, so that a divergence between them in an observable result, error or state change that the suite asserts fails a test. A fake imported from outside the repository, and a stub or mock configured inside a single test, are outside the rule.

## Rationale
A fake is a second implementation of an interface, and the tests that use it check the code under test, not the fake's fidelity to the real implementation. When the real implementation changes (a new error on a duplicate key, a different ordering), nothing in those tests compares the two. The fake keeps its old behaviour, and every test that uses it keeps passing while a production path that depends on the changed behaviour fails. Mocking has the same flaw: once the real code is refactored, tests that still use the old interface through mocks keep passing, so a suite can be green while the code is broken. In a study that manually analysed more than 2,000 test dependencies in three open-source systems and one industrial system, and surveyed more than 100 professionals, developers named keeping a mock's behaviour compatible with the behaviour of the original class as one of the key challenges of mocking; a fake reimplements more of that behaviour, so it has more to keep compatible. A contract suite restores one oracle for both implementations: it is written once against the interface and parameterised over the implementation, so a divergence in a behaviour the suite asserts shows up as a failing test in the fake's own suite, not as a silent pass in the tests that use the fake. A standard library ships this pairing: an in-memory implementation for tests together with a conformance checker that its maintainers run against both the in-memory and the production implementation.

## Example
```python
bad:  class FakeStore(Store):
          def put(self, key, value): self.rows[key] = value
      def test_checkout(): assert checkout(FakeStore(), cart) == "paid"
good: class FakeStore(Store): ...
      @pytest.mark.parametrize("make", [FakeStore, SqlStore])
      def test_put_then_get(make):
          store = make()
          store.put("k", 1)
          assert store.get("k") == 1
```

## Limits
A fake imported from outside the repository, whether the owner of the real implementation ships it or a third party does, is outside the rule: its contract suite belongs to the project that maintains it. A stub or mock configured inside a single test, and a hand-written double whose every answer is a fixed value set by the test that uses it, are outside too: each test sets their answers, so there is no one implementation for a shared suite to run. A fake that the repository's tests run through a conformance checker shipped by the owner of the interface meets the rule when the same checker also runs on the real implementation the fake stands in for: in the owner's own tests when the owner ships that implementation, in this repository's tests otherwise. The suite compares the interface's observable results, errors and state changes; it need not match latency, storage medium or resource use. The run against the real implementation may sit in a slower or gated suite (a command-line flag, an environment variable) and still counts. A documented project tolerance that names the fake and the reason its real implementation cannot run in any test environment rejects the finding. A fake whose interface has no real implementation yet, in the repository or in its dependencies, is outside the rule until one exists.

## Validator
Grep the added lines for a type declaration or implementation block named as a fake, in-memory or stub implementation, and for a construction of one. Open the declaration: confirm it is a hand-written type in this repository that tests use in place of a real implementation of the same interface or base type (it is declared in test code or a test-support module, or only tests construct it), and that it keeps state or computes results rather than returning values each test sets. Skip an in-memory type that production code selects as one of its own implementations. Skip a fake whose interface has no real implementation yet. Skip a fake imported from outside the repository. At scope callers, search the test tree for a suite that runs the same public-interface assertions against more than one implementation: a shared test routine that takes the implementation or a factory, a test parameterised over implementations, or an abstract test base with one concrete subclass per implementation. Check that both the fake and the real implementation are among its targets. A conformance checker shipped by the owner of the interface counts with the fake as its only target here when the owner also ships the real implementation the fake stands in for, because the owner runs the checker against it; when the real implementation comes from anywhere else, check that this repository's tests run the checker on it too. Validator question: **Does the diff add or change a hand-written fake with no test suite that runs the same public-interface tests against both the fake and the real implementation it stands in for?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: TST-05`, severity minor, `file`, `symbol`, `code` = the added declaration line of the fake, or its first added line when the declaration line is unchanged, `fix` = a shared or parameterised test, in the file's language, that runs the interface's assertions against both the fake and the real implementation, or a call of the interface owner's conformance checker on the fake, and on the real implementation unless the owner ships it, where such a checker exists, `rationale` = names the fake, the real implementation it stands in for, and the interface behaviour that no test compares between them).

## Source
- Go standard library, package `testing/fstest` (pkg.go.dev/testing/fstest), `func TestFS` and `type MapFS`: "TestFS tests a file system implementation." / "MapFS is a simple in-memory file system for use in tests" / "Typical usage inside a test is:" `if err := fstest.TestFS(myFS, "file/that/should/be/present"); err != nil {` (fetched)
- golang/go `src/testing/fstest/mapfs_test.go` (`TestMapFS`) and `src/os/os_test.go` (`testDirFS`), one checker run on the in-memory and the operating-system file system: `if err := TestFS(m, "hello", "fortune", "fortune/k", "fortune/k/ken.txt"); err != nil {` / `if err := fstest.TestFS(fsys, "a", "b", "dir/x"); err != nil {` (fetched)
- googleapis/google-cloud-go `spanner/spannertest/integration_test.go`, file comment and `testDBFlag`: "This file holds tests for the in-memory fake for comparing it against a real Cloud Spanner." / "Fully-qualified database name to test against; empty means use an in-memory fake." (fetched)
- getmoto/moto `tests/__init__.py`, `aws_verified`, applied through `s3_aws_verified` in `tests/test_s3/test_s3.py`: "Function that is verified to work against AWS. Can be run against AWS at any time by setting: MOTO_TEST_ALLOW_AWS_REQUEST=true" / "If this environment variable is not set, the function runs in a `mock_aws` context." (fetched)
- DOI 10.1109/MSR.2017.61, abstract: "developers report that maintaining the behavior of the mock compatible with the behavior of original class is hard" (fetched)
- Python documentation, `unittest.mock`, section "Autospeccing": "any tests for code that is still using the *old api* but uses mocks instead of the real objects will still pass. This means your tests can all pass even though your code is broken." (fetched)
- Caveat: the study and the documentation describe framework-generated mocks; the contract-suite practice for fakes rests on the conformance checker and the fake test suites above.

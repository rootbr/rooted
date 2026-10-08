---
title: A test that changes a store outliving it removes or resets that change, by managed cleanup, rollback or a reset before each test, whenever another test or a later run can observe it
rule_id: TST-31
domain: tests
step: [test, review]
applies_to: [tests]
triggers: ['(?i:\binsert\s+into\b|\b(?:create|drop)\s+(?:table|schema|database|index)\b|\btruncate\s+\w|\bdelete\s+from\b|[.](?:create_?(?:queue|topic|bucket|stream|table)|put_?object|send_?message|publish)\()|[.](?:save|saveAll|persist|insert|insertOne|insertMany|insert_one|insert_many|bulk_create|create_all|Create)\(']
scope: callers
check_kind: semantic
severity_default: major
---

# A test that changes a store outliving it removes or resets that change, by managed cleanup, rollback or a reset before each test, whenever another test or a later run can observe it

## Thesis
A test that changes a store outside its own process that outlives the test, such as rows in a database, the state of a server or files in a shared directory, removes or resets that change whenever another test or a later run can observe it. It does so through a cleanup the test framework manages, a transaction rolled back at the end of the test, or a reset that runs before each test.

## Rationale
State one test leaves behind can leak into the next test and cause it to fail, and debugging is harder because the problem comes from another test. A later run is an observer too: of 1,618 entries in one public flaky-test dataset, 160 are tests that pass in the first run but fail in the second. Cleaning up between tests can be easy to forget, and some state is impossible to clean up. An after-test hook is not guaranteed to run: a run refreshed in the middle of a test leaves partial state in the database and never calls it. Each mechanism the rule names has a defined point at which it runs. A registered cleanup is called when the test and all its subtests complete; a fixture defines the specific steps for each piece of setup to clean up after itself; a transaction rolled back at the end of the test restores the database to its initial state; code in a before-each hook always runs prior to the test, even after a run was refreshed in the middle of an earlier one.

## Example
```rust
bad:  #[test] fn stores_order() {
          let db = connect();
          db.insert("orders", "o-1");
          assert!(db.contains("orders", "o-1")); }
good: #[test] fn stores_order() {
          let db = connect();
          let tx = db.begin(); // rolled back when dropped
          tx.insert("orders", "o-1");
          assert!(tx.contains("orders", "o-1")); }
```

## Limits
When cleanup runs is the disputed part. A fixture removes the change after the test so that it does not interfere with other tests, a registered cleanup runs when the test and its subtests complete, and a transactional test case rolls its transaction back at the end of the test; a browser end-to-end test resets before each test or starts each test from a fresh environment, because an after-test hook is not guaranteed to run and some state cannot be cleaned. When the change is observable, a reset before each test and a managed cleanup or rollback after it both satisfy the rule, except where a run can be refreshed in the middle of a test: such a run never calls the after-test hook, so there the reset runs before each test. Whether a test needs its own cleanup at all turns on two conditions, either of which requires it: the operations it runs affect another test downstream, or the change stays in the store after the run, test data that a fixture should not leave behind. When each test acts only on records that no other test and no later run reads, and the store is cleared after the whole run, per-test removal is not required. A test that calls commit and rollback and observes their effects resets the store by truncating its tables after the test or by a reset before each test. State the test framework already clears before each test needs no cleanup of its own. State held inside the test process and per-test temporary directories that the framework removes are outside this rule.

## Validator
Grep the hunk for a test that writes to a store outside the test process: an insert, save, persist, publish, send-message, put-object, create-queue or create-table call, or SQL that inserts, deletes, drops or truncates. Open the file and trace where that store lives, a database, broker, bucket or directory shared with other tests in the suite or kept between runs, and whether another test reads what this test changed, such as a fixed key, a table another test counts or a queue another test consumes. Search the repository for the suite-wide setup that runs before or after these tests, such as a shared fixture, a root-level before-each hook or a package test main, and for other tests that use the same table, key, queue or path. Then look for what removes or resets the change: a fixture teardown or registered cleanup, a guard released when the test ends, a transaction rolled back at the end of the test, truncation after the test, a reset hook that runs before each test in this file or in a suite-wide setup file, or a clear of the store after the whole run when no other test reads the change. Validator question: **Does a test leave a change that another test reads or that stays in the store for a later run, with no managed cleanup, rollback or before-each reset covering that change, or with only an after-test hook in a runner whose run can be refreshed in the middle of a test?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: TST-31`, severity major, `file`, `symbol`, `code` = the test's write to the shared store, quoted verbatim from the diff, `fix` = the same test with a framework-managed cleanup, a rolled-back transaction or a before-each reset covering that write, in the file's language, `rationale` = the store written, the test or later run that can read the leftover change, and the missing cleanup).

## Source
- pytest docs, How to use fixtures, §Teardown/Cleanup (pytest-dev/pytest, doc/en/how-to/fixtures.rst) (fetched): "we'll want to make sure they clean up after themselves so they don't mess with any other tests (and also so that we don't leave behind a mountain of test data to bloat the system)"; "Fixtures in pytest offer a very useful teardown system, which allows us to define the specific steps necessary for each fixture to clean up after itself."
- Go package testing, `Cleanup` doc comment (golang/go, src/testing/testing.go) (fetched): "Cleanup registers a function to be called when the test (or subtest) and all its subtests complete."
- Django docs, Testing tools, TransactionTestCase and TestCase (django/django, docs/topics/testing/tools.txt) (fetched): "it encloses the test code in a database transaction that is rolled back at the end of the test. This guarantees that the rollback at the end of the test restores the database to its initial state."; "A TransactionTestCase resets the database after the test runs by truncating all tables. A TransactionTestCase may call commit and rollback and observe the effects of these calls on the database."
- Cypress docs, Best Practices, §Using after Or afterEach Hooks (cypress-io/cypress-documentation, docs/app/core-concepts/best-practices.mdx) (fetched): "there is no guarantee that this code will run"; "if you refresh Cypress in the middle of the test - you will have built up partial state in the database"; "Code put in a before or beforeEach hook will always run prior to the test - even if you refreshed Cypress in the middle of an existing one!"; "If the state you are trying to clean lives on the server - by all means, clean that state."; "Cypress already automatically enforces test isolation by clearing state before each test."; "Make sure you are not trying to clean up state that is already cleaned up by Cypress automatically."; "The only times you ever need to clean up state, is if the operations that one test runs affects another test downstream."
- Playwright docs, Isolation, §Two Ways of Test Isolation (microsoft/playwright, docs/src/browser-contexts.md) (fetched): "start from scratch or cleanup in between"; "it can be easy to forget to clean up and some things are impossible to clean up"; "State from one test can leak into the next test which could cause your test to fail and make debugging harder as the problem comes from another test."
- International Dataset of Flaky Tests (TestingResearchIllinois/idoft at 4903dc9, readme.md category table and py-data.csv) (fetched): "NIO | Non-Idempotent-Outcome Tests [...] Tests that pass in the first run but fail in the second."; 160 of the 1,618 rows of py-data.csv carry NIO.
- Bazel Test Encyclopedia, Test interaction with the filesystem (bazelbuild/bazel, docs/reference/test-encyclopedia.mdx) (fetched): "the test itself must take care to be hermetic, to use unique paths to avoid colliding with other, simultaneously running tests and non-test processes, and to clean up the files it creates in `/tmp`."
- Caveat: the dataset covers Python projects and its category does not separate state in an external store from state inside the test process; it supports only that a later run observes what an earlier run left.

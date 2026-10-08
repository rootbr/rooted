---
title: A test that uses a database or other out-of-process store creates the records it changes, selects or counts and never relies on records another test or an earlier run left there
rule_id: TST-30
domain: tests
step: [test, review]
applies_to: [tests]
triggers: ['(?i)\blimit\s+1\b|\bfetchone\(\)|[.](findFirst|first|find_first|First)\(\s*\)', '(?i)\b(assert\w*|expect|assert_eq!|require[.]\w+)\W.*\bcount\w*\(', '(?i)[.](find(_?by_?id)?|get(_?by_?id)?|findById|FindByID|load)\(\s*\d+\s*[,)]', '(?i)\b(seed|seeds|fixtures?|testdata)\b[\w/.-]*[.](sql|json|ya?ml|csv)\b', '(?i)\bselect\b.+\bfrom\b(?!.*\bwhere\b)']
scope: file
check_kind: semantic
severity_default: major
---

# A test that uses a database or other out-of-process store creates the records it changes, selects or counts and never relies on records another test or an earlier run left there

## Thesis
A test that reads or writes a database or other store outside its process inserts the records it will change, select or count, and asserts only on those records, found by the keys it created, so that no other test affects its result and running the tests in any order produces the same result.

## Rationale
Tests that each query the database for a valid record before picking one to act on can pick the same record and are then likely to behave unexpectedly, and stale records left in the application can be picked up by another test. A count over a table that other tests also write counts shared test data: their inserts change its result, where test independence asks that no test affect any other test's result and that running the tests in any order produce the same results. Pollution of state shared across tests is the main reason for test dependencies; a study of 96 real-world dependent tests from 5 issue tracking systems shows that test dependence can be hard for programmers to identify and can mask program faults and lead to spurious bug reports. Order dependence caused 59% of the 7,571 flaky tests in one dataset of open-source packages, and 50.5% of 422 flaky tests in a second dataset were order-dependent.

## Example
```go
bad:  seedOnce(t, db, "testdata/orders.sql")
      var id int64
      db.QueryRow("SELECT id FROM orders LIMIT 1").Scan(&id)
      closeOrder(t, db, id)
      require.Equal(t, 1, countClosedOrders(t, db))
      require.Equal(t, "open", store.FindByID(7).Status)
good: id := insertOrder(t, db, Order{Status: "open"})
      t.Cleanup(func() { deleteOrder(t, db, id) })
      closeOrder(t, db, id)
      require.Equal(t, "closed", loadOrder(t, db, id).Status)
```

## Limits
Reference data that no test changes may be seeded once for the run and read by every test: a later test can fail when it assumes a shared location still holds its initial value after an earlier test modified it, and data no test modifies keeps that value. Records that a test's own setup writes into a store started for that test alone are records the test created, since such a store starts in a known state. In-process shared state, such as globals, static fields and singletons, and the order in which a runner executes tests are outside this rule; a test that reaches an out-of-process record it did not create is inside it whether the tests that share the store run in one process or in several.

## Validator
Grep the hunk for queries without a key filter, first-row or LIMIT 1 fetches, lookups by a literal id, assertions on counts, and seed or fixture files. Open the test file and, for each test that uses a database or other store outside its process, trace every record the test changes, selects or counts back to the insert that creates it in that test or its setup. Skip reads of reference rows that no test changes and stores started for that one test alone. Validator question: **Does a test that uses an out-of-process store change, select or count a record it did not create, or assert a total over a table that other tests also write?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: TST-30`, severity major, `file`, `symbol`, `code` = the query, lookup or count assertion that reaches a record the test did not create, `fix` = the test inserting its own record under a key it generates and asserting on that record, in the file's language, `rationale` = where the record comes from outside the test and which other test or run can change it).

## Source
- SeleniumHQ/seleniumhq.github.io trunk, website_and_docs/content/documentation/test_practices/encouraged/avoid_sharing_state.en.md (fetched): "Do not share test data. Imagine several tests that each query the database for valid orders before picking one to perform an action on. Should two tests pick up the same order you are likely to get unexpected behavior." · "Clean up stale data in the application that might be picked up by another test"
- doi:10.1145/2771783.2771793, ISSTA 2015, abstract (fetched): "Prior research has shown that the main reason for test dependencies is the ``pollution'' of state shared across tests." · "a subsequent test could fail if it assumes the shared location to have the initial value before the state was modified."
- doi:10.1145/2610384.2610404, ISSTA 2014, abstract (fetched): "no test should affect any other test’s result, and running the tests in any order should produce the same test results" · "We studied 96 real-world dependent tests from 5 issue tracking systems. Our study shows that test dependence can be hard for programmers to identify. It also shows that test dependence can cause non-trivial consequences, such as masking program faults and leading to spurious bug reports."
- doi:10.1109/ICST49551.2021.00026, arXiv:2101.09077, ICST 2021, abstract (fetched): "Order dependency is a much more dominant problem in Python, causing 59 % of the 7 571 flaky tests in our dataset."
- doi:10.1109/ICST.2019.00038, ICST 2019, abstract (fetched): "Using iDFlakies, we build a dataset of 422 flaky tests, with 50.5% order-dependent and 49.5% not." (Maven-based Java projects)
- testcontainers/testcontainers-java, docs/index.md (fetched): "use a containerized instance of a MySQL, PostgreSQL or Oracle database to test your data access layer code [...] safe in the knowledge that your tests will always start with a known DB state."
- Caveat: the research counts order dependence through any state shared across tests, not database records alone; the database case is the one the first source documents.

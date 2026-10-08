---
title: A test isolated by a rolled-back transaction flushes pending ORM writes before asserting and checks commit-time behaviour in a test that commits or emulates the commit
rule_id: TST-33
domain: tests
step: [test, review]
applies_to: [tests]
triggers: ['@(Transactional|DataJpaTest|DataJdbcTest|Rollback)\b|(?i:\b(on_?commit|captureOnCommitCallbacks|after_?commit|TransactionSynchronization|TransactionalEventListener|(select_|with_)?for_update|pessimistic_write)\b)|\bFOR UPDATE\b|\b(entityManager|em|session|sessionFactory|getCurrentSession\(\)|\w*[Rr]epo(sitory)?)[.](persist|merge|save|saveAll|saveOrUpdate|add|add_all|delete|remove)\(|(?i:[.](begin_nested|(begin_)?test_transaction|rollback|savepoint)\()|\bTransactionTestCase\b|\bdjango[.]test\b']
scope: file
check_kind: semantic
severity_default: major
---

# A test isolated by a rolled-back transaction flushes pending ORM writes before asserting and checks commit-time behaviour in a test that commits or emulates the commit

## Thesis
A test that isolates database state inside a transaction rolled back at its end flushes the ORM's in-memory unit of work within each test method that runs code manipulating it, after that code and before the test's assertions. Commit callbacks are verified in a test that commits, or in a test that captures them and asserts on them or invokes them to emulate the commit, and a check that a block of code executes within a transaction, as a row-locking select requires, is verified in a test that commits.

## Rationale
A test transaction that is rolled back at the end is never committed, so callbacks registered to run on commit never run inside it. A faulty write held in an in-memory unit of work throws once the unit of work is finally flushed, as production code does: failing to flush it within the test can produce a false positive, where the test passes but the same code throws an exception in a live, production environment. Failing to flush or clear the unit of work can also leave certain entity lifecycle callbacks uninvoked. Some database behaviours cannot be tested inside the rolled-back transaction; whether a block of code executes within a transaction is one of them. A test that commits can call commit and rollback and observe their effects on the database, and a test that captures commit callbacks can assert on them or call them to invoke their side effects, emulating a commit. Flushing removes the false positive in which the test passes while the same code throws in production; committing, or emulating the commit, runs the callbacks the rolled-back transaction never runs.

## Example
```python
bad:  def test_archive(session):  # rolled back after each test
          session.add(invoice := Invoice(status="open"))
          archive(invoice)
          assert invoice.status == "archived"
good: def test_archive(session):  # rolled back after each test
          session.add(invoice := Invoice(status="open"))
          archive(invoice)
          session.flush()
          assert invoice.status == "archived"
```

## Limits
The rule applies only where a test runs inside a transaction that is rolled back at its end; a test that commits and resets the database another way, such as truncating all tables, already observes commit and rollback. The flush half reaches the ORM frameworks that maintain an in-memory unit of work, the scope the evidence states; code that writes without one falls outside it. The rolled-back transaction is the faster way to reset the database to a known state, so only the behaviour that cannot be tested inside it moves to a committing test.

## Validator
Grep the hunk for the triggers: a test-transaction annotation or rollback fixture, a write through a unit of work (persist, merge, save, add, delete, remove), a commit-callback registration or capture, a row-locking select. Open the test file and establish whether its tests run inside a transaction rolled back at the end: a framework default, a class-level annotation, or a fixture that begins a transaction, nested transaction or savepoint and rolls it back. For each test in the hunk, trace the code under test. When it writes through an ORM unit of work, look for a flush, or a query the ORM documents as flushing first, between the last write and the assertion. When it asserts on what commit callbacks do, look for a commit in that test or for a capture whose callbacks the test invokes; leave a test that captures the callbacks and asserts only on the captured list unflagged. When it checks that the code under test executes within a transaction, as a row-locking select requires, establish whether that check runs inside the rolled-back transaction, which satisfies it whatever the code does. Validator question: **Does a test running inside a rolled-back transaction assert on writes still pending in an ORM unit of work without flushing it, assert on the effects of commit callbacks without committing or invoking the captured callbacks, or check that a block of code executes within a transaction, which the enclosing rolled-back transaction always satisfies?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: TST-33`, severity major, `file`, `symbol`, `code` = the write, the commit-callback call or the transaction-requiring call and the assertion that follows it, quoted verbatim from the diff, `fix` = the flush placed before the assertion, the commit-callback test moved to a committing case or wrapped in a commit-callback capture whose callbacks it asserts on or invokes, or the transaction check moved to a test that runs outside the rolled-back transaction and commits, in the file's language, `rationale` = the pending write or commit-time behaviour the rolled-back transaction hides and the production failure the passing test can mask).

## Source
- Spring Framework reference, TestContext framework, Transaction Management (spring-projects/spring-framework, framework-docs/modules/ROOT/pages/testing/testcontext-framework/tx.adoc), note "Avoid false positives when testing ORM code": "Failing to flush the underlying unit of work can produce false positives: Your test passes, but the same code throws an exception in a live, production environment. Note that this applies to any ORM framework that maintains an in-memory unit of work."; its example: "an exception will be thrown once the Hibernate Session is finally flushed (i.e., in production code)"; entity lifecycle callbacks note: "Failing to _flush_ or _clear_ the underlying unit of work can result in certain lifecycle callbacks not being invoked." (fetched)
- Django documentation, Testing tools (django/django, docs/topics/testing/tools.txt), TransactionTestCase section: "Django's TestCase class is a more commonly used subclass of TransactionTestCase that makes use of database transaction facilities to speed up the process of resetting the database to a known state at the end of each test."; "some database behaviors cannot be tested within a Django TestCase class. For instance, you cannot test that a block of code is executing within a transaction, as is required when using select_for_update. In those cases, you should use TransactionTestCase."; "A TransactionTestCase may call commit and rollback and observe the effects of these calls on the database."; TestCase.captureOnCommitCallbacks: "From this list you can make assertions on the callbacks or call them to invoke their side effects, emulating a commit." (fetched)
- Django documentation, Database transactions (django/django, docs/topics/db/transactions.txt): "no transaction is ever actually committed, thus your on_commit() callbacks will never be run."; "Another way to overcome the limitation is to use TransactionTestCase instead of TestCase. This will mean your transactions are committed, and the callbacks will run." (fetched)
- Caveat: the sources are two frameworks' documentation of their own rolled-back test transactions; the Spring note states its scope as any ORM framework with an in-memory unit of work.

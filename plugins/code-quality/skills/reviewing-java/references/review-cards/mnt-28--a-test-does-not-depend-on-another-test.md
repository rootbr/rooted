---
title: A test does not depend on another test through shared mutable static state or a required execution order
rule_id: MNT-28
domain: maintainability
triggers: ['static (?!final)[\w<>\[\], ?]+\s+\w+\s*(=|;)', 'static \w[\w<>\[\], ?]*\s+\w+\s*=\s*new ', '@TestMethodOrder|@Order\(', '@TestInstance\(.*PER_CLASS', '@BeforeAll|@AfterAll']
scope: file
check_kind: semantic
severity_default: minor
---

# A test does not depend on another test through shared mutable static state or a required execution order

## Thesis
Each test method sets up what it needs and can run alone, in any order, and repeatedly: state that one test writes is not a `static` field another test reads, a `PER_CLASS` instance or a `@BeforeAll` fixture is not mutated by the tests that follow, and `@TestMethodOrder`/`@Order` are not used to make one test rely on what an earlier one left behind.

## Rationale
JUnit creates a new instance of the test class before each test method by default, so that test methods run in isolation without side effects from mutable instance state; a `static` field or a per-class instance puts the leak back, and the default method order is deterministic but intentionally non-obvious, so a test that happens to pass after its neighbour fails when run alone, when filtered, or when run in parallel. Ordering annotations turn the accident into a dependency: the later test now fails for the earlier test's reasons, and neither can be understood or fixed on its own.

## Example
```java
bad:  static List<Order> created = new ArrayList<>();
      @Test @Order(1) void creates() { created.add(service.create(req)); }
      @Test @Order(2) void findsCreated() { assertThat(service.find(created.get(0).id())).isPresent(); }
good: @Test void findsCreated() {
          Order o = service.create(req);
          assertThat(service.find(o.id())).isPresent(); }
```

## Limits
A `static final` immutable constant, a shared read-only fixture built in `@BeforeAll` and never mutated, and an expensive resource (a container, an embedded server) shared read-only across a class are fine. `@Order` on `@Nested` classes, and lifecycle-driven integration suites the project context documents as sequential, are out of scope. Parameterized tests over a static source method are not shared mutable state.

## Validator
On the triggered hunk find each mutable `static` field in a test class, each `@BeforeAll` fixture, and each `@TestMethodOrder`/`@Order`. Open the file: check whether one test method writes what another reads, or whether an ordered test assumes an earlier test's effect. Validator question: **would this test fail if run alone, or in a different order, because another test's state or side effect is missing?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: MNT-28`, severity minor, `file`, `symbol`, `code` = the shared field or the ordering annotation and the dependent test quoted verbatim from the diff, `fix` = the self-contained test, `rationale` naming the run — alone, filtered, parallel — that fails).

## Source
JUnit Jupiter `org.junit.jupiter.api.TestInstance` Javadoc — the lifecycle "will implicitly default to PER_METHOD", under which "a new test instance will be created for each test method"; `PER_CLASS` enables "shared test instance state between test methods". `org.junit.jupiter.api.TestMethodOrder` Javadoc — without it "test methods will be ordered using a default algorithm that is deterministic but intentionally nonobvious" (both fetched from `junit-team/junit-framework`, branch `main`). JUnit User Guide, "Test Instance Lifecycle" — "In order to allow individual test methods to be executed in isolation and to avoid unexpected side effects due to mutable test instance state, JUnit creates a new instance of each test class before executing each test method" (`junit-team/junit-framework`, tag `r5.11.4`, `documentation/src/docs/asciidoc/user-guide/writing-tests.adoc`, line 932).

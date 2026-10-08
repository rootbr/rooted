---
title: Code whose correctness depends on a real dependency's behaviour, such as a query, a schema mapping or a wire format, is run by at least one test against that dependency or a stand-in of the same product and not only against doubles
rule_id: TST-34
domain: tests
step: [design, test, review]
applies_to: [tests, service-boundary]
triggers: ['(?i:[\x22\x27\x60]\s*(select|insert\s+into|update|delete\s+from)\b)|@(Query|Repository|Entity|Table|Mapper)\b|\b(create_engine|sql[.]Open|sqlx::query\w*)\(|\b(json[.](Marshal|Unmarshal|dumps|loads)|JSON[.](parse|stringify)|serde_json::\w+|proto[.](Marshal|Unmarshal))\b|@JsonProperty\b', '(?i)\b(mock|patch|stub|fake|when)\w*\(.*\b\w*(Repository|Repo|Dao|Client|Connection|Cursor|Session|Producer|Consumer|Publisher)\b']
scope: callers
check_kind: semantic
severity_default: major
---

# Code whose correctness depends on a real dependency's behaviour, such as a query, a schema mapping or a wire format, is run by at least one test against that dependency or a stand-in of the same product and not only against doubles

## Thesis
Code whose correctness depends on how a real dependency behaves, such as a database query or its schema mapping, a message or wire format exchanged with another component, or a client for a store or a queue, is run by at least one test against that dependency or against a throwaway instance of the same product. That test comes in addition to the tests of the code on its own, which may replace the dependency with a double.

## Rationale
Units of code that work correctly on their own could have problems when integrated, so test coverage of the integrated code is important as well. Integration testing verifies the interactions among components, and a double takes the place of one side of that interaction. A throwaway instance of the same database product, started in a container, tests data-access code for complete compatibility without complex setup on developers' machines, and the tests start from a known database state. The same mechanism runs an application in a short-lived test mode against its databases, message queues or web servers.

## Example
```typescript
bad:  findOpen = async () => (await this.db.query("SELECT * FROM orders WHERE status = 'open'")).rows;
      jest.mock("./dbClient"); // the only test of OrderRepository.findOpen
      const repo = new OrderRepository(dbClient);
      expect(await repo.findOpen()).toEqual([openOrder]);
good: const pg = await new PostgreSqlContainer("postgres:16").start();
      const repo = new OrderRepository(connect(pg.getConnectionUri()));
      await repo.save(openOrder);
      expect(await repo.findOpen()).toEqual([openOrder]);
```

## Limits
The small tests of the same code keep their doubles; the integrated test is coverage added beside them, not a replacement. One test that reaches the changed query, mapping or format through the real dependency or an instance of the same product meets the rule, and the remaining cases stay in the small tests. Code that has no interaction with the dependency, such as logic that only transforms values already read, is outside the rule. Which double stands in for the dependency in the small tests is outside the rule too. A message or wire format exchanged with another service also meets the rule when its consumer tests run against a contract double whose recorded interactions the provider's own tests verify against the real provider, as in consumer-driven contract testing.

## Validator
Grep the hunk for query strings, mapping annotations, driver or engine calls and serialization calls, and for doubles of repository, client, connection, session, producer or consumer types in test files. For each changed query, mapping, client or format, open its callers and follow them into the tests that reach it. Trace whether any of those tests runs it against the real dependency or an instance of the same product (a container, a local instance of the same engine, a test deployment of the service), as opposed to a mock, a stub, a fake or an engine of a different product; a contract double whose interactions the provider's own tests verify against the real provider counts as the real dependency. Validator question: **Does the change add or alter code whose correctness depends on a real dependency's behaviour while every test that reaches it replaces that dependency with a double?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: TST-34`, severity major, `file`, `symbol`, `code` = the changed query, mapping, client call or serialization line quoted verbatim from the diff, `fix` = a test that runs that code against the real dependency or a throwaway instance of the same product, in the file's language, `rationale` = the integration point that only doubles exercise and the interaction they leave unverified).

## Source
- rust-lang/book, src/ch11-03-test-organization.md, §Integration Tests (fetched): "Units of code that work correctly on their own could have problems when integrated, so test coverage of the integrated code is important as well."
- SWEBOK V3.0, ch. 4 'Software Testing', §2.1.2 'Integration Testing' (fetched): "Integration testing is the process of verifying the interactions among software components."
- testcontainers/testcontainers-java, docs/index.md, §About Testcontainers for Java (fetched): "lightweight, throwaway instances of common databases"; "use a containerized instance of a MySQL, PostgreSQL or Oracle database to test your data access layer code for complete compatibility, but without requiring complex setup on developers' machines and safe in the knowledge that your tests will always start with a known DB state"; "for running your application in a short-lived test mode with dependencies, such as databases, message queues or web servers."
- pact-foundation/pact-js, README.md, §Writing a Consumer test and §Verifying a Provider (fetched): "By unit testing our API client with Pact, it will produce a `contract` that we can share to our `Provider` to confirm these assumptions and prevent breaking changes."; "A provider test takes one or more pact files (contracts) as input, and Pact verifies that your provider adheres to the contract."
- Caveat: none of these sources measures how often double-only tests miss integration defects; the container statement names databases, message queues and web servers, and the rule reaches other dependencies through the two general statements.

---
title: A result set whose size a client or an unbounded table controls is capped by the server: a maximum page size, a query limit, or a cursor
rule_id: REL-24
domain: reliability
triggers: ['@RequestParam\(.*size', 'Pageable', 'PageRequest[.]of\(', 'findAll\(\)', 'getResultList\(\)', 'setMaxResults\(', 'Integer size', 'int size', 'int limit', 'Integer limit', 'executeQuery\(']
scope: file
check_kind: semantic
severity_default: major
---

# A result set whose size a client or an unbounded table controls is capped by the server: a maximum page size, a query limit, or a cursor

## Thesis
A handler that accepts a page size or limit clamps it to a server-side maximum before querying; a query over a table that grows without bound carries `setMaxResults`, a `limit` clause, a `Pageable` or a keyset cursor; and a `findAll()` or unbounded `getResultList()` runs only over a table whose size is bounded by design.

## Rationale
A client that asks for `size=1000000`, or a table that has grown since the code was written, makes the server materialize every row into heap before responding: the request holds a connection for the whole read, the entity list is allocated in one go, and the process fails with `OutOfMemoryError` or stalls in garbage collection, taking every other request down with it. The bound belongs on the server because the client's number is untrusted input, and it belongs in the query because the database can stop after N rows where the application cannot. Spring Data's pageable resolver caps requests at 2000 for exactly this reason — "to prevent potential attacks trying to issue an OutOfMemoryError" — and a query language's `limit` exists "to place a hard upper limit on the number of results that may be returned by a query".

## Example
```java
bad:  @GetMapping("/items") List<Item> list(@RequestParam int page, @RequestParam int size) {
          return repo.findAll(PageRequest.of(page, size)).getContent(); }
      List<Event> all = em.createQuery("from Event", Event.class).getResultList();
good: @GetMapping("/items") List<Item> list(@RequestParam int page, @RequestParam int size) {
          return repo.findAll(PageRequest.of(page, Math.min(size, MAX_PAGE))).getContent(); }
      List<Event> batch = em.createQuery("from Event order by id", Event.class).setMaxResults(500).getResultList();
```

## Limits
A `Pageable` resolved by Spring Data's web support with its default or configured `maxPageSize` is already clamped; a project context naming that configuration rejects the finding for handler parameters. A `findAll()` over a reference table with a bounded, documented size (currencies, countries, configuration rows) is correct with a comment. A streaming or scrolling read that processes rows as they arrive and never holds the full result is out of scope.

## Validator
On the triggered hunk find each client-supplied size or limit and each query with no `setMaxResults`, `limit`, `Pageable` or cursor. Open the file to check for a clamp on the parameter, a resolver with a maximum, or a comment bounding the table. Validator question: **can a client value or a growing table make this request load an unbounded number of rows into memory?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: REL-24`, severity major, `file`, `symbol`, `code` = the parameter or query quoted verbatim from the diff, `fix` = `Math.min(size, MAX)` or `setMaxResults`/`limit`/a keyset cursor, `rationale` naming the heap the unbounded result fills).

## Source
Spring Data Commons `org.springframework.data.web.PageableHandlerMethodArgumentResolverSupport#setMaxPageSize` Javadoc — "Configures the maximum page size to be accepted. This allows to put an upper boundary of the page size to prevent potential attacks trying to issue an OutOfMemoryError. Defaults to DEFAULT_MAX_PAGE_SIZE" (2000). Hibernate ORM user guide, "Hibernate Query Language", "Limits and offsets" — "It's often useful to place a hard upper limit on the number of results that may be returned by a query. The limit and offset clauses are an alternative to the use of setMaxResults() and setFirstResult()". `java.sql.Statement#setMaxRows(int)` Javadoc, Java SE 21 — the driver drops rows beyond the limit. The query-limit half of the Thesis is the card's extension of the page-size rule to the query the page size feeds: the Hibernate sentence is advice and `setMaxRows` defines an API; only the page-size cap carries a stated motive.

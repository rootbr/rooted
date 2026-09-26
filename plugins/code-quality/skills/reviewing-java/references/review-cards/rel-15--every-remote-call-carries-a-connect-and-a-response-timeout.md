---
title: Every remote call carries an explicit connect timeout and a response timeout, so no thread can wait forever
rule_id: REL-15
domain: reliability
triggers: ['HttpClient[.]newBuilder\(\)', 'HttpClient[.]newHttpClient\(\)', 'HttpRequest[.]newBuilder\(', 'RestTemplate\(', 'RestClient[.]create\(', 'WebClient[.]create\(', 'RestClient[.]builder\(', 'HttpClients[.]create', 'new OkHttpClient\(', 'newCall\(', 'ManagedChannelBuilder', 'setQueryTimeout\(', 'createQuery\(']
scope: file
check_kind: mechanical
severity_default: major
---

# Every remote call carries an explicit connect timeout and a response timeout, so no thread can wait forever

## Thesis
A client that talks to another process — an HTTP, gRPC, JDBC or message-broker client — is built with a bounded connect timeout and a bounded read/response timeout (or per-request `timeout`), and a query that can run long carries a query timeout; no call is issued through a client whose wait is unbounded by default.

## Rationale
A remote peer that accepts the connection and never answers — a stalled process, a dropped packet after the handshake, a database waiting on a lock — holds the caller's thread for as long as the caller is willing to wait. With `java.net.http.HttpRequest`, "the effect of not setting a timeout is the same as setting an infinite Duration, i.e. block forever"; a JDBC statement has "no limit on the amount of time allowed for a running statement to complete" by default. Under load, each stuck call pins one pool thread and one connection, the pool drains, and every later request queues behind calls that will never return: one slow dependency becomes an outage of the caller. A timeout turns the stall into a failure at the site of the call, after a bound the code chose, with the thread and the connection released.

## Example
```java
bad:  HttpClient client = HttpClient.newHttpClient();
      HttpRequest req = HttpRequest.newBuilder(uri).GET().build();
good: HttpClient client = HttpClient.newBuilder().connectTimeout(Duration.ofSeconds(2)).build();
      HttpRequest req = HttpRequest.newBuilder(uri).timeout(Duration.ofSeconds(10)).GET().build();
```

## Limits
A client injected from configuration whose timeouts are set centrally — a `RestClient.Builder` or `HttpClientSettings` the project context names, a `spring.http.client.*` property block — satisfies the rule; open the builder's definition before flagging a use. A streaming or long-polling request whose unbounded read is the design is correct with a comment saying so and an idle or overall deadline elsewhere. A JDBC query timeout set globally (`jakarta.persistence.query.timeout` in configuration, a transaction `timeout`) covers queries that set none.

## Validator
On the triggered hunk find each client construction and each request. Open the file (and the builder's definition when the client is injected) to check for a connect timeout and a read/response/request timeout, and for a query timeout or transaction timeout on database calls that can run long. Validator question: **can this call wait without bound for a peer that never answers?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: REL-15`, severity major, `file`, `symbol`, `code` = the client construction or request quoted verbatim from the diff, `fix` = the builder with `connectTimeout` and a request `timeout` (or the client's read-timeout setter, or `setQueryTimeout`), `rationale` naming the unbounded wait and the pool it drains).

## Source
`java.net.http.HttpRequest.Builder#timeout(Duration)` Javadoc, Java SE 21 — "The effect of not setting a timeout is the same as setting an infinite Duration, i.e. block forever"; `java.net.http.HttpClient.Builder#connectTimeout(Duration)` — an `HttpConnectTimeoutException` when the connection cannot be established within the duration. `java.sql.Statement#setQueryTimeout(int)` — "By default there is no limit on the amount of time allowed for a running statement to complete". arXiv:2512.16959 §VI.C — "Timeouts prevent indefinite waiting on unresponsive dependencies".

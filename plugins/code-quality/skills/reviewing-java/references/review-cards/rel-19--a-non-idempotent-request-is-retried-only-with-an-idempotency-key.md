---
title: A POST or PATCH request is retried only when it carries an Idempotency-Key the server dedupes on
rule_id: REL-19
domain: reliability
triggers: ['[.]POST\(', '[.]PATCH\(', 'HttpMethod[.]POST', 'HttpMethod[.]PATCH', 'postForObject\(', 'postForEntity\(', '[.]post\(\)', '[.]patch\(\)', '@Retryable', 'Retry[.]of', 'RetryConfig', 'retr(y|ies)']
scope: file
check_kind: semantic
severity_default: major
---

# A POST or PATCH request is retried only when it carries an Idempotency-Key the server dedupes on

## Thesis
A retry policy — a loop, `@Retryable`, a Resilience4j `Retry`, a client-level retry setting — applies to a `POST` or `PATCH` request only when the request carries an `Idempotency-Key` header (or an equivalent client-generated key the server documents) that makes a repeat safe; without such a key the policy retries only `GET`, `HEAD`, `OPTIONS`, `PUT` and `DELETE`.

## Rationale
An idempotent method has the same intended effect on the server whether sent once or many times, which is why "the request can be repeated automatically if a communication failure occurs before the client is able to read the server's response". `POST` and `PATCH` are not idempotent: when the connection drops after the server has committed and before the response arrives, the client cannot tell whether the operation was applied, and a retry creates a second order, a second charge, a second message. The standard therefore says a client should not automatically retry a non-idempotent request "unless it has some means to know that the request semantics are actually idempotent ... or some means to detect that the original request was never applied". A unique per-operation `Idempotency-Key` is that means: the server stores the key with the first outcome and answers a repeat with the stored response.

## Example
```java
bad:  Retry.decorateSupplier(retry, () -> client.post().uri("/charges").body(req).retrieve().body(Charge.class));
good: String key = UUID.randomUUID().toString();     // one key per logical charge, reused on each attempt
      Retry.decorateSupplier(retry, () -> client.post().uri("/charges")
          .header("Idempotency-Key", key).body(req).retrieve().body(Charge.class));
```

## Limits
A `POST` whose handler is documented as idempotent for the resource (a pure query sent as POST, an upsert keyed by the body) may be retried with a comment naming that documentation. A retry restricted to failures that prove the request was never applied — a connect timeout before any byte was sent — is the "means to detect" the standard allows and is not flagged. The key must be generated once per logical operation and reused across attempts; a key regenerated per attempt is no key.

## Validator
On the triggered hunk find each retry policy and each request it wraps, or each `POST`/`PATCH` request in a method that a retry annotation or client retry setting covers. Open the file to read the request's headers and the retry's exception predicate. Validator question: **can this policy resend a `POST` or `PATCH` after the server may already have applied it, with no key that lets the server recognize the repeat?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: REL-19`, severity major, `file`, `symbol`, `code` = the retry policy and the request quoted verbatim from the diff, `fix` = an `Idempotency-Key` generated once per operation and sent on every attempt, or the retry predicate narrowed to failures before the request was sent, `rationale` naming the duplicate side effect).

## Source
RFC 9110 "HTTP Semantics" §9.2.2 "Idempotent Methods" — "Of the request methods defined by this specification, PUT, DELETE, and safe request methods are idempotent"; "A client SHOULD NOT automatically retry a request with a non-idempotent method unless it has some means to know that the request semantics are actually idempotent, regardless of the method, or some means to detect that the original request was never applied" (fetched from the httpwg source `draft-ietf-httpbis-semantics-latest.xml`). IETF `draft-ietf-httpapi-idempotency-key-header` (`ietf-wg-httpapi/idempotency`, `main`) — "Repeating the request multiple times can result in duplication or incorrect updates ... the client does not know if it can safely retry the request"; the key "MUST be unique and MUST NOT be reused with another request with a different request payload".

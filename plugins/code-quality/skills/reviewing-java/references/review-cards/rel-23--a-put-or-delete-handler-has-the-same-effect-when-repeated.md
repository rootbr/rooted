---
title: A handler mapped to PUT or DELETE has the same effect when the request is repeated
rule_id: REL-23
domain: reliability
triggers: ['@PutMapping', '@DeleteMapping', '@RequestMapping', 'RequestMethod[.]PUT', 'RequestMethod[.]DELETE', '@PUT\b', '@DELETE\b']
scope: file
check_kind: semantic
severity_default: major
---

# A handler mapped to PUT or DELETE has the same effect when the request is repeated

## Thesis
A `PUT` handler replaces the target identified by the URI, so that sending the same request twice leaves the same state; a `DELETE` handler removes the target, so that a repeat has no further effect. An operation that appends, increments, debits, sends or creates a new resource on each call is mapped to `POST`, or made a replacement keyed by the URI.

## Rationale
Idempotent methods are those for which "the intended effect on the server of multiple identical requests with that method is the same as the effect for a single such request", and "PUT, DELETE, and safe request methods are idempotent". They are "distinguished because the request can be repeated automatically if a communication failure occurs before the client is able to read the server's response": a client library, a proxy or a retrying gateway that loses the connection after a `PUT` or `DELETE` resends it without asking, so a `PUT` that appends an item or a `DELETE` that debits a fee on every call performs the side effect twice and the client never learns it. Mapping such an operation to `POST` tells intermediaries not to repeat it; keying a `PUT` by the URI makes the second write overwrite the first.

## Example
```java
bad:  @PutMapping("/cart/{id}/items") Cart add(@PathVariable long id, @RequestBody Item i) { return svc.append(id, i); }
      @DeleteMapping("/holds/{id}") void release(@PathVariable long id) { svc.chargeReleaseFee(id); svc.delete(id); }
good: @PostMapping("/cart/{id}/items") Cart add(@PathVariable long id, @RequestBody Item i) { return svc.append(id, i); }
      @PutMapping("/cart/{id}/items/{sku}") Cart set(@PathVariable long id, @PathVariable String sku, @RequestBody Item i) { ... }
      @DeleteMapping("/holds/{id}") void release(@PathVariable long id) { if (svc.deleteIfPresent(id)) svc.chargeReleaseFee(id); }
```

## Limits
The idempotent property "only applies to what has been requested by the user": a server that logs each request, retains a revision history, bumps a version counter or writes an audit entry on every repeat is still idempotent in the resource's state and is not flagged. A `DELETE` that returns 404 on the repeat is idempotent: the state is the same. A `PUT` used as an upsert keyed by the URI is correct. A handler behind an idempotency-key filter the project context names is out of scope.

## Validator
On the triggered hunk find each `PUT` or `DELETE` mapping, read the handler body and the name and signature of the service call it makes, and open the service class when it is in this file. Ask whether calling the handler twice with the same request leaves the same state or performs a second append, increment, debit or send. Validator question: **does repeating this request cause a second state change its method promises not to cause?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: REL-23`, severity major, `file`, `symbol`, `code` = the mapping and the state-changing call quoted verbatim from the diff, `fix` = the operation remapped to `POST`, or the handler made a replacement keyed by the URI, `rationale` naming the automatic repeat that performs the side effect twice).

## Source
RFC 9110 "HTTP Semantics" §9.2.2 "Idempotent Methods" — "the intended effect on the server of multiple identical requests with that method is the same as the effect for a single such request"; "PUT, DELETE, and safe request methods are idempotent"; "the idempotent property only applies to what has been requested by the user; a server is free to log each request separately, retain a revision control history, or implement other non-idempotent side effects for each idempotent request"; "Idempotent methods are distinguished because the request can be repeated automatically if a communication failure occurs before the client is able to read the server's response" (fetched from the httpwg source `draft-ietf-httpbis-semantics-latest.xml`).

---
title: A POST or PATCH handler whose clients may retry accepts an Idempotency-Key and returns the stored result for a repeated key
rule_id: REL-51
domain: reliability
triggers: ['@PostMapping', '@PatchMapping', 'RequestMethod[.]POST', 'Idempotency-Key', '@RequestHeader', 'charge\(', 'transfer\(', 'createOrder\(', 'place\(']
scope: file
check_kind: semantic
severity_default: major
---

# A POST or PATCH handler whose clients may retry accepts an Idempotency-Key and returns the stored result for a repeated key

## Thesis
A `POST` or `PATCH` endpoint that performs a non-idempotent side effect a client cannot afford twice — a charge, a transfer, an order, an outbound message — reads an `Idempotency-Key` request header, stores the key with the first response for a documented retention period, answers a repeat of the same key and payload with the stored response, and answers a repeat with a different payload with `422` and a concurrent repeat with `409`.

## Rationale
A client whose connection drops after the server committed and before the response arrived "is left uncertain about the status of the resource ... it doesn't know if it can safely retry the request", and a retry without a key "can result in duplication or incorrect updates": a second charge, a second order. The key lets the server recognize the repeat: on a "first time request (idempotency key and fingerprint has not been seen)" it processes normally; on a repeat after completion it "SHOULD respond with the result of the previously completed operation, success or an error"; on a repeat "before the original request completed" it "SHOULD respond with a resource conflict error". The dedupe must be atomic with the side effect — a check-then-act on the key store races with the concurrent repeat — and the key must be scoped to the client so one tenant's key cannot read another's response.

## Example
```java
bad:  @PostMapping("/charges") Charge charge(@RequestBody ChargeRequest r) { return svc.charge(r); }
good: @PostMapping("/charges")
      Charge charge(@RequestHeader("Idempotency-Key") String key, @RequestBody ChargeRequest r, Principal p) {
          return idempotency.execute(p.getName(), key, r, () -> svc.charge(r));   // stores key+response, 24 h TTL
      }
```

## Limits
A `POST` whose effect is naturally idempotent — an upsert keyed by the body, a search — needs no key. An endpoint whose clients are documented as never retrying, or whose duplicate the project context accepts (a log append), is out of scope. A dedupe done on a business key already in the payload (an order number the client generates) is an equivalent form.

## Validator
On the triggered hunk find each `POST`/`PATCH` handler and open the service it calls: does it create, charge, transfer or send something a duplicate would double? Check for an `Idempotency-Key` (or equivalent client-generated key) read from the request, a store consulted atomically before the side effect, and the stored response returned on a repeat. Validator question: **would a client's retry of this request, after a lost response, perform the side effect a second time?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: REL-51`, severity major, `file`, `symbol`, `code` = the handler signature quoted verbatim from the diff, `fix` = an `Idempotency-Key` parameter and an atomic key-to-response store around the side effect, `rationale` naming the duplicated side effect).

## Source
IETF `draft-ietf-httpapi-idempotency-key-header` "The Idempotency-Key HTTP Header Field" (`ietf-wg-httpapi/idempotency`, `main`) — "Repeating the request multiple times can result in duplication or incorrect updates ... The client is left uncertain about the status of the resource"; the key "MUST be unique and MUST NOT be reused with another request with a different request payload"; server behaviour — "First time request ... process the request normally"; "Duplicate request ... Retry: The request was retried after the original request completed. The resource SHOULD respond with the result of the previously completed operation"; "Concurrent request ... SHOULD respond with a resource conflict error"; a reused key with a different payload — `422`; a missing key on a documented idempotent operation — `400`. RFC 9110 §9.2.2 — `POST` and `PATCH` are not idempotent; a client may retry a non-idempotent request only with "some means to know that the request semantics are actually idempotent" (fetched from the httpwg source). The scoping of the key to the client — one tenant's key never reading another's stored response — is the card's own reading; the draft states the key's uniqueness, not its scope.

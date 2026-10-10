---
title: A POST or PATCH handler whose clients may retry accepts an Idempotency-Key and returns the stored result for a repeated key
rule_id: JAVA-182
domain: errors
step: [design, handle-errors]
applies_to: [java, service-boundary, public-api]
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
When the validator answers yes, the finder emits one finding (`rule_id: JAVA-182`, severity major, `file`, `symbol`, `code` = the handler signature quoted verbatim from the diff, `fix` = an `Idempotency-Key` parameter and an atomic key-to-response store around the side effect, `rationale` naming the duplicated side effect).

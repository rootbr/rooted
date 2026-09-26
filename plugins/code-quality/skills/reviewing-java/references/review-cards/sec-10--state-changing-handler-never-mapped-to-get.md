---
title: A handler that changes state is mapped to POST, PUT, PATCH or DELETE, never to GET or another safe method
rule_id: SEC-10
domain: security
triggers: ['@GetMapping', 'RequestMethod[.]GET', 'doGet\(', 'HttpMethod[.]GET', '@RequestMapping\(', '[.]GET\(|[.]get\(\s*"/']
scope: file
check_kind: semantic
severity_default: major
---

# A handler that changes state is mapped to POST, PUT, PATCH or DELETE, never to GET or another safe method

## Thesis
A controller method or servlet entry that creates, updates, deletes or otherwise mutates server-side state — including logout, "mark as read", "add to cart", a toggle — is reachable through POST, PUT, PATCH or DELETE only. A `@GetMapping`, `RequestMethod.GET`, `doGet` or method-less `@RequestMapping` on such an operation is the defect.

## Rationale
CSRF protection is applied to unsafe methods only, and the safe methods GET, HEAD, OPTIONS and TRACE are assumed read-only: no token is required for them, a `SameSite=Lax` cookie is still sent on a top-level GET navigation, and browser prefetchers and link previews issue GETs on their own. A GET that mutates state is therefore forgeable from an `<img src>` or a link on any page, with the victim's cookies attached, whatever the CSRF configuration says. A method-less `@RequestMapping` answers GET as well as POST and inherits the same exposure. Moving the operation to an unsafe method puts it back under the token check and under the `Lax` protection.

## Example
```java
bad:  @GetMapping("/orders/{id}/cancel")
      public String cancel(@PathVariable long id) { orders.cancel(id); return "ok"; }
good: @PostMapping("/orders/{id}/cancel")
      public String cancel(@PathVariable long id) { orders.cancel(id); return "ok"; }
```

## Limits
Applies to a GET handler that writes: a repository save or delete, a service call that mutates, a session attribute change with security meaning, an outbound call with side effects. A GET that only reads, or that records an idempotent observation with no security consequence (a view counter, a cache warm) under a documented project tolerance, is not flagged. A confirmation page served by GET that then posts is correct. A GET whose only write is an audit-log entry is reported at lower severity.

## Validator
On the triggered hunk take each GET-mapped or method-less handler and read its body and the service methods it calls, in the file. Identify any write: `save`, `delete`, `update`, an `INSERT` or `UPDATE` statement, a state-changing session or security call, a publish to a queue. Validator question: **does a request with a safe method change server-side state in this handler?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: SEC-10`, severity major, `file`, `symbol`, `code` = the mapping annotation and the mutating call quoted verbatim from the diff, `fix` = the same handler under `@PostMapping`, `@PutMapping`, `@PatchMapping` or `@DeleteMapping`, `rationale` naming the token exemption and the `Lax` navigation that a safe method keeps).

## Source
Spring Security reference, "Cross Site Request Forgery (CSRF)" §Safe Methods Must be Read-only — "requests with the HTTP GET, HEAD, OPTIONS, and TRACE methods should not change the state of the application"; "For either protection against CSRF to work" they must be read-only. OWASP Cross-Site Request Forgery Prevention Cheat Sheet — "Do not use GET requests for state changing operations"; §Limitations of SameSite — "Lax only blocks unsafe methods... If any state-changing operation in the application is reachable via a GET request, SameSite=Lax will not stop it". OWASP ASVS 5.0 requirement 3.5.3. RFC 9110 §9.2.1 "Safe Methods" — a method is safe when "the client does not request, and does not expect, any state change on the origin server as a result of applying a safe method to a target resource".

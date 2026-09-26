---
title: A lookup by a client-supplied identifier on user-owned data is scoped to the calling principal, not guarded by a role check alone
rule_id: SEC-21
domain: security
triggers: ['findById\(', 'getReferenceById\(|getById\(|getOne\(', '@PathVariable', 'deleteById\(|existsById\(', 'findByIdAnd', 'getPrincipal\(\)|@AuthenticationPrincipal']
scope: callers
check_kind: semantic
severity_default: critical
---

# A lookup by a client-supplied identifier on user-owned data is scoped to the calling principal, not guarded by a role check alone

## Thesis
When an id from a request selects an object that belongs to a user or a tenant — an order, an invoice, a document, a profile — the query includes the caller's identity (`findByIdAndOwnerId(id, principal.id)`, a tenant filter, a `@PostAuthorize("returnObject.owner == authentication.name")`) or the code checks ownership on the loaded object before acting; `repo.findById(id)` followed by the operation, with only a role check on the route, is the defect.

## Rationale
A role check answers "may this kind of user do this kind of thing"; it does not answer "may this user touch this object". An authenticated customer who changes `/orders/523` to `/orders/524` in the URL receives another customer's order when the lookup is by id alone — horizontal privilege escalation through a user-controlled key — and unguessable ids only make enumeration slower, not access wrong. The check belongs on every object operation — read, update, delete, export — and is easiest to make unforgettable by putting the owner into the query, so that a foreign id returns nothing rather than relying on a comparison someone must remember. Deriving the user from the session rather than from a request field is the same principle.

## Example
```java
bad:  @GetMapping("/orders/{id}") Order get(@PathVariable long id) { return orders.findById(id).orElseThrow(); }
good: @GetMapping("/orders/{id}") Order get(@PathVariable long id, @AuthenticationPrincipal User u) {
          return orders.findByIdAndCustomerId(id, u.getId()).orElseThrow(NotFoundException::new); }
```

## Limits
Applies to objects that have an owner or a tenant. Reference data with no owner (a product catalogue, a public post), and administrative endpoints whose role legitimately spans all objects, are not flagged; the finding names the object type's ownership. A tenant filter applied globally (a Hibernate filter or a multitenant datasource keyed by the session) documented in the project context is the correct form and rejects the finding. A lookup that loads the object and then compares its owner to the principal before any use is correct.

## Validator
On the triggered hunk find each repository lookup by an id that came from a request, and the operation performed on the result. Determine, from the entity in the file or from the repository across the codebase, whether the type has an owner or tenant field. Look for the principal in the query or an ownership comparison before the operation. Validator question: **can an authenticated user reach another user's object by changing the identifier in the request?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: SEC-21`, severity critical, `file`, `symbol`, `code` = the lookup and the operation quoted verbatim from the diff, `fix` = the owner-scoped query or the ownership check before use, `rationale` naming the object type and the identifier a user can change).

## Source
OWASP Authorization Cheat Sheet, "Ensure Lookup IDs are Not Accessible Even When Guessed or Cannot Be Tampered With" — the `acct_id` example; "A user should not be able to access a resource they do not have permissions simply because they are able to guess and manipulate that object's identifier"; CWE-639, Authorization Bypass Through User-Controlled Key. OWASP Insecure Direct Object Reference Prevention Cheat Sheet, "Mitigation" — "implement access control checks for each object that users try to access... determine the currently authenticated user from session information". OWASP ASVS 5.0 requirement 8.2.2.

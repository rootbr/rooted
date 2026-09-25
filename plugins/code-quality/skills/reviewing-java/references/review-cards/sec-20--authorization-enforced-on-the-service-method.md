---
title: Authorization for a protected operation is enforced on the service method that performs it, not only on the controller that exposes it
rule_id: SEC-20
domain: security
triggers: ['@PreAuthorize|@PostAuthorize|@Secured|@RolesAllowed', 'hasRole\(|hasAuthority\(|hasAnyRole\(|hasAnyAuthority\(', '@Service', '@RestController|@Controller', '@EnableMethodSecurity', 'isAuthenticated\(\)']
scope: callers
check_kind: semantic
severity_default: major
---

# Authorization for a protected operation is enforced on the service method that performs it, not only on the controller that exposes it

## Thesis
A service method that reads or changes data under an access rule — an order, an account, an administrative action — carries the rule itself (`@PreAuthorize`, `@PostAuthorize`, `@Secured`, or an explicit check against the current principal) so that every caller is covered. A rule placed on the controller alone, with the service method public and unchecked, is the defect when the service is reachable from another controller, a scheduled job, a message listener, a GraphQL resolver or a batch path.

## Rationale
Permission is validated on every request regardless of what initiated it; an attacker needs one entry that skips the check. A controller annotation guards one HTTP route. The service behind it is called by whatever else the codebase wires to it — a second endpoint added later, an event handler, a management command — and each of those enters without the check. Method security is built for enforcing the rule at the service layer, where the operation is defined once; the controller rule may stay as an early rejection, but the decisive check sits with the operation. A rule on the service is also the one a unit test of the service exercises.

## Example
```java
bad:  @RestController class AccountApi { @PreAuthorize("hasRole('ADMIN')") @DeleteMapping("/{id}")
          void close(@PathVariable long id) { accounts.close(id); } }
      @Service class AccountService { public void close(long id) { repo.deleteById(id); } }
good: @Service class AccountService {
          @PreAuthorize("hasRole('ADMIN')") public void close(long id) { repo.deleteById(id); } }
```

## Limits
Applies to an operation with an access rule. A service method with no rule of its own (a public catalogue read) is not flagged. An application whose only entry is one controller layer, with a project context stating that services are never called from elsewhere, is a tolerance the finder honours. A rule expressed as an ownership query (`findByIdAndOwner`) inside the service is a correct form. A gateway or filter that authorizes every route in front of all controllers still leaves non-HTTP entries, so it does not remove the finding on its own.

## Validator
On the triggered hunk find each authorization annotation or check on a controller method and the service method it calls, and each new public service method that touches user- or role-scoped data. Grep the repository for other callers of that service method: other controllers, `@Scheduled`, `@KafkaListener`, `@JmsListener`, `@RabbitListener`, `@EventListener`, resolvers, command-line runners. Validator question: **can the operation be invoked through a path that never passes the access rule?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: SEC-20`, severity major, `file`, `symbol`, `code` = the controller rule and the unchecked service method quoted verbatim from the diff, `fix` = the rule on the service method, `rationale` naming the caller that bypasses the controller).

## Source
OWASP Authorization Cheat Sheet, "Validate the Permissions on Every Request" — "regardless of whether the request was initiated by an AJAX script, server-side, or any other source... an attacker only needs to find one way in. Even if just a single access control check is "missed", the confidentiality and/or integrity of a resource can be jeopardized". Spring Security reference, "Method Security" — method authorization "is handy for... Enforcing security at the service layer". OWASP ASVS 5.0 requirement 8.3.1.

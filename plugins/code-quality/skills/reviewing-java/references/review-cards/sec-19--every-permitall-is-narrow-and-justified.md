---
title: Every permitAll or anonymous rule opens the narrowest matcher that covers the public endpoints
rule_id: SEC-19
domain: security
triggers: ['permitAll\(', '@PermitAll', '[.]anonymous\(', '@AnonymousAllowed', '"/\*\*"', 'hasIpAddress\(']
scope: file
check_kind: semantic
severity_default: major
---

# Every permitAll or anonymous rule opens the narrowest matcher that covers the public endpoints

## Thesis
A `permitAll()` (or `@PermitAll`, `anonymous()`) covers exactly the endpoints meant to be reached without authentication — a login page, a health probe, static assets, a public read-only API — by a matcher that names them. A `permitAll` over `/**`, or over an API prefix that also holds authenticated operations, is the defect; the fix narrows the matcher to the public paths and records the reason beside it, in a comment or in the matcher's own name.

## Rationale
Access control fails one endpoint at a time: an attacker needs one path that lacks a check. A wide `permitAll` is the simplest way to create such a path, because it opens every endpoint added under the prefix in the future as well as the ones present now, and nothing in a request trace shows that an authenticated endpoint became public. Deny-by-default requires the reverse habit: each grant is justified explicitly, so the reader of the diff can check the justification against the endpoints the pattern covers. A stated reason also survives the next refactoring, when the matcher is widened for convenience.

## Example
```java
bad:  .requestMatchers("/api/**").permitAll()
good: .requestMatchers("/api/public/**", "/actuator/health").permitAll()   // unauthenticated catalogue and probe
```

## Limits
Applies to grants the diff adds or widens. Static-resource patterns (`/css/**`, `/js/**`, `/favicon.ico`), the login and error pages, and `dispatcherTypeMatchers(FORWARD, ERROR)` are conventional public matchers and are not flagged. A narrow grant that carries no comment is not flagged; the reason is part of the fix when a grant is narrowed, not a finding on its own. A project context listing the public endpoints rejects the finding for those. A `permitAll` on a chain scoped by `securityMatcher` to a public API is judged against that chain's endpoints only.

## Validator
On the triggered hunk take each `permitAll` or anonymous grant and its matcher. Open the file and, for a pattern, enumerate the controllers or paths it covers as far as the file and the diff show; note any comment or self-describing path (`public`, `health`, `login`, `static`) that names the reason, for the fix. Validator question: **does the grant cover an endpoint that is not meant to be public?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: SEC-19`, severity major, `file`, `symbol`, `code` = the grant and its matcher quoted verbatim from the diff, `fix` = the matcher narrowed to the public paths with the reason beside it (a comment or a self-describing matcher), `rationale` naming the endpoints the grant opens beyond the public ones).

## Source
OWASP Authorization Cheat Sheet, "Deny by Default" — "One should be able to explicitly justify why a specific permission was granted to a particular user or group rather than assuming access to be the default position"; "Validate the Permissions on Every Request" — "an attacker only needs to find one way in". OWASP ASVS 5.0 requirement 8.2.1. Spring Security reference, "Authorize HttpServletRequests" — `permitAll`: "The request requires no authorization and is a public endpoint".

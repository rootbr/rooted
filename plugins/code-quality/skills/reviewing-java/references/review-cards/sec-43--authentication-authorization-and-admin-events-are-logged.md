---
title: An authentication outcome, an authorization denial and an administrative action are each logged with actor, action, resource and outcome
rule_id: SEC-43
domain: security
triggers: ['AuthenticationFailureHandler', 'AuthenticationSuccessHandler', 'AccessDeniedHandler', 'AuthenticationEntryPoint', 'onAuthenticationFailure\(', 'onAuthenticationSuccess\(', 'AuthenticationProvider', 'AccessDeniedException', 'AuthenticationEventPublisher', 'hasRole\(.?ADMIN', 'ROLE_ADMIN']
scope: file
check_kind: semantic
severity_default: minor
---

# An authentication outcome, an authorization denial and an administrative action are each logged with actor, action, resource and outcome

## Thesis
Code that decides an authentication (success and failure, including a second factor and a password reset), denies an authorization, or performs an administrative action — user creation or deletion, a privilege or role change, a configuration change, a key rotation — writes one log event carrying who (the principal or the attempted username, never the credential), what (the action or endpoint), on what (the resource id) and the outcome, or publishes the framework's security event so that its listener records it.

## Rationale
Failed and successful authentications are the earliest signal of credential stuffing, password spraying and account takeover; authorization denials show probing of what a user may not reach; administrative actions are what an attacker with a foothold performs first. A handler that swallows the failure, a custom provider that returns `null` without a trace, or an admin endpoint that changes a role silently leaves no record for detection or investigation. The event with actor, action, resource and outcome is what an alert on failed-login rate or on a burst of denials is computed from; without the event no alert can exist.

## Example
```java
bad:  public void onAuthenticationFailure(HttpServletRequest rq, HttpServletResponse rs, AuthenticationException e) throws IOException {
          rs.sendError(401); }
good: public void onAuthenticationFailure(HttpServletRequest rq, HttpServletResponse rs, AuthenticationException e) throws IOException {
          log.warn("auth_failure user={} ip={} reason={}", rq.getParameter("username"), rq.getRemoteAddr(), e.getClass().getSimpleName());
          rs.sendError(401); }
```

## Limits
Applies to code that replaces or adds a security decision or an administrative action. A custom handler or provider that delegates to the framework's default handler or to its authentication event publisher inherits the framework's record and is not flagged when the delegation is shown. An audit written through a dedicated audit service or table satisfies the rule. The log line must not carry the password, token or secret; that is a separate defect.

## Validator
On the triggered hunk find each authentication handler, provider, access-denied handler, admin-role endpoint or role and privilege mutation. Open the file and look for a log call or an event publication on the success and the failure path that carries actor, action, resource and outcome. Validator question: **does this security decision or administrative action complete with no log event and no published security event?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: SEC-43`, severity minor, `file`, `symbol`, `code` = the handler or action method signature quoted verbatim from the diff, `fix` = the log or event line with actor, action, resource and outcome, `rationale` naming the attack the missing event would have revealed).

## Source
OWASP ASVS 5.0 §16.3.1 — "all authentication operations are logged, including successful and unsuccessful attempts"; §16.3.2 — "failed authorization attempts are logged"; §16.2.1 — each log entry includes when, where, who and what. OWASP Logging Cheat Sheet, "Which events to log" — always log authentication successes and failures, authorization (access control) failures, user administration actions, use of administrative privileges, changes to privileges, and encryption key use or rotation. Spring Security reference, "Authentication Events" — the `AuthenticationEventPublisher` and the success and failure events the framework publishes. CWE-778 — by id.

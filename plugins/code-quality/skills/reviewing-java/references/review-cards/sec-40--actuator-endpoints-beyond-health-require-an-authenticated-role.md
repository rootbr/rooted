---
title: Actuator endpoints beyond health require an authenticated role in the SecurityFilterChain; no permitAll covers EndpointRequest.toAnyEndpoint or /actuator/**
rule_id: SEC-40
domain: security
triggers: ['EndpointRequest', '/actuator', 'toAnyEndpoint\(', '@Endpoint\(', '@WebEndpoint\(', '@RestControllerEndpoint', '@ControllerEndpoint', 'management[.]endpoints']
scope: file
check_kind: mechanical
severity_default: major
---

# Actuator endpoints beyond health require an authenticated role in the SecurityFilterChain; no permitAll covers EndpointRequest.toAnyEndpoint or /actuator/**

## Thesis
A `SecurityFilterChain` whose matchers cover actuator endpoints — `EndpointRequest.toAnyEndpoint()`, `EndpointRequest.to(…)`, `/actuator/**` or the management base path — grants `permitAll` at most to `health` and requires `hasRole` or `authenticated` for every other endpoint; a custom `@Endpoint`, `@WebEndpoint` or `@RestControllerEndpoint` bean that exposes state or an action falls under the same rule.

## Rationale
Spring Boot exposes only `health` over HTTP by default and, when Spring Security is present and no `SecurityFilterChain` bean is defined, secures every other actuator endpoint; defining any `SecurityFilterChain` bean makes that auto-configuration back off, so the access rules for the actuators become whatever the bean states. `env` and `configprops` return the effective configuration, sanitised by value name; `heapdump` returns a dump of the JVM heap; `threaddump`, `mappings` and `beans` enumerate internals; `loggers` changes log levels; `shutdown` stops the process. Any of them reachable without authentication is information disclosure or denial of service to whoever finds the path, and a `permitAll` on the whole endpoint matcher opens every endpoint the exposure property lists now or later.

## Example
```java
bad:  http.securityMatcher(EndpointRequest.toAnyEndpoint())
          .authorizeHttpRequests(r -> r.anyRequest().permitAll());
good: http.securityMatcher(EndpointRequest.toAnyEndpoint())
          .authorizeHttpRequests(r -> r
              .requestMatchers(EndpointRequest.to(HealthEndpoint.class)).permitAll()
              .anyRequest().hasRole("ENDPOINT_ADMIN"))
          .httpBasic(withDefaults());
```

## Limits
Applies to an application reachable from outside its host. A management port bound to a private or loopback address, or a firewall rule, named in the project context as the control, rejects the finding for that deployment. `health` with details hidden is the documented default exposure; a curated `info` endpoint permitted without authentication, or a metrics endpoint permitted to a scraper's network, is a tolerance the project context states. The exposure property is configuration, not Java, and does not decide the finding: an endpoint not exposed is unreachable today, and a `permitAll` written now opens whatever is exposed tomorrow.

## Validator
On the triggered hunk find each `permitAll` or `anonymous` attached to a matcher that covers actuator paths, and each custom endpoint bean. Open the file to read the whole `authorizeHttpRequests` chain and the `securityMatcher`. Validator question: **does this chain let an unauthenticated request reach an actuator endpoint other than health?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: SEC-40`, severity major, `file`, `symbol`, `code` = the matcher and its `permitAll` quoted verbatim from the diff, `fix` = `permitAll` narrowed to the health endpoint with `anyRequest().hasRole(…)` after it, `rationale` naming the endpoints opened and what each discloses or does).

## Source
Spring Boot reference, "Actuator → Endpoints → Security" — "only the /health endpoint is exposed over HTTP by default"; "If Spring Security is on the classpath and no other SecurityFilterChain bean is present, all actuators other than /health are secured by Spring Boot auto-configuration. If you define a custom SecurityFilterChain bean, Spring Boot auto-configuration backs off and lets you fully control the actuator access rules"; the typical configuration matching `EndpointRequest.toAnyEndpoint()` with `hasRole("ENDPOINT_ADMIN")`; "Exposing Endpoints" — "Since Endpoints may contain sensitive information, you should carefully consider when to expose them"; "Sanitize Sensitive Values" — `/env` and `/configprops` values sanitised by default. OWASP ASVS 5.0 §13.4.5 — documentation and monitoring endpoints not exposed unless explicitly intended. CWE-200 — by id.

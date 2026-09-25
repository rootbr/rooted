---
title: CORS for a Spring Security application is configured through the security filter chain, not only through Spring MVC annotations
rule_id: SEC-48
domain: security
triggers: ['@CrossOrigin', 'addCorsMappings\(', 'CorsConfiguration', '[.]cors\(', 'CorsFilter|CorsConfigurationSource', 'Access-Control-Allow-Origin']
scope: callers
check_kind: semantic
severity_default: minor
---

# CORS for a Spring Security application is configured through the security filter chain, not only through Spring MVC annotations

## Thesis
When an application secured by Spring Security serves cross-origin browser clients, the CORS configuration is applied through `http.cors(...)` with a `CorsConfigurationSource` bean (or the Spring MVC configuration that `cors(withDefaults())` picks up), so that the `CorsFilter` runs before authentication; `@CrossOrigin` on controllers or `addCorsMappings` in a `WebMvcConfigurer` with no `cors(...)` in the chain is the defect.

## Rationale
A preflight `OPTIONS` request carries no cookies and no authorization header. If Spring Security handles it first, the request is unauthenticated and is rejected, so the browser never sends the real request; CORS has to be processed before Spring Security, which is what `http.cors(...)` arranges by placing the `CorsFilter` ahead of the security filters. Controller-level annotations run after the security chain and never see the rejected preflight. With more than one `CorsConfigurationSource` bean the framework configures nothing automatically and the source is passed to `cors(...)` explicitly. The allowed origins listed in the source are the security decision.

## Example
```java
bad:  @CrossOrigin(origins = "https://app.example") @RestController class Api { ... }   // no http.cors(...)
good: @Bean CorsConfigurationSource corsConfigurationSource() {
          CorsConfiguration c = new CorsConfiguration(); c.setAllowedOrigins(List.of("https://app.example"));
          c.setAllowedMethods(List.of("GET", "POST")); c.setAllowCredentials(true);
          UrlBasedCorsConfigurationSource s = new UrlBasedCorsConfigurationSource(); s.registerCorsConfiguration("/api/**", c); return s; }
      http.cors(Customizer.withDefaults());
```

## Limits
Applies to applications with Spring Security on the classpath that serve browser clients from another origin. A same-origin application with no cross-origin clients needs no CORS. `cors(withDefaults())` with only Spring MVC's global CORS configuration and no `CorsConfigurationSource` bean is the documented MVC integration and is correct. An application behind a gateway that terminates CORS, named in the project context, rejects the finding.

## Validator
On the triggered hunk find each CORS declaration. Grep the repository for `cors(` in a `SecurityFilterChain` and for `CorsConfigurationSource` beans. Validator question: **is CORS declared only at the MVC layer while a Spring Security chain protects the same endpoints?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: SEC-48`, severity minor, `file`, `symbol`, `code` = the MVC-level CORS declaration quoted verbatim from the diff, `fix` = a `CorsConfigurationSource` bean with `http.cors(...)` on the chain, `rationale` naming the preflight the security chain rejects before the annotation runs).

## Source
Spring Security reference, "CORS" — "CORS must be processed before Spring Security, because the pre-flight request does not contain any cookies (that is, the JSESSIONID). If the request does not contain any cookies and Spring Security is first, the request determines that the user is not authenticated (since there are no cookies in the request) and rejects it"; "The easiest way to ensure that CORS is handled first is to use the CorsFilter"; §Spring MVC Integration; "If you have more than one CorsConfigurationSource bean, Spring Security won't automatically configure CORS support for you".

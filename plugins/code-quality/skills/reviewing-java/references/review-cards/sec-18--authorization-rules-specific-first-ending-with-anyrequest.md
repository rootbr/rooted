---
title: Request authorization rules are declared most specific first and end with an anyRequest rule, so no broad permitAll shadows a narrower rule
rule_id: SEC-18
domain: security
triggers: ['authorizeHttpRequests\(', 'requestMatchers\(', 'anyRequest\(\)', 'permitAll\(\)', 'securityMatcher\(', 'authorizeExchange\(|pathMatchers\(']
scope: file
check_kind: mechanical
severity_default: critical
---

# Request authorization rules are declared most specific first and end with an anyRequest rule, so no broad permitAll shadows a narrower rule

## Thesis
Inside `authorizeHttpRequests` (and the reactive `authorizeExchange`) the rules are ordered from the most specific matcher to the most general, and the list ends with `anyRequest().authenticated()` (or `denyAll()` when everything permitted is listed). A `permitAll()` on a prefix such as `/api/**` placed before `requestMatchers("/api/admin/**").hasRole("ADMIN")` is the defect: the first rule matches and the second never runs.

## Rationale
The authorization filter evaluates the pattern/rule pairs in declaration order and applies only the first match. A broad pattern earlier in the list therefore decides for every path under it, and a rule for a sub-path declared later is dead configuration — the admin endpoints are public, and no test of the admin rule alone shows it. Ordering narrow-before-broad makes each rule reachable; the terminal `anyRequest` rule turns the list into an allowlist in which every unlisted path is authenticated or denied, so an endpoint added without a rule is protected rather than exposed. Denying by default is the documented healthy practice, and the explicit terminal rule is the shape the reordered list ends with.

## Example
```java
bad:  http.authorizeHttpRequests(a -> a
          .requestMatchers("/api/**").permitAll()
          .requestMatchers("/api/admin/**").hasRole("ADMIN")
          .anyRequest().authenticated());
good: http.authorizeHttpRequests(a -> a
          .requestMatchers("/api/admin/**").hasRole("ADMIN")
          .requestMatchers("/api/public/**").permitAll()
          .anyRequest().authenticated());
```

## Limits
Applies to the rule list of one chain. Two chains separated by `securityMatcher` are ordered by their `@Order`, which is a different check. `dispatcherTypeMatchers(FORWARD, ERROR).permitAll()` declared first is the documented form for view rendering and error pages and is not a shadowing rule. A method-restricted matcher (`requestMatchers(HttpMethod.GET, ...)`) narrower than a later path rule is correct when the later rule is meant for the other methods. A rule list with no terminal `anyRequest` rule is not flagged on its own: the finding is the shadowing pair, and the fix ends the reordered list with `anyRequest().authenticated()` or `denyAll()` so the default is stated for the reader.

## Validator
On the triggered hunk read the rules in order. For each pair of rules, check whether an earlier pattern matches every path a later pattern matches (a prefix `/x/**` before `/x/y/**`, `/**` before anything) while granting more. Note whether the last rule is `anyRequest()`, for the fix. Validator question: **is there a later rule whose paths an earlier, more permissive rule already matches?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: SEC-18`, severity critical, `file`, `symbol`, `code` = the shadowing rule and the shadowed rule quoted verbatim from the diff, `fix` = the rules reordered narrow-first, ending with `anyRequest().authenticated()` (or `denyAll()`) where the list has no terminal rule, `rationale` naming the first-match evaluation and the paths the earlier rule opens).

## Source
Spring Security reference, "Authorize HttpServletRequests" — "AuthorizationFilter processes these pairs in the order listed, applying only the first match to the request"; "Each rule is considered in the order they were declared"; "Any URL that has not already been matched on is denied access. This is a good strategy if you do not want to accidentally forget to update your authorization rules"; "Denying the request by default is a healthy security practice since it turns the set of rules into an allow list". OWASP Authorization Cheat Sheet, "Deny by Default".

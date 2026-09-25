---
title: A Content-Security-Policy set from a SecurityFilterChain is strict, with a nonce or hash for scripts, object-src and base-uri none, and no unsafe-inline or unsafe-eval
rule_id: SEC-07
domain: security
triggers: ['contentSecurityPolicy\(', 'Content-Security-Policy', 'policyDirectives\(', 'unsafe-inline|unsafe-eval', 'script-src|default-src', 'ContentSecurityPolicyHeaderWriter']
scope: hunk
check_kind: mechanical
severity_default: major
---

# A Content-Security-Policy set from a SecurityFilterChain is strict, with a nonce or hash for scripts, object-src and base-uri none, and no unsafe-inline or unsafe-eval

## Thesis
A policy string passed to `contentSecurityPolicy(csp -> csp.policyDirectives(...))` or written as a `Content-Security-Policy` header sets `object-src 'none'` and `base-uri 'none'`, and its `script-src` (or `default-src` where `script-src` is absent) carries no `'unsafe-inline'`, no `'unsafe-eval'` and no bare `*`, `https:` or `data:` source; scripts are admitted by a per-response `'nonce-…'` or a `'sha256-…'` hash, optionally with `'strict-dynamic'`, or by an allowlist of named hosts. `'unsafe-inline'` or `'unsafe-eval'` in `script-src`, a wildcard source in place of a list, or a policy that omits `object-src 'none'` or `base-uri 'none'` is the defect in every application; a host allowlist in place of a nonce or hash is the defect only where the project context states that the application is assessed at ASVS level 3. Where the application cannot yet meet the policy, `Content-Security-Policy-Report-Only` with a report endpoint is the staging form, not a weakened enforced policy.

## Rationale
CSP is the browser-side layer that stops an injected script from running when output encoding failed somewhere; its value is exactly what `script-src` admits. `'unsafe-inline'` admits every inline script, including the one an attacker injected, so the policy stops nothing; `'unsafe-eval'` re-enables `eval` and string-to-code constructs; a `*`, `https:` or `data:` source names no host and so defines no allowlist at all. A nonce that is random per response, or a hash of each approved inline script, admits only the scripts the server placed, and `'strict-dynamic'` extends that trust to scripts those load without listing every host; that strict form is the leading practice because it is easier to deploy and less likely to be bypassed than a host allowlist, and it is the required form at ASVS level 3, below which an allowlist of named hosts meets the minimum. `object-src 'none'` closes plugin-based execution and `base-uri 'none'` stops a `<base>` injection from redirecting relative script URLs, whichever form admits the scripts. The nonce is added to the policy and to each approved script tag by the server's templating; a middleware that stamps the nonce on every script tag stamps the injected one too. Spring Security adds no CSP by default, so the policy exists only where a diff writes it.

## Example
```java
bad:  .contentSecurityPolicy(csp -> csp.policyDirectives(
          "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'"))
good: String nonce = Base64.getEncoder().encodeToString(randomBytes(16));   // fresh per response
      response.setHeader("Content-Security-Policy",
          "script-src 'nonce-" + nonce + "' 'strict-dynamic'; object-src 'none'; base-uri 'none'");
```

## Limits
Applies to a policy the diff writes or changes. A hash-based policy in a static `policyDirectives` string is correct when the inline scripts are fixed. `'unsafe-inline'` beside a nonce or hash source in the same `script-src` — the form `'nonce-…' 'strict-dynamic' 'unsafe-inline' https:` — is the backward-compatible strict policy: a browser that understands nonces and hashes ignores the keyword and an older one falls back to it, so it is not flagged. `'unsafe-inline'` in `style-src` is a lesser weakening, noted in the finding but not flagged at this severity on its own. A host allowlist with no nonce or hash is flagged only where the project context states ASVS level 3; elsewhere it meets the minimum and is not flagged. At level 3 a project context that documents a legacy allowlist policy as accepted rejects that finding. A `Content-Security-Policy-Report-Only` header is a monitoring stage and is not flagged. A pure JSON API that serves no HTML needs no script policy; the finding applies to responses a browser renders.

## Validator
On the triggered hunk read the policy string. Check `script-src` (or `default-src` when `script-src` is absent) for `'unsafe-inline'` with no nonce or hash source beside it, for `'unsafe-eval'`, and for a bare `*`, `https:` or `data:`; check for `object-src 'none'` and `base-uri 'none'`; note whether scripts are admitted by a nonce or hash or by a host allowlist, and whether the project context states ASVS level 3. Validator question: **does the enforced policy carry `'unsafe-inline'` (with no nonce or hash beside it), `'unsafe-eval'` or a wildcard script source, omit `object-src 'none'` or `base-uri 'none'`, or — where the project context states ASVS level 3 — admit scripts by a host allowlist instead of a nonce or hash?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: SEC-07`, severity major, `file`, `symbol`, `code` = the policy string quoted verbatim from the diff, `fix` = the policy with the offending keyword removed and `object-src 'none'` and `base-uri 'none'` present, or — at level 3 — the nonce- or hash-based `script-src`, `rationale` naming the source keyword or missing directive that lets an injected script, a plugin or a `<base>` element take over).

## Source
OWASP ASVS 5.0 requirement 3.4.3 — "As a minimum, a global policy must be used which includes the directives object-src 'none' and base-uri 'none' and defines either an allowlist or uses nonces or hashes. For an L3 application, a per-response policy with nonces or hashes must be defined". OWASP Content Security Policy Cheat Sheet, "CSP Types" — "current leading practice is to create a "Strict" CSP which is much easier to deploy and more secure as it is less likely to be bypassed"; "Strict CSP" — nonce-based and hash-based policies `script-src 'nonce-{RANDOM}' 'strict-dynamic'; object-src 'none'; base-uri 'none'`; "Don't create a middleware that replaces all script tags with "script nonce=..." because attacker-injected scripts will then get the nonces as well"; the `'unsafe-inline'` and `'unsafe-eval'` source keywords. Spring Security reference, "Security HTTP Response Headers" §Content Security Policy — "Spring Security does not add Content Security Policy by default". The backward-compatible form in the Limits rests on the W3C Content Security Policy Level 3 source-list rule that a nonce or hash source makes `'unsafe-inline'` ignored, which is not among these fetched sources.

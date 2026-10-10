---
title: A cookie that carries a session id, a token or another credential is set with HttpOnly, Secure, an explicit SameSite and a __Host- or __Secure- name prefix
rule_id: SEC-47
domain: security
triggers: ['new Cookie\(', 'ResponseCookie[.]from\(', 'addCookie\(', 'Set-Cookie|SET_COOKIE', 'httpOnly\(|setHttpOnly\(|[.]secure\(|setSecure\(|sameSite\(', '(?i)(session|token|jwt|refresh|auth)\w*cookie|cookie\w*(session|token|jwt|refresh)']
scope: file
check_kind: mechanical
severity_default: major
---

# A cookie that carries a session id, a token or another credential is set with HttpOnly, Secure, an explicit SameSite and a __Host- or __Secure- name prefix

## Thesis
Code that writes a cookie holding a session identifier, a JWT, a refresh token, a remember-me value or any credential sets `HttpOnly` (script cannot read it), `Secure` (sent over HTTPS only), an explicit `SameSite` (`Strict`, or `Lax` when cross-site navigation must keep the login), a path, and a `__Host-` name prefix (or `__Secure-` where subdomains must share the cookie). A `new Cookie(name, token)` added to the response with the defaults — no `HttpOnly`, `Secure` false — is the defect.

## Rationale
The cookie's value is the credential. Without `HttpOnly`, any injected script reads it through `document.cookie` and sends it away, turning a single XSS into account takeover; with it, the script can still make requests as the user but cannot exfiltrate the credential. Without `Secure`, a browser tricked into an `http://` reference to the host sends the cookie in clear, and an on-path attacker reads it even when the site itself is HTTPS-only. `SameSite` decides whether cross-site requests carry the cookie, which is the automatic attachment CSRF relies on; the browser default varies, so the attribute is set explicitly. The `__Host-` prefix commits the cookie to `Secure`, no `Domain` attribute and `Path=/`, which prevents a subdomain from forging it and an HTTPS downgrade from planting it; `__Secure-` commits `Secure` alone and is for the case where subdomains must share the cookie. `HttpOnly` is not encryption: the value still travels and is stored in clear, so nothing secret beyond the credential belongs in it.

## Example
```java
bad:  Cookie c = new Cookie("refresh_token", token); response.addCookie(c);
good: ResponseCookie c = ResponseCookie.from("__Host-refresh_token", token)
          .httpOnly(true).secure(true).sameSite("Strict").path("/").maxAge(Duration.ofDays(14)).build();
      response.addHeader(HttpHeaders.SET_COOKIE, c.toString());
```

## Limits
Applies to cookies carrying credentials or session state. A CSRF token cookie that JavaScript must read is set without `HttpOnly` by design and keeps `Secure` and `SameSite`. A preference cookie with no security meaning is out of scope. A local development profile that runs plain HTTP may relax `Secure`, and with it the prefix, behind a profile guard shown in the diff. The container's own session cookie is configured in server properties, not in this code, and is out of this card's scope.

## Validator
On the triggered hunk find each cookie construction and the attributes set on it; identify from the name and the value's origin whether it carries a credential. Validator question: **is a credential-bearing cookie written without HttpOnly, without Secure, without an explicit SameSite, or without a __Host- or __Secure- name prefix?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: SEC-47`, severity major, `file`, `symbol`, `code` = the cookie construction quoted verbatim from the diff, `fix` = the same cookie with `HttpOnly`, `Secure`, `SameSite` and a `__Host-` (or `__Secure-`) prefix, `rationale` naming the attribute missing and the exposure it opens).

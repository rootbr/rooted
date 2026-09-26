---
title: An HTTP client that reaches a destination a client can influence has redirect following off, or re-validates every redirect target before following it
rule_id: SEC-13
domain: security
triggers: ['followRedirects\(', 'Redirect[.](NORMAL|ALWAYS)', 'setInstanceFollowRedirects\(|setFollowRedirects\(', 'SimpleClientHttpRequestFactory|HttpComponentsClientHttpRequestFactory|JdkClientHttpRequestFactory', 'setRedirectStrategy\(|LaxRedirectStrategy|DefaultRedirectStrategy|followRedirect\(', 'openConnection\(']
scope: file
check_kind: semantic
severity_default: major
---

# An HTTP client that reaches a destination a client can influence has redirect following off, or re-validates every redirect target before following it

## Thesis
An HTTP client used for a request whose URL a request value influenced is built with automatic redirects off — `HttpClient.newBuilder().followRedirects(Redirect.NEVER)`, which is the JDK client's default, `HttpURLConnection.setInstanceFollowRedirects(false)`, a `RestTemplate` or `RestClient` request factory or Apache client with redirects disabled, `followRedirect(false)` on Reactor Netty — and, where a redirect must be honoured, reads the `Location` header and runs the same host, scheme and address validation on it before issuing the next request. A client with the JDK's `Redirect.NORMAL`, `HttpURLConnection`'s default, or a redirect strategy enabled, sent to a validated URL, is the defect.

## Rationale
The validation covered the first URL only. A server the attacker controls answers with `302 Location: http://169.254.169.254/latest/meta-data/`, and a client that follows redirects issues that second request unchecked — the destination check is bypassed by one response header. `HttpURLConnection` follows redirects by default; the JDK `HttpClient` does not unless the builder sets a policy; `RestTemplate` inherits its factory's client behaviour, which for `HttpURLConnection` is to follow. Turning following off makes the redirect visible to the code as a 3xx response, whose `Location` the code can validate like any other input; that is the form the SSRF defense requires. An open redirect on a trusted allowlisted host produces the same bypass, which is why the target of each hop, not only the first, is validated.

## Example
```java
bad:  HttpClient c = HttpClient.newBuilder().followRedirects(HttpClient.Redirect.NORMAL).build();
      c.send(HttpRequest.newBuilder(validated).build(), BodyHandlers.ofString());
good: HttpClient c = HttpClient.newBuilder().followRedirects(HttpClient.Redirect.NEVER).build();
      HttpResponse<String> r = c.send(HttpRequest.newBuilder(validated).build(), BodyHandlers.ofString());
      if (r.statusCode() / 100 == 3) { URI next = validate(r.headers().firstValue("Location").orElseThrow()); /* re-issue */ }
```

## Limits
Applies when the destination is influenced by a request. A client whose destinations are fixed configuration may follow redirects. A client wrapped by a redirect strategy that calls the destination validator on each hop is the correct form. Refusing an HTTPS-to-HTTP hop, which the JDK's `NORMAL` policy does, is not the protection in question.

## Validator
On the triggered hunk find each client construction or factory and its redirect setting (an explicit policy, or the type's default: `HttpURLConnection` follows, the JDK `HttpClient` does not). Open the file and determine whether the requests sent through it can carry a request-influenced destination, and whether any 3xx handling re-validates `Location`. Validator question: **can a response from an attacker-influenced server redirect this client to a destination the validation never saw?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: SEC-13`, severity major, `file`, `symbol`, `code` = the client construction or redirect setting quoted verbatim from the diff, `fix` = redirects disabled with `Location` validated before any re-issue, `rationale` naming the second request the redirect issues without validation).

## Source
OWASP Server-Side Request Forgery Prevention Cheat Sheet — "Disable the support for the following of the redirection in your web client in order to prevent the bypass of the input validation"; Case 2, step 7 — "don't forget to disable the support for redirection in the web client used". `java.net.http.HttpClient.Builder#followRedirects` Javadoc, Java SE 21 — newly built clients "will use a default redirection policy of NEVER"; `HttpClient.Redirect.NORMAL` — "Always redirect, except from HTTPS URLs to HTTP URLs". `java.net.HttpURLConnection#setFollowRedirects` Javadoc — redirects "automatically followed by this class. True by default". CWE-918.

---
title: A server-side request whose destination a client can influence goes only to an allowlisted host and scheme, and never to a loopback, link-local, private or unique-local address
rule_id: SEC-11
domain: security
triggers: ['RestTemplate|RestClient|WebClient', 'HttpClient[.]newBuilder\(|HttpRequest[.]newBuilder\(', 'new URL\(|URI[.]create\(|new URI\(', 'openConnection\(', '(?i)webhook|callback[_ ]?ur[li]|target[_ ]?ur[li]|remote[_ ]?ur[li]', 'getForObject\(|getForEntity\(|exchange\(|retrieve\(|postForObject\(']
scope: file
check_kind: semantic
severity_default: critical
---

# A server-side request whose destination a client can influence goes only to an allowlisted host and scheme, and never to a loopback, link-local, private or unique-local address

## Thesis
When any part of the URL a server-side HTTP (or other protocol) client will call comes from a request — a webhook URL, a callback, an image-fetch URL, a host parameter — the code either maps the input to an entry of a fixed host allowlist and builds the URL itself with a fixed scheme, port and path, or parses the input, checks the scheme against `https` (or an explicit allowed set), checks the host against the allowlist, and rejects any resolved address that is loopback, link-local, site-local (private), any-local or IPv6 unique-local. A client called with the raw input is the defect.

## Rationale
The server sends the request from inside the network, so a URL an attacker chooses reaches what the attacker cannot: the cloud instance-metadata endpoint at `169.254.169.254` (credentials for the instance role), `localhost` admin ports, databases and internal services on private ranges, and non-HTTP schemes (`file:`, `gopher:`, `dict:`) where the client supports them. A denylist of known-bad hosts is bypassed by alternate encodings of the same address (decimal, octal, hex, IPv6-mapped), by a DNS name pointing at an internal address, and by the next internal service nobody listed; an allowlist of hosts the application is meant to reach, compared by exact string after parsing, is the defense that survives those. Parsing before checking matters: `http://good.example\@evil.example` reads as different hosts in different parsers, so the host the client will use is the one to validate. The `InetAddress` classification methods give the range checks for `127.0.0.0/8`, `169.254.0.0/16`, `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`, `0.0.0.0` and `::1`; the IPv6 unique-local range `fc00::/7` needs an explicit prefix test.

## Example
```java
bad:  String url = req.getParameter("callback");
      rest.postForObject(url, payload, Void.class);
good: URI u = URI.create(req.getParameter("callback"));
      if (!"https".equals(u.getScheme()) || !ALLOWED_HOSTS.contains(u.getHost())) throw new IllegalArgumentException();
      for (InetAddress a : InetAddress.getAllByName(u.getHost()))
          if (a.isLoopbackAddress() || a.isLinkLocalAddress() || a.isSiteLocalAddress() || a.isAnyLocalAddress()) throw new IllegalArgumentException();
      rest.postForObject(u, payload, Void.class);
```

## Limits
Applies when the destination depends on a request value. A client whose base URL is configuration and whose only variable part is a path segment or query value encoded into a fixed template is not flagged, unless the variable part can carry a scheme or host. An application whose business is fetching arbitrary public URLs cannot allowlist and takes the range-rejection form plus a resolver that resolves no internal names, which the project context documents. A destination chosen from configuration by a key the request supplies (`hosts.get(key)`) is the correct mapping form.

## Validator
On the triggered hunk find each client call and each URL or URI construction, and trace the URL string or its host component to its origin in the file. When it originates in a request, look for the allowlist comparison of the parsed host and the scheme check before the call, and for rejection of the resolved addresses where the allowlist is absent. Validator question: **can a request choose a host, scheme or address that the code did not enumerate, and does the client then connect to it?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: SEC-11`, severity critical, `file`, `symbol`, `code` = the client call and the URL construction quoted verbatim from the diff, `fix` = the allowlist lookup or the parse-check-reject sequence before the call, `rationale` naming the internal destination the request can reach).

## Source
OWASP Server-Side Request Forgery Prevention Cheat Sheet — Case 1, allowlist of "identified and trusted applications"; "Match the host against an allowlist, and build the request yourself"; "Treat parser disagreement as a rejection"; Case 2, block-list of private, loopback and link-local ranges; "Deny-list (Last Resort)" table (`169.254.169.254`, `127.0.0.0/8`, `0.0.0.0/8`, `::1/128`, RFC 1918 ranges). OWASP ASVS 5.0 requirement 13.2.4. `java.net.InetAddress#isLoopbackAddress`, `#isLinkLocalAddress`, `#isSiteLocalAddress`, `#isAnyLocalAddress` Javadoc, Java SE 21. CWE-918.

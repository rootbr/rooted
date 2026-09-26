---
title: The address a server-side request connects to is the address that passed the SSRF check, not a hostname the client resolves again
rule_id: SEC-12
domain: security
triggers: ['InetAddress[.]getByName\(|getAllByName\(', 'isSiteLocalAddress\(|isLoopbackAddress\(|isLinkLocalAddress\(|isAnyLocalAddress\(', '(?i)allow(ed)?[_ ]?hosts?|host[_ ]?allow', '[.]getHost\(\)', '(?i)resolve[rd]?\b', 'DnsResolver|AddressResolver|Dns\b']
scope: file
check_kind: semantic
severity_default: major
---

# The address a server-side request connects to is the address that passed the SSRF check, not a hostname the client resolves again

## Thesis
When a destination check resolves a hostname and validates the resulting addresses, the request that follows is sent to a validated address — the client is given a resolver that returns only the validated set, or is built to connect to that `InetAddress` — rather than handed the hostname to resolve on its own. A check on `InetAddress.getByName(host)` followed by `client.get("https://" + host + ...)` is the defect.

## Rationale
A name is resolved at least twice in that pattern: once by the check and once by the HTTP client when it connects. An attacker who controls the name's DNS returns a public address to the first lookup and an internal one (`169.254.169.254`, `127.0.0.1`) to the second whenever the client's lookup is not served from the same cache as the check's — a client with its own resolver, or a JDK lookup after the cached entry has expired — so the check passes and the connection goes inside; the JDK caches a successful lookup for its own implementation-specific period (`networkaddress.cache.ttl`), not for the record's TTL, which narrows the window but does not remove the gap. A domain allowlist alone has the same weakness, because an allowed name can be pointed at an internal address. Validating every A and AAAA record the name resolves to, then connecting to a validated address, closes the gap for that request; resolving only through a resolver that never answers internal addresses is the alternative. A redirect target is a fresh name and takes the same check.

## Example
```java
bad:  if (isInternal(InetAddress.getByName(host))) throw new IllegalArgumentException();
      rest.getForObject("https://" + host + path, String.class);        // client resolves host again
good: InetAddress[] resolved = InetAddress.getAllByName(host);
      for (InetAddress a : resolved) if (isInternal(a)) throw new IllegalArgumentException();
      DnsResolver pinned = new SystemDefaultDnsResolver() {                     // answers the validated set for host
          @Override public InetAddress[] resolve(String h) throws UnknownHostException { return h.equals(host) ? resolved : super.resolve(h); } };
      HttpClient c = HttpClients.custom().setConnectionManager(
          PoolingHttpClientConnectionManagerBuilder.create().setDnsResolver(pinned).build()).build();
```

## Limits
Applies to a check that validates addresses and a client that connects by name afterwards. A client whose destinations are fixed configuration needs no pinning. A resolver in front of the client that answers only from an internal DNS which never returns internal addresses for external names, documented in the project context, is the alternative form and rejects the finding. A check that validates the name against an allowlist of the organization's own hosts, whose DNS the organization controls, is a project tolerance to state.

## Validator
On the triggered hunk find each resolution-and-check of a host, then find the client call that follows in the same flow in the file. Determine what the client receives: the hostname string, or the validated address or a pinned resolver. Validator question: **does the client resolve the name a second time after the check, so that a different answer would reach an unchecked address?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: SEC-12`, severity major, `file`, `symbol`, `code` = the check and the client call quoted verbatim from the diff, `fix` = the client pinned to the validated addresses, `rationale` naming the second resolution and the address it can return).

## Source
OWASP Server-Side Request Forgery Prevention Cheat Sheet, §Domain name — a domain allowlist "is still vulnerable to the DNS pinning bypass... a DNS resolution will be made when the business code will be executed", with the internal-resolver and monitoring mitigations; Case 2, step 2 — "retrieve all the IP addresses behind the domain name provided (taking records A + AAAA for IPv4 + IPv6) and... apply the same verification" as for IP addresses; step 7 — build the request "using only validated information". `java.net.InetAddress` Javadoc, Java SE 21, "InetAddress Caching" — successful lookups cached "for a finite (implementation dependent) period of time". CWE-918.

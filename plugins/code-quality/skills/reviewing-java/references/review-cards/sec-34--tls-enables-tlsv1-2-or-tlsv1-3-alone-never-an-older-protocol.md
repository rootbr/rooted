---
title: TLS protocol selection enables TLSv1.2 or TLSv1.3 alone; SSLv3, TLSv1 and TLSv1.1 are never enabled or re-enabled
rule_id: SEC-34
domain: security
triggers: ['SSLContext[.]getInstance\(', 'setEnabledProtocols\(', 'setProtocols\(', '"TLSv1([.]1)?"', '"SSL(v[23])?"', 'jdk[.]tls[.]disabledAlgorithms', 'Security[.]setProperty\(']
scope: hunk
check_kind: mechanical
severity_default: major
---

# TLS protocol selection enables TLSv1.2 or TLSv1.3 alone; SSLv3, TLSv1 and TLSv1.1 are never enabled or re-enabled

## Thesis
Where the diff selects TLS protocol versions — `SSLContext.getInstance(protocol)`, `SSLSocket`/`SSLEngine.setEnabledProtocols`, `SSLParameters.setProtocols`, an HTTP client's TLS settings, or a write to the `jdk.tls.disabledAlgorithms` security property — the enabled set is `TLSv1.3`, with `TLSv1.2` at most; `SSLv2`, `SSLv3`, `TLSv1` and `TLSv1.1` are neither named as enabled nor removed from the disabled list.

## Rationale
TLS 1.0 and 1.1 are formally deprecated and must be disabled, and SSLv2 and SSLv3 must always be disabled: their handshakes and cipher suites carry known cryptographic weaknesses that let a network attacker downgrade or decrypt the session. The JDK enforces this by default — `jdk.tls.disabledAlgorithms` in `java.security` lists `SSLv3, TLSv1, TLSv1.1` — so a client or server that inherits the defaults negotiates 1.2 and 1.3 only. `setEnabledProtocols` replaces that set ("only protocols listed in the protocols parameter are enabled for use"), a context created for `TLSv1` enables that version, and `Security.setProperty("jdk.tls.disabledAlgorithms", …)` rewrites the default for the whole JVM, so one added line re-opens the downgrade for every connection it governs.

## Example
```java
bad:  SSLContext ctx = SSLContext.getInstance("TLSv1");
      socket.setEnabledProtocols(new String[] {"TLSv1", "TLSv1.1", "TLSv1.2"});
      Security.setProperty("jdk.tls.disabledAlgorithms", "");
good: SSLContext ctx = SSLContext.getInstance("TLSv1.3");
      socket.setEnabledProtocols(new String[] {"TLSv1.3", "TLSv1.2"});
```

## Limits
Applies to the protocol set. `SSLContext.getInstance("TLS")`, `"TLSv1.2"` or `"TLSv1.3"` is not flagged: a `TLS` context enables what the security properties allow. An `HttpURLConnection`, `HttpClient` or framework client built without explicit protocol settings inherits the JDK 21 defaults and is not flagged; pinning the version explicitly is hardening, not a finding. A project context that names a legacy peer able to speak only TLS 1.1 rejects the finding for that one connection.

## Validator
On the triggered hunk read each protocol name string or array and each write to `jdk.tls.disabledAlgorithms`. Flag `SSLv2`, `SSLv3`, `TLSv1` or `TLSv1.1` in an enable list or as a context name, and any property edit that drops them from the disabled list or empties it. Validator question: **does this line enable, or stop disabling, a protocol older than TLSv1.2?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: SEC-34`, severity major, `file`, `symbol`, `code` = the protocol selection quoted verbatim from the diff, `fix` = the same call naming `TLSv1.3` and `TLSv1.2` only, `rationale` naming the old version and the downgrade it permits).

## Source
OWASP Transport Layer Security Cheat Sheet, "Only Support Strong Protocols" — "TLS 1.0 and TLS 1.1 are formally deprecated by RFC 8996 (March 2021) and must be disabled… SSLv2 and SSLv3 must always be disabled". OWASP ASVS 5.0 §12.1.1 — only the latest recommended TLS versions enabled, such as TLS 1.2 and 1.3. JDK 21 `conf/security/java.security` — `jdk.tls.disabledAlgorithms=SSLv3, TLSv1, TLSv1.1, DTLSv1.0, RC4, DES, …`. `javax.net.ssl.SSLSocket#setEnabledProtocols` Javadoc, Java SE 21 — "only protocols listed in the protocols parameter are enabled for use". RFC 8996 and NIST SP 800-52 Rev. 2 §3.1 — by number.

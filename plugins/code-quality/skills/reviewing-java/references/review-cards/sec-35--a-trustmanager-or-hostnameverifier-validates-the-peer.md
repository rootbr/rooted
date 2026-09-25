---
title: A TrustManager or HostnameVerifier validates the peer; a checkServerTrusted that returns without checking or a verify that returns true is never installed
rule_id: SEC-35
domain: security
triggers: ['X509TrustManager', 'X509ExtendedTrustManager', 'checkServerTrusted\(', 'HostnameVerifier', 'setDefaultHostnameVerifier\(', 'NoopHostnameVerifier', 'TrustAllStrategy', 'TrustSelfSignedStrategy', 'getAcceptedIssuers\(']
scope: file
check_kind: mechanical
severity_default: critical
---

# A TrustManager or HostnameVerifier validates the peer; a checkServerTrusted that returns without checking or a verify that returns true is never installed

## Thesis
An `X509TrustManager` installed into an `SSLContext`, and a `HostnameVerifier` installed on a connection or client, each performs the check its interface exists for: `checkServerTrusted` builds a certificate path from the peer's chain to a trusted root and throws `CertificateException` otherwise, and `verify` returns `true` only for a host name that matches the server's certificate; a manager with an empty body, a verifier of the form `(h, s) -> true`, or a library "trust all" strategy is not installed outside test sources.

## Rationale
TLS authenticates the server through its certificate chain; the trust manager is the component that decides whether that chain leads to a trusted authority, and the hostname verifier whether the certificate was issued for the host being contacted. A manager that returns without checking accepts any certificate, including one an attacker on the path mints on the spot, so the connection is encrypted to whoever answers; a verifier that returns `true` accepts a valid certificate for a different name, which any holder of any certificate can present. Either way the client sends its credentials and data to an impersonator and TLS provides no authentication of the peer.

## Example
```java
bad:  TrustManager tm = new X509TrustManager() {
          public void checkServerTrusted(X509Certificate[] c, String a) {}
          public void checkClientTrusted(X509Certificate[] c, String a) {}
          public X509Certificate[] getAcceptedIssuers() { return new X509Certificate[0]; } };
      HttpsURLConnection.setDefaultHostnameVerifier((h, s) -> true);
good: SSLContext ctx = SSLContext.getDefault();                  // platform trust store
      HttpClient client = HttpClient.newBuilder().sslContext(ctx).build();
```

## Limits
Applies to production code paths. A self-signed or internal CA is handled by a `TrustManagerFactory` initialised with a `KeyStore` holding that CA, or by a certificate pin, both of which still validate the chain; that form is correct. A trust-all manager or verifier confined to a test source set, or behind a flag the project context documents as development-only, is out of scope. A custom manager that delegates to the default manager and adds a check (revocation, pinning) is correct when the delegate call is present.

## Validator
On the triggered hunk read the body of each `checkServerTrusted`, `checkClientTrusted` and `verify`, and each trust strategy or verifier passed to a client builder. Flag an empty or log-only body, an unconditional `return true`, `getAcceptedIssuers` returning an empty array beside such a body, and `NoopHostnameVerifier` or `TrustAllStrategy`. Open the file to confirm the object is installed into an `SSLContext`, an `HttpClient`, an `HttpsURLConnection` or a framework client used outside tests. Validator question: **does this manager or verifier accept a peer it has not validated?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: SEC-35`, severity critical, `file`, `symbol`, `code` = the manager or verifier body quoted verbatim from the diff, `fix` = the default `SSLContext` or a `TrustManagerFactory` over a keystore holding the intended CA, `rationale` naming the check that is skipped and the impersonation it allows).

## Source
`javax.net.ssl.X509TrustManager#checkServerTrusted` Javadoc, Java SE 21 — "Given the partial or complete certificate chain provided by the peer, build a certificate path to a trusted root and return if it can be validated and is trusted for server SSL authentication"; "@throws CertificateException if the certificate chain is not trusted by this TrustManager". `javax.net.ssl.HostnameVerifier#verify` — "Verify that the host name is an acceptable match with the server's authentication scheme"; "@return true if the host name is acceptable". OWASP ASVS 5.0 §12.3.2 — TLS clients validate certificates before communicating; §12.3.4 — internal or self-signed certificates trusted only for specific CAs or specific certificates. CWE-295 — by id.

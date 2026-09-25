---
title: An environment-specific value such as a URL, host, port, credential, timeout or feature switch is read from configuration, not written as a literal in Java
rule_id: MNT-36
domain: maintainability
triggers: ['"https?://', '"jdbc:', '"(localhost|127[.]0[.]0[.]1)', '"[\w.-]+[.](com|io|net|org|internal|local)(:\d+)?/?', 'Duration[.]of\w+\(\d+\)', 'static final (boolean|String|int) (ENABLE|FEATURE|FLAG|USE_)\w*']
scope: hunk
check_kind: mechanical
severity_default: minor
---

# An environment-specific value such as a URL, host, port, credential, timeout or feature switch is read from configuration, not written as a literal in Java

## Thesis
A value that differs between environments or deployments — a service URL or host, a port, a database name, a credential, a queue name, a timeout, a retry count, a feature switch — is bound from external configuration (`@ConfigurationProperties`, `@Value("${…}")`, the `Environment`) and not written as a string or numeric literal in a Java source file; a literal appears only as the declared default of such a property.

## Rationale
The same application code runs in several environments only if the values that differ are outside it: a literal URL means a rebuild to point at staging, a literal timeout means a code change to tune production, and a literal feature switch means a deploy to flip it. Spring Boot resolves property sources — files, environment variables, command-line arguments — in a defined override order precisely so that the code stays the same and the value comes from the environment. A credential in source is also a secret in version control, which is a security matter of its own.

## Example
```java
bad:  private final String paymentsUrl = "https://payments.internal:8443/v1";
      private static final Duration TIMEOUT = Duration.ofSeconds(5);
good: @ConfigurationProperties("payments") record PaymentsProperties(URI url, Duration timeout) {}
      PaymentClient(PaymentsProperties props) { this.url = props.url(); this.timeout = props.timeout(); }
```

## Limits
A protocol constant, a public well-known URL that never changes (a schema namespace), a test's literal endpoint against a test container or a mock server, a default value declared in a properties class, and a `@Bean` that reads from properties are correct. A constant the project context declares fixed by contract is out of scope. Whether a secret sits in `application.yml` is not visible in a Java diff.

## Validator
On the triggered hunk find each string or numeric literal that names a host, URL, port, credential, queue, timeout, limit or switch. Read the surrounding code to see whether it is a property default or a live value. Validator question: **would this literal have to change to run the same code in another environment or to tune it in production?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: MNT-36`, severity minor, `file`, `symbol`, `code` = the literal quoted verbatim from the diff, `fix` = the property binding, `rationale` naming the rebuild the literal forces).

## Source
Spring Boot reference, Core Features → Externalized Configuration — "Spring Boot lets you externalize your configuration so that you can work with the same application code in different environments. You can use a variety of external configuration sources including Java properties files, YAML files, environment variables, and command-line arguments. Property values can be injected directly into your beans by using the @Value annotation, accessed through Spring's Environment abstraction, or be bound to structured objects through @ConfigurationProperties"; the property-source order is "designed to allow sensible overriding of values".

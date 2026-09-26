---
title: A @ConfigurationProperties class is @Validated with constraints on its required fields, and a required property has no empty placeholder default that hides its absence
rule_id: MNT-37
domain: maintainability
triggers: ['@ConfigurationProperties', '@Validated', '@Value\("\$\{[^}]*:\s*\}"\)', '@Value\("\$\{', '@(NotNull|NotBlank|NotEmpty|Min|Max|Positive)\b']
scope: file
check_kind: mechanical
severity_default: minor
---

# A @ConfigurationProperties class is @Validated with constraints on its required fields, and a required property has no empty placeholder default that hides its absence

## Thesis
A `@ConfigurationProperties` class carries `@Validated` and Jakarta Bean Validation constraints (`@NotNull`, `@NotBlank`, `@Min`, `@Positive`, `@Valid` on nested objects) on every property the application cannot run without, so that a missing or invalid value fails the application at startup with the property's name; a required `@Value("${key}")` has no default, and in particular no empty default (`${key:}`) that lets the application start with a blank URL or credential and fail later.

## Rationale
Configuration is read at startup, and startup is the one moment when a wrong value can be reported next to its source with nothing else affected; an unvalidated property surfaces instead as a `NullPointerException` in a request, a connection refused to `null:0`, or a silent misbehaviour hours later. Spring Boot validates `@ConfigurationProperties` classes whenever they are annotated with `@Validated`, using the constraint annotations on the fields, and its default placeholder configurer fails initialization when a `${}` placeholder cannot be resolved; an empty default converts that failure into a legal-looking blank.

## Example
```java
bad:  @ConfigurationProperties("mail") record MailProperties(String host, int port) {}
      @Value("${mail.host:}") String host;
good: @Validated @ConfigurationProperties("mail")
      record MailProperties(@NotBlank String host, @Min(1) @Max(65535) int port) {}
      @Value("${mail.host}") String host;
```

## Limits
A genuinely optional property declares a meaningful default (`${mail.port:25}`, a default in the properties class) and needs no constraint. A properties class validated through a `@Bean` method annotated `@Validated`, or a project that validates configuration in a startup check the project context names, satisfies the rule. A project without a Bean Validation implementation on the classpath has no `@Validated` support; the finding then asks for the dependency.

## Validator
On the triggered hunk find each `@ConfigurationProperties` class and each `@Value` placeholder. For the class, open the file and check for `@Validated` and for constraints on the fields the code treats as required (dereferenced without a null check, used to connect). For the placeholder, check for an empty or blank default. Validator question: **can a required property be absent or invalid without failing startup with its name?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: MNT-37`, severity minor, `file`, `symbol`, `code` = the properties class header or the placeholder quoted verbatim from the diff, `fix` = `@Validated` with the constraints, or the placeholder without an empty default, `rationale` naming the later failure that startup validation would have reported).

## Source
Spring Boot reference, Externalized Configuration → Type-safe Configuration Properties → "@ConfigurationProperties Validation" — "Spring Boot attempts to validate @ConfigurationProperties classes whenever they are annotated with Spring's @Validated annotation. You can use JSR-303 jakarta.validation constraint annotations directly on your configuration class … add constraint annotations to your fields"; also triggered by `@Validated` on the `@Bean` method; "Property Placeholders" — "${name:default}" syntax. Spring Framework reference, Using @Value — a `PropertySourcesPlaceholderConfigurer` "ensures Spring initialization failure if any ${} placeholder could not be resolved", and "Spring Boot configures by default a PropertySourcesPlaceholderConfigurer bean".

---
title: Jackson polymorphic typing never lets the JSON name the class; default typing and Id.CLASS require a PolymorphicTypeValidator allowlist, and Id.NAME with @JsonSubTypes is the form
rule_id: SEC-38
domain: security
triggers: ['enableDefaultTyping\(', 'activateDefaultTyping\(', 'Id[.]CLASS', 'Id[.]MINIMAL_CLASS', '@JsonTypeInfo', 'PolymorphicTypeValidator', 'LaissezFaireSubTypeValidator', 'allowIf(Sub|Base)Type\(Object[.]class\)', 'DefaultTyping[.]']
scope: file
check_kind: mechanical
severity_default: critical
---

# Jackson polymorphic typing never lets the JSON name the class; default typing and Id.CLASS require a PolymorphicTypeValidator allowlist, and Id.NAME with @JsonSubTypes is the form

## Thesis
Polymorphic deserialization in Jackson is declared with `@JsonTypeInfo(use = Id.NAME)` and an explicit `@JsonSubTypes` list, so the discriminator selects among named application types only. `ObjectMapper.enableDefaultTyping()` is absent. `activateDefaultTyping` and `@JsonTypeInfo(use = Id.CLASS)` or `Id.MINIMAL_CLASS` appear only with a `BasicPolymorphicTypeValidator` that allows specific base types or subtypes, never `Object.class`, and for the annotation form that validator is registered on the mapper with `setPolymorphicTypeValidator` (or the builder's `polymorphicTypeValidator`), because the one passed to `activateDefaultTyping` does not apply to annotated types.

## Rationale
With default typing or a class-name discriminator the incoming JSON names the Java class to instantiate, and Jackson creates it and calls its setters; classes in common libraries have setters that open connections, load classes or run code, so an untrusted document becomes remote code execution. The default `ObjectMapper` is not affected: the attack requires the developer to enable default typing or an equivalent annotation with a base type of `Object`. From Jackson 2.10 the unsafe methods are deprecated with a documented security warning and the safe form requires an allowlist — the validator decides which subtypes may be instantiated — and the validator given to `activateDefaultTyping` governs default typing only; annotation-based polymorphism uses the validator set on the mapper.

## Example
```java
bad:  ObjectMapper om = new ObjectMapper().enableDefaultTyping();
      @JsonTypeInfo(use = JsonTypeInfo.Id.CLASS) abstract class Event {}
good: @JsonTypeInfo(use = JsonTypeInfo.Id.NAME, property = "type")
      @JsonSubTypes({ @Type(value = Created.class, name = "created"),
                      @Type(value = Closed.class, name = "closed") })
      abstract class Event {}
```

## Limits
Applies to a mapper that reads content from outside the process. A mapper that reads only the application's own trusted files, named in the project context, lowers the severity, but the deprecated method remains a finding. `activateDefaultTyping(ptv, …)` with a validator whose `allowIfBaseType` and `allowIfSubType` name a specific application package or class is accepted; `allowIfSubType(Object.class)`, `allowIfBaseType(Object.class)` or `LaissezFaireSubTypeValidator` is not. `@JsonTypeInfo(use = Id.NAME)` needs no validator. A `Map<String, Object>` or `Object` target is safe with a default mapper and unsafe once default typing is on.

## Validator
On the triggered hunk find each `enableDefaultTyping`, `activateDefaultTyping`, `@JsonTypeInfo` with `Id.CLASS` or `Id.MINIMAL_CLASS`, and each validator construction. Open the file: for default typing read the validator's allow rules; for a class-name annotation find `setPolymorphicTypeValidator` or the builder's `polymorphicTypeValidator` on the mapper that reads the type, and read its rules. Validator question: **can a JSON document name a class outside an explicit allowlist and have it instantiated?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: SEC-38`, severity critical, `file`, `symbol`, `code` = the default-typing call or the annotation quoted verbatim from the diff, `fix` = `Id.NAME` with `@JsonSubTypes`, or a `BasicPolymorphicTypeValidator` naming the allowed types and registered where the form requires, `rationale` naming the class-selection path and the gadget instantiation it allows).

## Source
`com.fasterxml.jackson.databind.ObjectMapper` Javadoc, 2.19 — `enableDefaultTyping()`: "@deprecated Since 2.10 use activateDefaultTyping(PolymorphicTypeValidator) instead"; `activateDefaultTyping(PolymorphicTypeValidator)`: "choice of PolymorphicTypeValidator to pass is critical for security as allowing all subtypes can be risky for untrusted content"; `setPolymorphicTypeValidator`: the validator "for validating polymorphic subtypes used with explicit polymorphic types (annotation-based), but NOT one with 'default typing'". FasterXML Jackson wiki, "Jackson Polymorphic Deserialization CVE Criteria" — the problem requires untrusted JSON, "Default Typing" (or an equivalent `@JsonTypeInfo` with base type `java.lang.Object`) and a gadget library; 2.10 added "Safe Default Typing" with an allow-list and deprecated the unsafe methods. OWASP Deserialization Cheat Sheet — jackson-databind "can be used safely as long as polymorphism is not used". OWASP ASVS 5.0 §1.5.2. CWE-502 — by id.

---
title: A class that implements Serializable declares an explicit private static final long serialVersionUID
rule_id: JAVA-157
domain: interface
step: [implement]
applies_to: [java, object-oriented]
triggers: ['implements .*Serializable', 'extends .*Exception', 'extends .*Throwable', 'serialVersionUID']
scope: file
check_kind: mechanical
severity_default: minor
---

# A class that implements Serializable declares an explicit private static final long serialVersionUID

## Thesis
Every non-enum class that is `Serializable` — directly, through a superclass such as `Exception`, or through an interface — declares `private static final long serialVersionUID`, and the value changes only when the author intends old serialized instances to stop deserializing.

## Rationale
Deserialization compares the stream's `serialVersionUID` with the receiving class's; a mismatch throws `InvalidClassException`. When the class declares none, the runtime computes one from the class's members and structure, a computation "highly sensitive to class details that may vary depending on compiler implementations": adding a method, a synthetic field from an inner class or a lambda, or building with another compiler changes the value while the data format did not, so an HTTP session, a cache entry, a message or a file written by the previous build fails to read after a deploy with no code-level reason. An explicit value pins compatibility to the author's decision.

## Example
```java
bad:  public class OrderNotFoundException extends RuntimeException {
          public OrderNotFoundException(long id) { super("order " + id); }
      }
good: public class OrderNotFoundException extends RuntimeException {
          private static final long serialVersionUID = 1L;
          public OrderNotFoundException(long id) { super("order " + id); }
      }
```

## Limits
Enum types have a fixed `serialVersionUID` of 0 and are excluded. A project context stating that Java serialization is never used across builds — no session replication, no serialized caches or messages, exceptions never serialized — lowers the finding to a suggestion. A `record` that is serialized uses its components and needs no declared value for compatibility of the format, though one may be declared.

## Validator
On the triggered hunk find each class that is or becomes `Serializable` (including subclasses of `Exception`, `Throwable`, or a serializable base). Open the file and check for a `static final long serialVersionUID` declaration. Validator question: **is this serializable class without an explicit serialVersionUID?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: JAVA-157`, severity minor, `file`, `symbol`, `code` = the class declaration quoted verbatim from the diff, `fix` = `private static final long serialVersionUID = 1L;`, `rationale` naming the `InvalidClassException` a recompilation can cause).

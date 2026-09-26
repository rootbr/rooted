---
title: An ObjectInputStream that reads untrusted data has an ObjectInputFilter with a class allowlist and graph limits set before readObject
rule_id: SEC-37
domain: security
triggers: ['new ObjectInputStream\(', 'readObject\(', 'readUnshared\(', 'ObjectInputFilter', 'resolveClass\(', 'SerializationUtils[.]deserialize\(', 'jdk[.]serialFilter']
scope: file
check_kind: mechanical
severity_default: critical
---

# An ObjectInputStream that reads untrusted data has an ObjectInputFilter with a class allowlist and graph limits set before readObject

## Thesis
Every `ObjectInputStream` whose bytes come from a network, a client, a message broker, a cache another process writes, or a file the application did not produce itself is given an `ObjectInputFilter` — through `setObjectInputFilter` on the stream before the first `readObject`, through `ObjectInputFilter.Config.setSerialFilter` or the `jdk.serialFilter` property at startup, or through a filter factory — whose pattern allows the expected classes by name and rejects everything else (`!*`), with `maxdepth`, `maxarray`, `maxrefs` and `maxbytes` limits.

## Rationale
Java deserialization instantiates whatever classes the stream names and runs their `readObject`, `readResolve` and related methods before the caller sees the result; with common libraries on the classpath, chains of such classes turn an incoming byte stream into code execution, and a deeply nested or huge graph exhausts memory before any application check runs. A serial filter is consulted for every class, array length, reference count, depth and byte count as the stream is read, so a class outside the allowlist or a graph beyond the limits is rejected before it is instantiated. The JDK documents deserialization of untrusted data as "inherently dangerous" and the filter as the defensive mechanism; a filter set after an object has been read is refused, and a filter set on a different stream protects nothing.

## Example
```java
bad:  try (ObjectInputStream in = new ObjectInputStream(request.getInputStream())) {
          Order o = (Order) in.readObject();
      }
good: try (ObjectInputStream in = new ObjectInputStream(request.getInputStream())) {
          in.setObjectInputFilter(ObjectInputFilter.Config.createFilter(
              "com.example.order.*;java.base/*;!*;maxdepth=8;maxarray=10000;maxbytes=1048576"));
          Order o = (Order) in.readObject();
      }
```

## Limits
Applies to streams over data from outside the process's trust boundary. A stream over bytes the same application wrote and stored where nothing else can write — a local checkpoint, a blob whose signature is verified before reading — is lower risk and may rely on the JVM-wide filter alone. A JVM-wide filter or a filter factory installed in the application's startup code or launch flags and named in the project context satisfies the rule for every stream it covers, provided its pattern ends in `!*` (a filter that allows `*` is no filter). Overriding `resolveClass` to reject every class not on a list is an older form of the same control and is accepted when the override throws for unexpected classes. Replacing Java serialization with JSON or protobuf at the boundary removes the finding.

## Validator
On the triggered hunk find each `ObjectInputStream` construction, `readObject`/`readUnshared` call, or helper that wraps one. Open the file: locate a `setObjectInputFilter` on the same stream before the first read, a `Config.setSerialFilter` or filter factory in startup code, or a `resolveClass` override, and read the pattern — an allowlist ending in `!*` with limits passes, a missing filter or a pattern that admits `*` fails. Decide whether the bytes come from outside the process. Validator question: **can bytes from outside the trust boundary reach `readObject` with no filter that rejects unexpected classes?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: SEC-37`, severity critical, `file`, `symbol`, `code` = the stream construction and the `readObject` call quoted verbatim from the diff, `fix` = the `setObjectInputFilter` call with an allowlist pattern and limits placed before the read, `rationale` naming the untrusted source and the code execution or memory exhaustion an unfiltered stream permits).

## Source
`java.io.ObjectInputFilter` class Javadoc, Java SE 21 — "Warning: Deserialization of untrusted data is inherently dangerous and should be avoided"; "For each context and use case, developers should construct and apply an appropriate filter"; the JVM-wide filter via `jdk.serialFilter` or `Config.setSerialFilter`, the filter factory, the pattern form `"example.*;java.base/*;!*"`, and the limits `maxdepth`, `maxrefs`, `maxbytes`, `maxarray`. `java.io.ObjectInputStream#setObjectInputFilter` — the filter is invoked for each class, array, proxy and replacement object; `IllegalStateException` "if an object has been read". OWASP Deserialization Cheat Sheet, "Java" — restrict resolvable classes before `readObject` (look-ahead `resolveClass`) and check input length and object count. OWASP ASVS 5.0 §1.5.2 — deserialization of untrusted data enforces an allowlist of object types. JEP 290, JEP 415, SEI CERT SER12-J and CWE-502 — by id.

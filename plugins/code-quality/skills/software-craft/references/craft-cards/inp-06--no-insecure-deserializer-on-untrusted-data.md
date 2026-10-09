---
title: Data that may come from an untrusted source is not deserialized with a mechanism its documentation defines as insecure, such as native object serialization that can construct arbitrary objects or run code
rule_id: INP-06
domain: input
step: [implement, review]
applies_to: [universal]
triggers: ['\b(c?[Pp]ickle|dill|cloudpickle|joblib)[.]loads?\(|\bshelve[.]open\(|\bjsonpickle[.]decode\(|\bmarshal[.]loads?\(', '\byaml[.](unsafe_)?load(_all)?\(|\bLoader\s*=\s*yaml[.](Unsafe|Full)?Loader\b', '\bObjectInputStream\b|[.]readObject\(\)|\bXMLDecoder\b|\benableDefaultTyping\(|\bactivateDefaultTyping\(', '\bBinaryFormatter\b|\bnode-serialize\b|\bunserialize\(', '\b(access|from_bytes)_unchecked(_mut)?\b|\barchived_(root|value)(_mut)?\b']
scope: hunk
check_kind: mechanical
severity_default: major
---

# Data that may come from an untrusted source is not deserialized with a mechanism its documentation defines as insecure, such as native object serialization that can construct arbitrary objects or run code

## Thesis
Data that could have come from an untrusted source or been tampered with is read through a data-only format such as JSON, or through a loader its documentation offers for untrusted input, onto types the code names rather than types the data names. A deserialization mechanism whose documentation defines it as insecure for untrusted input, such as a native object deserializer or a loader that can create arbitrary objects and run code while reading, or an accessor that skips validation, reads only data the program trusts and that could not have been tampered with.

## Rationale
Crafted input to a native object deserializer, or to a loader that builds the objects the data names, can create arbitrary objects, which can then be used to execute arbitrary code during deserialization itself. An accessor that skips validation does not check that the bytes are valid to access, and bytes from a potentially malicious source should always be validated before access. Untrusted serialized data is input so complex that validation can only minimally protect the application: the only safe architectural pattern is to accept no serialized objects from untrusted sources, or to deserialize in limited capacity for only simple data types, using an easier-to-defend format such as JSON when possible. Deserialization of untrusted data enforces safe input handling, such as an allow-list of object types or a restriction on client-defined object types, and mapping the data onto types the code names is that restriction. A class allow-list or a serialization filter on an insecure mechanism restricts which classes resolve, yet class checks alone do not bound resource consumption, and filtering does not make arbitrary untrusted deserialization safe.

## Example
```rust
bad:  fn quantity(untrusted: &[u8]) -> Result<u32, Error> {
          let order = unsafe { rkyv::access_unchecked::<ArchivedOrder>(untrusted) };
          Ok(order.quantity.to_native())
      }
good: fn quantity(untrusted: &[u8]) -> Result<u32, Error> {
          let order = rkyv::access::<ArchivedOrder, Error>(untrusted)?;
          Ok(order.quantity.to_native())
      }
```

## Limits
Data the program trusts and that could not have been tampered with is outside the rule; signing the data with a secret key and verifying the signature before deserializing is a documented way to ensure that a payload has not been tampered with. Where a loader is offered for untrusted input, the code registers no custom constructor on it that allows arbitrary object creation. The rule reaches every mechanism whose documentation defines it as insecure for untrusted input, in a standard library or a third-party package alike; which data format or parser to adopt is outside it.

## Validator
Grep the hunk for a call to a native object deserializer, a loader that builds the objects the data names, a setting that lets the data name its own types, or an accessor that skips validation. Open the enclosing routine and trace the argument back to where its bytes enter: a request body, a message, an upload, a cookie, a header, a socket, or a file or store another party can write. Look for a signature verified with a secret key on those bytes before the call. Validator question: **Does data that could have come from an untrusted source or been tampered with reach a deserialization mechanism whose documentation defines it as insecure for untrusted input, with no signature verified before the call?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: INP-06`, severity major, `file`, `symbol`, `code` = the deserializing call and the line that hands it the untrusted bytes, verbatim from the diff, `fix` = the same data read through a data-only format or a loader offered for untrusted input, onto a type the code names, in the file's language, `rationale` = names the mechanism, where its bytes come from, and that crafted input can create arbitrary objects and run code or bypass validation).

## Source
- OWASP ASVS 5.0, V1 Encoding and Sanitization, requirement 1.5.2, Level 2 (OWASP/ASVS master 5.0/en/0x10-V1-Encoding-and-Sanitization.md): "Verify that deserialization of untrusted data enforces safe input handling, such as using an allowlist of object types or restricting client-defined object types, to prevent deserialization attacks. Deserialization mechanisms that are explicitly defined as insecure must not be used with untrusted input." (fetched)
- OWASP Deserialization Cheat Sheet (OWASP/CheatSheetSeries master cheatsheets/Deserialization_Cheat_Sheet.md), Python and Java sections: "Unpickling can execute arbitrary code; never unpickle untrusted data."; "override `ObjectInputStream.resolveClass()` to restrict ordinary class resolution during deserialization"; "For untrusted YAML, use `yaml.safe_load()`, and do not register custom constructors that allow arbitrary object creation."; "class checks alone do not bound resource consumption"; "Filtering does not make arbitrary untrusted deserialization safe." (fetched)
- OWASP Top 10 Proactive Controls 2024, C3, 'Special Case: Validate Data During Deserialization' (OWASP/www-project-proactive-controls master docs/the-top-10/c3-validate-input-and-handle-exceptions.md): "Some forms of input are so complex that validation can only minimally protect the application. For example, it's dangerous to deserialize untrusted data or data that can be manipulated by an attacker. The only safe architectural pattern is to not accept serialized objects from untrusted sources or to only deserialize in limited capacity for only simple data types. You should avoid processing serialized data formats and use easier to defend formats such as JSON when possible." (fetched)
- Python documentation, pickle module warning (python/cpython main Doc/library/pickle.rst): "It is possible to construct malicious pickle data which will **execute arbitrary code during unpickling**. Never unpickle data that could have come from an untrusted source, or that could have been tampered with."; "Consider signing data with :mod:`hmac` if you need to ensure that it has not been tampered with." (fetched)
- Ruff S301 suspicious-pickle-usage (astral-sh/ruff main crates/ruff_linter/src/rules/flake8_bandit/rules/suspicious_function_call.rs): "Deserializing untrusted data with `pickle` and other deserialization modules is insecure as it can allow for the creation of arbitrary objects, which can then be used to achieve arbitrary code execution"; "consider signing the data with a secret key and verifying the signature before deserializing the payload" (fetched)
- Ruff S506 unsafe-yaml-load (astral-sh/ruff main crates/ruff_linter/src/rules/flake8_bandit/rules/unsafe_yaml_load.rs): "`yaml.load` allows for the creation of arbitrary Python objects, which can then be used to execute arbitrary code." (fetched)
- rkyv API documentation (rkyv/rkyv main rkyv/src/api/mod.rs), module docs and `access_unchecked`: "bytes from a potentially-malicious source should always be validated prior to access."; "This function does not check that the bytes are valid to access. Use [`access`](high::access) to safely access the buffer using validation."; "Using techniques such as cryptographic signing can provide a more performant way to verify data integrity from trusted sources." (fetched)
- Caveat: the evidence documents named mechanisms of particular ecosystems; the rule reaches another mechanism where its own documentation makes the same statement.

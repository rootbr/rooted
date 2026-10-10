---
title: Data that may come from an untrusted source is not deserialized with a mechanism its documentation defines as insecure, such as native object serialization that can construct arbitrary objects or run code
rule_id: INP-06
domain: input
step: [implement]
applies_to: [universal]
triggers: ['\b(c?[Pp]ickle|dill|cloudpickle|joblib)[.]loads?\(|\bshelve[.]open\(|\bjsonpickle[.]decode\(|\bmarshal[.]loads?\(', '\byaml[.](unsafe_)?load(_all)?\(|\bLoader\s*=\s*yaml[.](Unsafe|Full)?Loader\b', '\bObjectInputStream\b|[.]readObject\(\)|\bXMLDecoder\b|\benableDefaultTyping\(|\bactivateDefaultTyping\(', '\bBinaryFormatter\b|\bnode-serialize\b|\bunserialize\(', '\b(access|from_bytes)_unchecked(_mut)?\b|\barchived_(root|value)(_mut)?\b']
scope: callers
check_kind: semantic
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

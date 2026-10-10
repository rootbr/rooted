---
title: A client that reads another service's responses or events ignores fields it does not know and handles enumeration values it does not know without failing, so that a compatible extension by the provider does not break it
rule_id: ARCH-40
domain: architecture
step: [implement, handle-errors, review]
applies_to: [service-boundary]
triggers: ['FAIL_ON_UNKNOWN_PROPERTIES\s*,\s*true|[.]enable\s*\([^)]*FAIL_ON_UNKNOWN_PROPERTIES|failOnUnknownProperties\s*\(\s*true|fail-on-unknown-properties\s*[=:]\s*true|ignoreUnknown\s*=\s*false', '[.]DisallowUnknownFields\s*\(', 'deny_unknown_fields', 'extra\s*=\s*[\x22\x27]forbid[\x22\x27]|Extra[.]forbid', '[\x22\x27]?additionalProperties[\x22\x27]?\s*:\s*false', '[.]strict\s*\(\s*\)|unknownKeys\s*:\s*[\x22\x27]strict']
scope: callers
check_kind: semantic
severity_default: major
---

# A client that reads another service's responses or events ignores fields it does not know and handles enumeration values it does not know without failing, so that a compatible extension by the provider does not break it

## Thesis
A client that reads another service's responses or events ignores the fields it does not know and raises no error for them, handles a value it does not know in an enumeration the contract leaves open either agnostically or with a default behaviour, and keeps such fields and values in the payload when it passes the object back in a subsequent PUT request. A deserializer, schema or enumeration mapping set to reject unknown fields of an object the provider's contract leaves open, or unknown open-enumeration values, on data another service sends is the finding, and so is a read-modify-write path that rebuilds such an object for a subsequent PUT request from its known fields only.

## Rationale
A provider evolves its data format by adding fields, and a client that ignores the fields it cannot process is what lets it do so: the provider can send extra information this client does not care about without breaking it. Forward compatibility of an event schema is conditional on the reader: consumers read events tagged with the latest schema version using the previous version as long as they follow the robustness principle. For events, compatibility and extensibility issues that happen less frequently with client-server APIs become regular considerations: events are often intermediated by publish/subscribe systems and commonly captured in logs or long-term storage to be read later, so the schemas publishers and consumers use can drift over time, and a consumer may process an event with an older copy of the schema than the one that defined the new fields. A schema-based binary serialization format builds the same behaviour into its parser: when an old binary parses data sent by a new binary, the new fields become unknown fields, which the parser preserves and includes in its serialized output, and it preserves unrecognized enumeration values as well. A limited enumeration type cannot simply implement this. In that format, a language with open enumeration types stores an unknown value as its underlying integer, a language with closed enumeration types represents it by a dedicated case, and either way the value is serialized back with the message.

## Example
```go
bad:  dec := json.NewDecoder(resp.Body)
      dec.DisallowUnknownFields()
      err := dec.Decode(&order)
good: if err := json.NewDecoder(resp.Body).Decode(&order); err != nil {
          return err
      }
      if order.Status != "paid" { // any other status, known or not, is held
          return hold(order)
      }
      return ship(order)
```

## Limits
The direction of the data separates the cases. The tolerance covers what a provider sends, its responses and its events. A server receiving a request is held to the opposite rule: it should not ignore unknown input fields in the payload or URL and should answer with an HTTP 400 error, which signals to the client that those fields would not be stored on its behalf; input-validation practice likewise defines the allowed fields of each object and configures a JSON schema's additional properties explicitly. The same practice reaches data from internal APIs, partner feeds and queues when it crosses a trust boundary; there a client validates every field it uses against its own rules for that field and declares each object open wherever the provider's contract carries no closing declaration. A server that accepts unexpected input fields documents how it handles them for PUT, POST and PATCH requests. Apart from the unknown fields and values it passes back unchanged in a subsequent PUT request, a client stays as strict as it reasonably can with the requests it sends, so that no information leaks silently. The field clause reaches every response or event object whose contract carries no additional-properties declaration, since a client may not read that absence as a closed object. The enumeration clause reaches enumerations the contract leaves open; adding a value to an enumeration whose value list is declared complete is an incompatible change, which the provider aligns with all consumers like any other incompatible change. How a provider versions, evolves and deprecates its contract, and transport mechanics such as retries, timeouts and delivery guarantees, are separate rules.

## Validator
Grep the hunk for a strict reading setting: an unknown-property failure switch turned on, a decoder call that disallows unknown fields, a model or schema option that forbids extra keys, an additional-properties declaration set to false, a strict object-parsing mode. Open the file and the usages of the type, decoder or schema the setting governs, and trace it to its input: an HTTP client's response body or an event or message consumer is data another service sends; a request handler's body, path or query is request data, where strictness is correct; a schema is provider data when this client validates responses or events against it and the provider's own contract carries no closing declaration for that object. In data another service sends, also check each enumeration mapping: a switch or lookup over an open enumeration value whose branch for an unknown value fails or returns an error, a closed enumeration type that represents an open enumeration and rejects an unknown value on decoding, and a read-modify-write path that rebuilds the object for a subsequent PUT request from its known fields only. Validator question: **Does a deserializer, schema or enumeration mapping that reads another service's responses or events reject a field it does not know in an object the provider's contract leaves open, or an unknown value of an open enumeration, or drop unknown fields from an object it passes back in a subsequent PUT request?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: ARCH-40`, severity major, `file`, `symbol`, `code` = the strict reading setting, the failing enumeration branch or the rebuild that drops unknown fields before a PUT request, quoted verbatim from the diff, `fix` = the same read without the strict setting, with a default branch for unknown enumeration values, or with the unknown fields and values carried through to the PUT request, in the file's language, `rationale` = the compatible extension, a new field or a new enumeration value from the provider, that would break this client or that the PUT request would remove from the resource).

---
title: A component whose RPC API and long-term storage both use protocol buffer messages keeps separate message types for the two, and each of its modules handles client messages, storage messages or the translation between them
rule_id: ARCH-19
domain: architecture
step: [design, implement, review]
applies_to: [service-boundary]
triggers: ['(?:[.]|->)(SerializeToString|SerializeAsString|SerializeToArray|toByteArray|toByteString|serializeBinary|encode_to_vec|write_to_bytes)\(|\bproto[.]Marshal\(|\bprotojson[.]Marshal\(|\bMessageToJson\(|\btoBinary\(', '(?i)\b(save|store|put|insert|persist|write|upsert)\w*\(\s*[\w.]*(req|request|resp|response)\b']
scope: callers
check_kind: semantic
severity_default: minor
---

# A component whose RPC API and long-term storage both use protocol buffer messages keeps separate message types for the two, and each of its modules handles client messages, storage messages or the translation between them

## Thesis
A component whose live RPC API and long-term storage both use protocol buffer messages declares separate message types for the two roles, even where the storage types start out largely duplicating the API types. Its code is layered so that each module deals with client messages, with storage messages, or with the translation between them.

## Rationale
Reusing one message type for the API and for long-term storage may seem convenient, since it saves boilerplate and the overhead of converting between messages. The needs of long-term storage and of live RPC services tend to diverge later. Separate types give the freedom to change the storage format without affecting external clients. Maintaining the translation layer has a cost, and it quickly pays off once the component has clients and makes its first storage change.

## Example
```python
bad:  def create_order(request: CreateOrderRequest) -> None:
          store.put(request.order_id, request.SerializeToString())
good: def create_order(request: CreateOrderRequest) -> None:  # client messages
          orders.save(to_record(request))
      def to_record(request: CreateOrderRequest) -> OrderRecord:  # translation
          return OrderRecord(id=request.order_id, customer_id=request.customer_id)
      def save(record: OrderRecord) -> None:  # storage messages
          store.put(record.id, record.SerializeToString())
```

## Limits
The rule reaches a component whose live RPC API and long-term storage both carry protocol buffer messages: a message type declared as a top-level request or response that is also written to long-term storage, and a module outside the translation layer that handles both client and storage messages. A component whose protocol buffer messages serve only one of the two roles is outside it. A message type nested one or more levels inside a top-level request or response is a weaker case, which the protocol buffer API guidance leaves to how closely the component is willing to couple its clients to that message, so the rule asserts only the top-level request and response messages. The evidence speaks of long-term storage, so a record kept only briefly, such as a response cache, is outside what the rule asserts. The evidence concerns protocol buffer messages; a component that uses another schema language for both roles is outside what the rule asserts.

## Validator
Grep the hunk for serialization calls on protocol buffer messages and for save, store, put or insert calls whose argument is a request or response object. Open the callers at scope: the RPC handlers that receive or return the message, and the persistence code that writes or reads it. Trace the type of each value written to long-term storage back to the message types declared as a top-level RPC request or response. Check whether a module outside the translation layer reads or builds both client messages and storage messages. Validator question: **Is a message type declared as a top-level request or response of the component's live RPC API also written to its long-term storage, or does a module outside the translation layer read or build both client and storage messages?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: ARCH-19`, severity minor, `file`, `symbol`, `code` = the message declaration or the storage write that carries a top-level API request or response message, or the line where a module outside the translation layer reads or builds a storage message beside a client message, quoted verbatim from the diff, `fix` = a storage message type of its own and a translation function between it and the API message, or the conversion moved into a translation module, in the file's language, `rationale` = the needs of long-term storage and live RPC services tend to diverge, and separate types let the storage format change without affecting external clients).

## Source
- Protocol Buffers documentation, Proto Best Practices, § Do Use Different Messages For RPC APIs and Storage (#separate-types-for-storage), protocolbuffers/protocolbuffers.github.io content/best-practices/dos-donts.md (fetched): "Reusing the same messages for APIs and long-term storage may seem convenient, reducing boilerplate and overhead of conversion between messages. However, the needs of long-term storage and live RPC services tend to later diverge. Using separate types even if they are largely duplicative initially gives freedom to change your storage format without impacting your external clients. Layer your code so that modules deal either with client protos, storage protos, or translation. There is a cost in maintaining the translation layer, but it quickly pays off once you have clients and have to do your first storage changes."
- Protocol Buffers documentation, API Best Practices, section on separate wire and storage messages, https://protobuf.dev/best-practices/api (relayed, search summary): "The page says the case for separating storage and wire protos is weaker for protos nested one or more levels inside a top-level request or response. Whether to separate them depends on how tightly you're willing to couple clients to those nested protos."
- Caveat: the guidance is written for protocol buffer messages and gives no figure for the cost or the payoff of the translation layer.

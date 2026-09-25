---
title: A gRPC server or channel keeps maxInboundMessageSize bounded; Integer.MAX_VALUE removes the 4 MiB default protection
rule_id: SEC-39
domain: security
triggers: ['maxInboundMessageSize\(', 'maxInboundMetadataSize\(', 'ServerBuilder[.]forPort\(', 'NettyServerBuilder', 'ManagedChannelBuilder', 'Grpc[.]newChannelBuilder']
scope: hunk
check_kind: mechanical
severity_default: major
---

# A gRPC server or channel keeps maxInboundMessageSize bounded; Integer.MAX_VALUE removes the 4 MiB default protection

## Thesis
A gRPC `ServerBuilder`, `NettyServerBuilder`, `ManagedChannelBuilder` or `Grpc.newChannelBuilder` either leaves `maxInboundMessageSize` at its 4 MiB default or sets it to the size of the largest legitimate message plus headroom; it never sets `Integer.MAX_VALUE` or a value chosen to make a size error go away, and the same holds for `maxInboundMetadataSize`.

## Rationale
gRPC buffers an inbound message before handing it to the service, so this limit bounds what one remote message can make the process allocate. The 4 MiB default "provides protection to servers who haven't considered the possibility of receiving large messages"; raising it to the integer maximum lets any client, authenticated or not, make the server allocate up to 2 GiB per message per stream and take the process down with a handful of connections. A limit sized to the real payload keeps a large message a failure of the offending call rather than an out-of-memory error for every caller.

## Example
```java
bad:  Server s = ServerBuilder.forPort(port)
          .maxInboundMessageSize(Integer.MAX_VALUE)
          .addService(svc).build();
good: Server s = ServerBuilder.forPort(port)
          .maxInboundMessageSize(16 * 1024 * 1024)     // largest upload plus headroom
          .addService(svc).build();
```

## Limits
Applies to servers and channels reachable by another process. An in-process transport does not enforce the limit and is out of scope. A larger bound is correct when the project context states the payload size; a transfer of large content is better served by client streaming in small chunks than by a large limit. The default is not flagged.

## Validator
On the triggered hunk read the argument of each `maxInboundMessageSize` and `maxInboundMetadataSize` call. Flag `Integer.MAX_VALUE`, a value above what the project context or a nearby comment justifies, or a constant with no stated relation to a real message size. Validator question: **does this builder allow a single inbound message far larger than any legitimate payload?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: SEC-39`, severity major, `file`, `symbol`, `code` = the builder call quoted verbatim from the diff, `fix` = the same call with a bound sized to the largest legitimate message, `rationale` naming the per-message allocation a remote client can force).

## Source
`io.grpc.ServerBuilder#maxInboundMessageSize` Javadoc — "Sets the maximum message size allowed to be received on the server. If not called, defaults to 4 MiB. The default provides protection to servers who haven't considered the possibility of receiving large messages while trying to be large enough to not be hit in normal usage"; "This method is advisory… the only known transport to not enforce this is InProcessServer". `io.grpc.ManagedChannelBuilder#maxInboundMessageSize` — the same for channels. OWASP ASVS 5.0 §15.2.2 — defenses against loss of availability from resource-demanding functionality. CWE-400 — by id.

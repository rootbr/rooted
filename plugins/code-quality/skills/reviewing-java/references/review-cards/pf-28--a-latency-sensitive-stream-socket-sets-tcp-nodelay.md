---
title: A stream socket carrying a request-response or latency-sensitive protocol with small writes sets TCP_NODELAY before its first write
rule_id: PF-28
domain: performance
triggers: ['new Socket\(', 'SocketChannel[.]open\(', 'setTcpNoDelay\(', 'TCP_NODELAY', 'AsynchronousSocketChannel[.]open\(', '[.]accept\(\)']
scope: file
check_kind: semantic
severity_default: minor
---

# A stream socket carrying a request-response or latency-sensitive protocol with small writes sets TCP_NODELAY before its first write

## Thesis
When code opens a TCP socket or accepts a connection for a protocol that sends small messages and waits for the reply — an RPC, a database wire protocol, a control channel, an interactive session — it sets `TCP_NODELAY` (`socket.setTcpNoDelay(true)` or `channel.setOption(StandardSocketOptions.TCP_NODELAY, true)`) before the first write; a bulk transfer keeps the default.

## Rationale
The default for `TCP_NODELAY` is false: the Nagle algorithm coalesces short segments to improve network efficiency by holding a small write until the previous segment is acknowledged. For a request-response exchange the peer's acknowledgement may itself wait on its delayed-acknowledgement timer, so a small request written in two pieces, or a reply written after a request, waits out that timer before it leaves the host — a latency added per round trip that a loopback test with large messages never shows. Enabling the option sends each write as soon as it is available; the option is meant to be enabled exactly where it is known that the coalescing impacts performance, which is the small-write, wait-for-reply case.

## Example
```java
bad:  SocketChannel ch = SocketChannel.open(addr);
      ch.write(header); ch.write(body);         // small writes, then read the reply
good: SocketChannel ch = SocketChannel.open(addr);
      ch.setOption(StandardSocketOptions.TCP_NODELAY, true);
      ch.write(header); ch.write(body);
```

## Limits
A socket used for bulk streaming (file transfer, a log shipper) benefits from coalescing and keeps the default. A socket created by a client library that sets the option itself (many HTTP, database and messaging clients do) is out of scope. Writes already batched into one segment per message gain little, though the option still costs nothing. Once enabled, whether the option can be disabled again is system dependent.

## Validator
On the triggered hunk find each socket or channel the diff opens or accepts. Open the file: determine the protocol's write pattern (several small writes per message, or a write followed by a blocking read of the reply) and look for `setTcpNoDelay(true)` or `setOption(TCP_NODELAY, true)` before the first write. Validator question: **does this socket carry small request-response writes without TCP_NODELAY set?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PF-28`, severity minor, `file`, `symbol`, `code` = the socket or channel creation quoted verbatim from the diff, `fix` = the `TCP_NODELAY` option set before the first write, `rationale` naming the coalescing delay per round trip).

## Source
`java.net.StandardSocketOptions#TCP_NODELAY` Javadoc, Java SE 21 — "Disable the Nagle algorithm... TCP/IP uses an algorithm known as The Nagle Algorithm to coalesce short segments and improve network efficiency. The default value of this socket option is FALSE. The socket option should only be enabled in cases where it is known that the coalescing impacts performance... Once the option is enabled, it is system dependent whether it can be subsequently disabled"; its `@spec` reference is RFC 1122. RFC 1122 §4.2.3.4 (the Nagle algorithm, which an application must be able to turn off) and §4.2.3.2 (delayed acknowledgements) — not fetched from the authoring environment.

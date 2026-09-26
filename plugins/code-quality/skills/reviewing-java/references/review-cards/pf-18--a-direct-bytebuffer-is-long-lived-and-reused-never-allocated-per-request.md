---
title: A direct ByteBuffer is a large, long-lived, reused buffer for native I/O, never allocated per request or per message
rule_id: PF-18
domain: performance
triggers: ['allocateDirect\(', 'ByteBuffer[.]allocate\(', 'MappedByteBuffer', 'SocketChannel', 'FileChannel', 'DatagramChannel']
scope: file
check_kind: semantic
severity_default: minor
---

# A direct ByteBuffer is a large, long-lived, reused buffer for native I/O, never allocated per request or per message

## Thesis
`ByteBuffer.allocateDirect` is called for buffers that live for the life of a connection, a channel or a pool and are reused across operations; a per-request or per-message buffer is a heap `ByteBuffer.allocate`, a slice of a pooled direct buffer, or a per-thread cached direct buffer sized to the common maximum.

## Rationale
A direct buffer's memory lives outside the garbage-collected heap: allocating and deallocating it typically costs more than a heap buffer, its memory is released by a cleaning action after the buffer object becomes unreachable rather than when the request ends, and its footprint is invisible to heap metrics. A direct buffer per request therefore pays the expensive allocation each time and accumulates native memory between collections, up to the direct-memory limit, at which point the allocator waits for reference processing before it fails. The platform recommends direct buffers primarily for large, long-lived buffers subject to native I/O, and only where they yield a measurable gain. A heap buffer handed to a channel is copied through a per-thread temporary direct buffer that the runtime caches, so the per-request heap form keeps the native I/O path.

## Example
```java
bad:  void send(SocketChannel ch, byte[] payload) throws IOException {
          ByteBuffer buf = ByteBuffer.allocateDirect(payload.length);
          buf.put(payload).flip(); ch.write(buf);
      }
good: private static final ThreadLocal<ByteBuffer> BUF =
          ThreadLocal.withInitial(() -> ByteBuffer.allocateDirect(64 * 1024));
      void send(SocketChannel ch, byte[] payload) throws IOException {
          ByteBuffer buf = BUF.get().clear(); buf.put(payload).flip(); ch.write(buf);
      }
```

## Limits
A direct buffer allocated once per channel, per connection or per pool, a memory-mapped file, and a framework-managed pooled allocator are correct uses. Code off the I/O path that never hands the buffer to a channel has no reason for a direct buffer at all. A tolerance in the project context — "requests are rare; a direct buffer per request is accepted" — rejects the finding. Whether an allocated direct buffer is released is a resource-lifetime question outside this rule.

## Validator
On the triggered hunk find each `ByteBuffer.allocateDirect`. Open the file: is the call on a per-request, per-message or per-iteration path (inside a handler, a loop, a method called per operation) rather than in a constructor, a static initializer, a pool or a per-thread initializer? Validator question: **is a direct buffer allocated on every request or message instead of being reused?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PF-18`, severity minor, `file`, `symbol`, `code` = the `allocateDirect` call quoted verbatim from the diff, `fix` = the heap buffer or the reused or pooled direct buffer, `rationale` naming the allocation cost and the deferred native-memory release).

## Source
`java.nio.ByteBuffer` class Javadoc, Java SE 21 ("Direct vs. non-direct buffers") — "The buffers returned by this method typically have somewhat higher allocation and deallocation costs than non-direct buffers. The contents of direct buffers may reside outside of the normal garbage-collected heap, and so their impact upon the memory footprint of an application might not be obvious. It is therefore recommended that direct buffers be allocated primarily for large, long-lived buffers that are subject to the underlying system's native I/O operations. In general it is best to allocate direct buffers only when they yield a measurable gain in program performance." JDK 21 source `java.nio.Bits#reserveMemory` — on reaching the direct-memory limit the allocator retries while "Cleaners that might free direct buffer memory" are processed; `sun.nio.ch.Util` — "Per-carrier-thread cache of temporary direct buffers" used when a heap buffer is passed to a channel.

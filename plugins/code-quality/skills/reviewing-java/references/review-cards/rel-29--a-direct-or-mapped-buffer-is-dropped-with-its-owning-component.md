---
title: A direct or mapped buffer is owned by the component whose lifetime bounds its use and is dropped with it, never retained by a per-request or per-connection object
rule_id: REL-29
domain: reliability
triggers: ['allocateDirect\(', 'MappedByteBuffer', '[.]map\(\s*(FileChannel[.])?MapMode[.]', '[.]map\(\s*(READ_ONLY|READ_WRITE|PRIVATE)']
scope: file
check_kind: semantic
severity_default: major
---

# A direct or mapped buffer is owned by the component whose lifetime bounds its use and is dropped with it, never retained by a per-request or per-connection object

## Thesis
A direct `ByteBuffer` or a `MappedByteBuffer` lives in a field of the component whose lifetime bounds its use — the channel handler, the connection, the pool, the index reader — and that owner drops the reference when it closes or is discarded. A request, message, session or cache entry that keeps such a buffer in a field after its use is done, or a long-lived collection that accumulates them without eviction, does not hold it: the native memory behind the buffer is reclaimed only when the buffer object itself becomes unreachable and is collected.

## Rationale
Finishing with a direct or mapped buffer frees nothing: "The buffer and the mapping that it represents will remain valid until the buffer itself is garbage-collected", and "Closing the channel, in particular, has no effect upon the validity of the mapping". Reclaim happens when the collector finds the buffer unreachable and its cleaner runs, so a buffer that a live object still references is never reclaimed, and the object that retains it — a finished request kept in a queue, a closed session kept in a map, an entry in an unbounded cache — holds native memory that no heap metric shows. The runtime caps the total capacity of direct buffers: when a reservation fails, the allocator waits for reference processing, calls `System.gc()`, retries with back-off, and then throws `OutOfMemoryError` — "Cannot reserve N bytes of direct buffer memory (allocated: …, limit: …)" — while the heap itself looks idle. A buffer that goes with its owner keeps the reserved total proportional to the live components, not to the history of requests.

## Example
```java
bad:  record Session(long id, MappedByteBuffer index) {}                       // per-connection object owns the mapping
      finished.add(new Session(id, ch.map(READ_ONLY, 0, ch.size())));        // retained after the connection ends
good: final class Index implements AutoCloseable {                             // the long-lived reader owns the mapping
          private MappedByteBuffer page;
          Index(FileChannel ch) throws IOException { page = ch.map(FileChannel.MapMode.READ_ONLY, 0, ch.size()); }
          int at(int i) { return page.getInt(i); }
          @Override public void close() { page = null; }                       // the last reference goes with the owner
      }
```

## Limits
A buffer taken from and returned to a pool (a Netty allocator, a project pool) is owned by the pool, and the pool's own bound is out of scope. A direct buffer allocated and dropped within one request, never stored past it, is an allocation-cost question, not this finding. A `MappedByteBuffer` held for the life of the process by a component that is never discarded is correct. A project context naming an off-heap budget and an eviction policy for a buffer cache rejects the finding for that cache.

## Validator
On the triggered hunk find each `allocateDirect` or `map` call and the field, local or collection that receives the buffer. Open the file and trace who holds the reference: a field of a component whose lifetime bounds the use and whose close path drops it, or a request, message, session, cache entry or collection that outlives the buffer's use. Validator question: **is this direct or mapped buffer retained by an object that outlives its use, so the native memory stays reserved after the buffer is done?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: REL-29`, severity major, `file`, `symbol`, `code` = the allocation or mapping and the retaining field or collection quoted verbatim from the diff, `fix` = the buffer held by the component whose lifetime bounds its use and dropped in its close path, `rationale` naming the native memory that stays reserved until the retainer dies).

## Source
`java.nio.channels.FileChannel#map(MapMode, long, long)` Javadoc, Java SE 21 — "The buffer and the mapping that it represents will remain valid until the buffer itself is garbage-collected"; "A mapping, once established, is not dependent upon the file channel that was used to create it. Closing the channel, in particular, has no effect upon the validity of the mapping". `java.nio.MappedByteBuffer` class Javadoc — "A mapped byte buffer and the file mapping that it represents remain valid until the buffer itself is garbage-collected". `java.nio.Bits#reserveMemory` source, JDK 21 — on a failed reservation the allocator retries "until success or there are no more references (including Cleaners that might free direct buffer memory) to process", calls `System.gc()`, backs off, and then throws `OutOfMemoryError("Cannot reserve " + size + " bytes of direct buffer memory (allocated: " + RESERVED_MEMORY.get() + ", limit: " + MAX_MEMORY + ")")`. `java.nio.ByteBuffer` class Javadoc, "Direct vs. non-direct buffers" — "The contents of direct buffers may reside outside of the normal garbage-collected heap, and so their impact upon the memory footprint of an application might not be obvious".

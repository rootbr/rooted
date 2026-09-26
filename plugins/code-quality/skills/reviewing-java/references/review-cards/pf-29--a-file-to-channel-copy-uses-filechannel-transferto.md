---
title: Copying a file to a socket or another channel uses FileChannel.transferTo or transferFrom, never a read-write loop through a user-space buffer
rule_id: PF-29
domain: performance
triggers: ['FileChannel', 'transferTo\(', 'transferFrom\(', 'while \(\(\w+ = \w+[.]read\(', 'while \(\w+[.]read\(', 'Files[.]copy\(', 'newInputStream\(|newOutputStream\(']
scope: hunk
check_kind: mechanical
severity_default: minor
---

# Copying a file to a socket or another channel uses FileChannel.transferTo or transferFrom, never a read-write loop through a user-space buffer

## Thesis
Code that serves a file over a socket, writes a received stream into a file, or copies between channels calls `FileChannel.transferTo(position, count, target)` (or `transferFrom`) in a loop until the whole range is moved; it does not read the file into a `ByteBuffer` or `byte[]` and write it out chunk by chunk. For stream-to-stream copies, `InputStream.transferTo(OutputStream)` and `Files.copy` are the equivalent forms.

## Rationale
`transferTo` is potentially much more efficient than a simple loop that reads from the file channel and writes to the target channel: many operating systems can transfer bytes directly from the filesystem cache to the target channel without copying them, so the data never enters a Java buffer, the copy takes one system call per call instead of two per chunk, and no per-request buffer is allocated. A read-write loop pays two copies per chunk — kernel to user buffer, user buffer to kernel — a system call for each, and the buffer. `transferTo` may transfer fewer bytes than requested, so the call is repeated until the count is reached.

## Example
```java
bad:  ByteBuffer buf = ByteBuffer.allocate(8192);
      while (file.read(buf) > 0) { buf.flip(); socket.write(buf); buf.clear(); }
good: long pos = 0, size = file.size();
      while (pos < size) pos += file.transferTo(pos, size - pos, socket);
```

## Limits
A copy that transforms the bytes (compression, encryption, framing) needs a user-space buffer. A copy of a few kilobytes off the hot path is not worth changing. Streams that are not channels use `InputStream.transferTo`, which reads all bytes and writes them in order without a caller-managed buffer. Whether the channels are closed is a resource-lifetime concern outside this rule.

## Validator
On the triggered hunk find each loop that reads from a `FileChannel` or file stream into a buffer and writes the same bytes unchanged to another channel or stream. Validator question: **does this code copy a file's bytes unchanged through a user-space buffer where transferTo or transferFrom would move them directly?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PF-29`, severity minor, `file`, `symbol`, `code` = the read-write loop quoted verbatim from the diff, `fix` = the `transferTo` or `transferFrom` loop, `rationale` naming the user-space copies and system calls avoided).

## Source
`java.nio.channels.FileChannel#transferTo(long, long, WritableByteChannel)` Javadoc, Java SE 21 — "This method is potentially much more efficient than a simple loop that reads from this channel and writes to the target channel. Many operating systems can transfer bytes directly from the filesystem cache to the target channel without actually copying them"; "Fewer than the requested number of bytes are transferred if" the file is shorter or a non-blocking target has less room; `#transferFrom` — the same statement for the reverse direction. `java.io.InputStream#transferTo(OutputStream)` Javadoc — "Reads all bytes from this input stream and writes the bytes to the given output stream in the order that they are read."

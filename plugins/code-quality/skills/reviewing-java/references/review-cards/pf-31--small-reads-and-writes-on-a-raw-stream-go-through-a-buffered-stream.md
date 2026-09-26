---
title: Byte-at-a-time or small reads and writes on a file, socket or process stream go through a BufferedInputStream, BufferedOutputStream, BufferedReader or BufferedWriter
rule_id: PF-31
domain: performance
triggers: ['new FileOutputStream\(', 'new FileInputStream\(', 'new FileWriter\(', 'new FileReader\(', 'new OutputStreamWriter\(', 'getOutputStream\(\)', 'getInputStream\(\)', 'Files[.]newOutputStream\(|Files[.]newInputStream\(', 'new PrintWriter\(']
scope: file
check_kind: mechanical
severity_default: minor
---

# Byte-at-a-time or small reads and writes on a file, socket or process stream go through a BufferedInputStream, BufferedOutputStream, BufferedReader or BufferedWriter

## Thesis
A raw stream that touches the operating system — `FileOutputStream`, `FileInputStream`, a socket's or process's `getInputStream()`/`getOutputStream()`, `Files.newInputStream`/`newOutputStream`, `FileWriter`/`FileReader` — is wrapped in the buffered counterpart (or replaced by `Files.newBufferedReader`/`newBufferedWriter`) when the code reads or writes it in small pieces: single bytes, single characters, short strings or lines. Large `byte[]` reads and writes and the JDK's own bulk copies may use the raw stream.

## Rationale
A `write(int)` on a raw file or socket stream is a call to the underlying system for that one byte; a `read()` on a raw input stream is a system call per byte. Each system call costs a user-kernel transition and, on a socket, may produce a tiny packet. A `BufferedOutputStream` lets an application write bytes to the underlying stream without necessarily causing a call to the underlying system for each byte written: it collects them in a buffer that grows to 8 KB by default and flushes it in one call; a `BufferedInputStream` refills its buffer from the contained stream many bytes at a time and serves reads from it. For character streams the same holds — without buffering each `print()` converts and writes immediately, which can be very inefficient. The difference is a system call per byte versus one per buffer.

## Example
```java
bad:  OutputStream out = socket.getOutputStream();
      for (byte b : payload) out.write(b);
good: OutputStream out = new BufferedOutputStream(socket.getOutputStream());
      for (byte b : payload) out.write(b);
      out.flush();
```

## Limits
A stream written once with a whole `byte[]`, or copied through `InputStream.transferTo` or `Files.copy`, an `ObjectOutputStream` or `DataOutputStream` already wrapped over a buffered stream, and a `PrintStream` constructed with its own buffering are fine. A buffered writer must be flushed or closed before the reader expects the data; a protocol that needs a message on the wire at once flushes after the message. Whether the stream is closed is a resource-lifetime concern outside this rule.

## Validator
On the triggered hunk find each raw stream construction or accessor. Open the file: are its reads or writes single bytes or characters, short strings, or line by line, with no buffered wrapper between the code and the raw stream? Validator question: **does this code make a system call per byte, character or line by reading or writing a raw stream in small pieces?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PF-31`, severity minor, `file`, `symbol`, `code` = the raw stream construction and one small write or read quoted verbatim from the diff, `fix` = the buffered wrapper with a flush where the protocol needs it, `rationale` naming the system call per byte).

## Source
`java.io.BufferedOutputStream` class Javadoc, Java SE 21 — "By setting up such an output stream, an application can write bytes to the underlying output stream without necessarily causing a call to the underlying system for each byte written"; in the JDK 21 source the default buffer starts at 512 bytes and grows to 8192. `java.io.BufferedInputStream` class Javadoc — "the internal buffer is refilled as necessary from the contained input stream, many bytes at a time". `java.io.BufferedWriter` class Javadoc — "Without buffering, each invocation of a print() method would cause characters to be converted into bytes that would then be written immediately to the file, which can be very inefficient." `java.io.FileOutputStream#write(int)` — "Writes the specified byte to this file output stream."

---
title: Many small repeated writes to a file, socket or other stream that does not buffer go through a buffered writer that is flushed when the writing ends, and are not flushed one by one, unless the output is required to appear promptly
rule_id: PRF-29
domain: performance
step: [implement]
applies_to: [universal]
triggers: ['\bnew\s+(FileOutputStream|PrintStream)\s*\(|\bFile::(create|open)\s*\(|\bOpenOptions::new\s*\(|\bTcpStream::connect\s*\(|\bfs[.]openSync\s*\(|\bbuffering\s*=\s*0\b|\bnew\s+PrintWriter\s*\(.*,\s*true\s*\)|\bsetvbuf\s*\(.*_IONBF|\bsetbuf\s*\(\s*\w+\s*,\s*(NULL|0|nullptr)\s*\)', '\bos[.]write\s*\(|\bsyscall[.]Write\s*\(|\bwrite(Sync)?\s*\(\s*(fd|\w+_fd|STDOUT_FILENO|STDERR_FILENO|[12])\s*,|\bstd::endl\b|<<\s*endl\b|\bflush\s*=\s*True\b|[.](flush|Flush)\s*\(\s*\)']
scope: file
check_kind: semantic
severity_default: minor
---

# Many small repeated writes to a file, socket or other stream that does not buffer go through a buffered writer that is flushed when the writing ends, and are not flushed one by one, unless the output is required to appear promptly

## Thesis
A routine that makes many small, repeated write calls to a destination that does not buffer (a raw file handle, a network socket, a file descriptor written with a system call, a file opened with buffering switched off, or a stream that flushes after every write) wraps that destination once in a buffered writer, or drops the flush that follows each write, and flushes or closes the writer once after the last write. The rule holds where the output is not required to appear promptly; where prompt or unbuffered output is required, the per-write path stays.

## Rationale
Every write call on an unbuffered network socket is a system call, and a buffered output stream exists so that an application can write bytes without necessarily causing a call to the underlying system for each byte. Without a buffer, each print call converts its characters to bytes that are written to the file immediately, which can be very inefficient. A buffered writer keeps the data in an in-memory buffer and forwards it to the underlying writer in large, infrequent batches; by writing only large chunks even when the caller writes a single byte, it hides any inefficiency in calling and executing the operating system's unbuffered routines. A flush after every write gives that batching up: redundant flushes slow output down, and writing to a file rarely needs a flush. The gain depends on the operating system and the kind of I/O, and on some systems unbuffered disk I/O can be as fast as buffered I/O; buffered I/O still offers predictable performance regardless of the platform and the backing device, which makes it almost always preferable for binary data. The data is guaranteed to have been forwarded to the underlying writer only once the writer is flushed after all of it has been written, and where disposing of a writer attempts the flush implicitly, errors raised during disposal can be ignored, so the explicit flush or close after the last write is part of the rule.

## Example
```typescript
bad:  const fd = fs.openSync(path, "w");
      for (const row of rows) fs.writeSync(fd, format(row));
      fs.closeSync(fd);
good: const out = fs.createWriteStream(path);
      out.cork();
      for (const row of rows) out.write(format(row));
      await finished(out.end());
```

## Limits
A destination that already buffers, and is not flushed after each write, lies outside the rule: a text file or a non-interactive standard output that the runtime opens block-buffered, and a character writer that accumulates its encoded bytes in a buffer before writing them, around which a further buffer only avoids frequent converter invocations. A buffer does not help when the routine writes very large amounts at once or writes only once or a few times, and it gives no advantage when the destination is itself in memory. Output that is required to appear promptly, or required unbuffered, keeps its per-write path, and a runtime may already line-buffer standard output when it is interactive and the standard error stream. The rule does not judge how the error reported by the final flush is handled.

## Validator
Grep the hunk for a raw file handle, descriptor or socket being opened or written, a file opened with buffering switched off, a flush call, a line terminator or print option that flushes, or a stream configured to flush on every write. Open the file and find each routine that writes to that destination: trace whether the writes run inside a loop or as many successive calls, whether each write is small, and whether the destination or a wrapper around it already buffers. Read the surrounding code and comments for a requirement that each record appear at once, such as an interactive prompt or an error stream, and check that a buffered writer in the hunk is flushed or closed after its last write. Validator question: **Does a routine make many small repeated writes to a destination that does not buffer or that is flushed after each of them, or leave its buffered writer unflushed after the last write, where nothing requires the output to appear promptly?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PRF-29`, severity minor, `file`, `symbol`, `code` = the write or flush call inside the loop and the line that opens the destination, `fix` = the destination wrapped once in a buffered writer before the loop, or the flush after each write removed, and one flush or close after the last write, in the file's language, `rationale` = the unbuffered destination, the number of small writes per run, and the call into the operating system that each write costs).

## Source
- `rust-lang/rust` master, `library/std/src/fs.rs`, struct `File` doc comment (fetched): "`File` does not buffer reads and writes. For efficiency, consider wrapping the file in a [`BufReader`] or [`BufWriter`] when performing many small [`read`] or [`write`] calls, unless unbuffered reads and writes are required."
- `rust-lang/rust` master, `library/alloc/src/io/buffered/bufwriter.rs`, struct `BufWriter` doc comment (fetched): "every call to [`write`][`TcpStream::write`] on [`TcpStream`] results in a system call. A `BufWriter<W>` keeps an in-memory buffer of data and writes it to an underlying writer in large, infrequent batches." / "It does not help when writing very large amounts at once, or writing just one or a few times. It also provides no advantage when writing to a destination that is in memory" / "It is critical to call [`flush`] before `BufWriter<W>` is dropped. Though dropping will attempt to flush the contents of the buffer, any errors that happen in the process of dropping will be ignored."
- `openjdk/jdk` tag jdk-21-ga, `src/java.base/share/classes/java/io/BufferedOutputStream.java`, class doc (fetched): "an application can write bytes to the underlying output stream without necessarily causing a call to the underlying system for each byte written."
- `openjdk/jdk` tag jdk-21-ga, `src/java.base/share/classes/java/io/BufferedWriter.java`, class doc (fetched): "Unless prompt output is required, it is advisable to wrap a BufferedWriter around any Writer whose write() operations may be costly" / "Without buffering, each invocation of a print() method would cause characters to be converted into bytes that would then be written immediately to the file, which can be very inefficient."
- `openjdk/jdk` tag jdk-21-ga, `src/java.base/share/classes/java/io/OutputStreamWriter.java`, class doc (fetched): "The resulting bytes are accumulated in a buffer before being written to the underlying output stream." / "consider wrapping an OutputStreamWriter within a BufferedWriter so as to avoid frequent converter invocations."
- `python/cpython` main, `Doc/library/io.rst`, Performance, Binary I/O (fetched): "By reading and writing only large chunks of data even when the user asks for a single byte, buffered I/O hides any inefficiency in calling and executing the operating system's unbuffered I/O routines. The gain depends on the OS and the kind of I/O which is performed. For example, on some modern OSes such as Linux, unbuffered disk I/O can be as fast as buffered I/O. The bottom line, however, is that buffered I/O offers predictable performance regardless of the platform and the backing device. Therefore, it is almost always preferable to use buffered I/O rather than unbuffered I/O for binary data."
- `python/cpython` main, `Doc/library/sys.rst`, `sys.stdout` buffering (fetched): "When interactive, the ``stdout`` stream is line-buffered. Otherwise, it is block-buffered like regular text files. The ``stderr`` stream is line-buffered in both cases."
- `isocpp/CppCoreGuidelines` master, SL.io.50 "Avoid `endl`" (fetched): "as most commonly used it simply slows down output by doing redundant `flush()`s." / "For writing to a file, there is rarely a need to `flush`."
- `golang/go` master, `src/bufio/bufio.go`, type `Writer` (fetched): "After all data has been written, the client should call the [Writer.Flush] method to guarantee all data has been forwarded to the underlying [io.Writer]."
- `nodejs/node` main, `doc/api/stream.md`, `writable.cork()` (fetched): "The `writable.cork()` method forces all written data to be buffered in memory. The buffered data will be flushed when either the [`stream.uncork()`][] or [`stream.end()`][stream-end] methods are called." / "The `'finish'` event is emitted after the [`stream.end()`][stream-end] method has been called, and all data has been flushed to the underlying system."
- Caveat: the documents state the mechanism without figures, and for disk files the gain depends on the operating system.

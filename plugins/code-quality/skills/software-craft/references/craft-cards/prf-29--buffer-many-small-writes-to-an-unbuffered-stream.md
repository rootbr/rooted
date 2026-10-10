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

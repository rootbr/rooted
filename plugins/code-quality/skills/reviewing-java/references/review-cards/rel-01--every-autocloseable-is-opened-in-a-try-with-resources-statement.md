---
title: Every AutoCloseable that holds an I/O handle is opened in a try-with-resources statement, so it closes on every exit path
rule_id: REL-01
domain: reliability
triggers: ['new (File|Buffered|Object|Data|Zip|GZIP|Input|Output)\w*(Stream|Reader|Writer)\(', 'getConnection\(', 'prepareStatement\(', 'createStatement\(', 'executeQuery\(', 'openStream\(', 'newBufferedReader\(', 'newBufferedWriter\(', 'newInputStream\(', 'newOutputStream\(', 'FileChannel[.]open\(', 'SocketChannel[.]open\(', 'new Socket\(', 'new ServerSocket\(', 'getInputStream\(', 'getOutputStream\(', 'AutoCloseable', 'Closeable', 'CloseableHttpResponse', 'newCall\(']
scope: file
check_kind: mechanical
severity_default: major
---

# Every AutoCloseable that holds an I/O handle is opened in a try-with-resources statement, so it closes on every exit path

## Thesis
A stream, reader, writer, channel, socket, JDBC `Connection`, `Statement` or `ResultSet`, or HTTP response body that the diff opens is declared in the resource header of a `try` statement, so that `close()` runs when the block exits by return, by exception or by fall-through; dependent resources are declared after the resource they wrap, so they close first.

## Rationale
An `AutoCloseable` holds an operating-system or pool resource — a file descriptor, a socket, a pooled connection — until `close()` runs. A `close()` placed after the work runs only when the work returns normally; the exception path leaks the handle, and under load the leaks accumulate until the descriptor table or the connection pool is exhausted and every later request fails. The resource header of a `try` statement closes each declared resource automatically on every exit, in reverse order of declaration, and keeps an exception thrown by `close()` attached as a suppressed exception to the one that ended the block.

## Example
```java
bad:  Connection c = ds.getConnection();
      PreparedStatement ps = c.prepareStatement(sql);
      ResultSet rs = ps.executeQuery();
      return map(rs);
good: try (Connection c = ds.getConnection();
           PreparedStatement ps = c.prepareStatement(sql);
           ResultSet rs = ps.executeQuery()) { return map(rs); }
```

## Limits
Applies to a resource the method both opens and finishes with. A resource returned to the caller, stored in a field with a documented owner that closes it, or handed to a framework that manages its lifetime (a container-managed `EntityManager`, an injected pooled client) is out of scope. A `try`/`finally` whose `finally` closes the resource is a correct form and is not flagged. An `AutoCloseable` type whose instances hold no releasable resource — a `Stream` over a collection, an in-memory `ByteArrayInputStream`, a `StringWriter` — needs no resource header.

## Validator
On the triggered hunk find each expression that opens a handle-holding `AutoCloseable`: a constructor of a file, socket, zip or object stream, a `getConnection`, `prepareStatement`, `createStatement` or `executeQuery` call, a `Files.new*` or `*Channel.open` call, an HTTP client execute or `newCall(...).execute()`. Open the file and check whether the expression is the initializer of a `try` resource, or is closed in a `finally` block, or leaves the method as a return value or a field with an owner. Validator question: **is there an exit path from this method — a return, an exception, a fall-through — on which the handle is never closed?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: REL-01`, severity major, `file`, `symbol`, `code` = the opening expression quoted verbatim from the diff, `fix` = the same expression as a `try` resource with dependents declared in wrapping order, `rationale` naming the exit path that leaks and the pool or descriptor limit it exhausts).

## Source
`java.lang.AutoCloseable` Javadoc, Java SE 21 — "The close() method of an AutoCloseable object is called automatically when exiting a try-with-resources block for which the object has been declared in the resource specification header. This construction ensures prompt release, avoiding resource exhaustion exceptions and errors that may otherwise occur"; its API note that try-with-resources is unnecessary for non-I/O-based forms. JLS §14.20.3 — resources closed in reverse order of initialization, exceptions from `close()` suppressed.

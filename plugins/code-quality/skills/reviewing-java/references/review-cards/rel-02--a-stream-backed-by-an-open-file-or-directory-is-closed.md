---
title: A Stream returned by Files.lines, Files.list, Files.walk or Files.find, or a streaming query result, is closed by try-with-resources
rule_id: REL-02
domain: reliability
triggers: ['Files[.]lines\(', 'Files[.]list\(', 'Files[.]walk\(', 'Files[.]find\(', 'getResultStream\(', '[.]stream\(\)\s*$', '\w*[Qq]uery\w*[.]stream\(', 'newDirectoryStream\(']
scope: hunk
check_kind: mechanical
severity_default: major
---

# A Stream returned by Files.lines, Files.list, Files.walk or Files.find, or a streaming query result, is closed by try-with-resources

## Thesis
A `Stream` whose source is an open file or directory — the return value of `Files.lines`, `Files.list`, `Files.walk` or `Files.find` — or the result stream of a database query is declared as a `try` resource so that the underlying file, directory or cursor is closed when the pipeline finishes; a terminal operation alone does not close it.

## Rationale
The stream returned by these methods contains a reference to an open file or directory, and that handle is closed only by closing the stream. A pipeline such as `Files.lines(p).filter(...).count()` runs the terminal operation and drops the stream object; the descriptor stays open, because nothing in the pipeline closes it, and each such call leaves one more open. A stream over a collection, array or generator holds no handle and needs no closing, which is why the leak is easy to miss: the API is the same.

## Example
```java
bad:  long n = Files.lines(path).filter(l -> l.contains("ERROR")).count();
good: try (Stream<String> lines = Files.lines(path)) {
          n = lines.filter(l -> l.contains("ERROR")).count();
      }
```

## Limits
Applies to a stream whose source is an I/O handle. A stream from `List.stream()`, `Arrays.stream`, `Stream.of` or `IntStream.range` is not flagged. A stream returned to the caller with the closing duty documented on the method, or wrapped with `onClose` and closed by a caller shown in the diff, is out of scope. A `DirectoryStream` from `Files.newDirectoryStream` is a resource of the same kind and takes the same form.

## Validator
On the triggered hunk find each `Files.lines`, `Files.list`, `Files.walk`, `Files.find`, `Files.newDirectoryStream` call and each query `getResultStream()` or `stream()` on a query object. Check whether the call is the initializer of a `try` resource, is closed in a `finally`, or is returned to a caller. Validator question: **does this stream over an open handle reach a terminal operation, or leave scope, without a `close()` on every path?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: REL-02`, severity major, `file`, `symbol`, `code` = the stream-opening expression quoted verbatim from the diff, `fix` = the same expression as a `try` resource, `rationale` naming the open file, directory or cursor that the terminal operation leaves open).

## Source
`java.nio.file.Files#lines(Path, Charset)` Javadoc, Java SE 21 — "The returned stream contains a reference to an open file. The file is closed by closing the stream"; its API note — "This method must be used within a try-with-resources statement or similar control structure to ensure that the stream's open file is closed promptly after the stream's operations have completed". `Files#list`, `#walk`, `#find` — "The directory is closed by closing the stream", with the same API note. `java.lang.AutoCloseable` Javadoc — try-with-resources is "in general unnecessary when using non-I/O-based forms" of `Stream`. Hibernate ORM `org.hibernate.query.SelectionQuery#getResultStream` Javadoc — "The client should call Stream.close() after processing the stream so that resources are freed as soon as possible".

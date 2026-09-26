---
title: A file path built from untrusted input is resolved against a fixed base, normalized, and rejected unless it still starts with the base
rule_id: SEC-15
domain: security
triggers: ['new File\(', 'Paths[.]get\(|Path[.]of\(', '[.]resolve\(', 'getRealPath\(', 'Files[.](read|write|copy|move|delete|newInputStream|newOutputStream|newBufferedReader|newBufferedWriter|exists|size|lines|list|walk)', 'new File(Input|Output)Stream\(|new FileReader\(|new FileWriter\(|RandomAccessFile']
scope: file
check_kind: semantic
severity_default: critical
---

# A file path built from untrusted input is resolved against a fixed base, normalized, and rejected unless it still starts with the base

## Thesis
Any filesystem operation whose path contains a value from outside the code — a filename parameter, an upload name, a document id used as a name — computes `Path target = base.resolve(value).normalize()` (or `toRealPath()` when the file must exist) against a base the code owns, and rejects the request unless `target.startsWith(base)` where `base` is itself absolute and normalized; the operation then uses `target`. `new File(userInput)`, `Paths.get(dir, userInput)` without the check, and `ServletContext.getRealPath(userInput)` are the defect; mapping an id to a stored name so that no user text enters the path is the better form.

## Rationale
A path is interpreted by the filesystem after the code has looked at it: `..` segments climb out of the intended directory, an absolute value replaces the base entirely in `resolve`, an encoded or mixed separator survives a string check, and a symbolic link inside the base points outside it. `normalize` removes `.` and `..` lexically and `toRealPath` resolves links and requires existence, so the prefix check that follows compares locations rather than the text the request sent; a check on the raw string (`contains("..")`) misses `%2e%2e`, `....//` and absolute paths. `getRealPath` translates a virtual path without applying the container's own constraints — its documentation warns that it bypasses the `WEB-INF` and declared security constraints and that unsanitized user data must not build its argument. Reading `/etc/passwd`, application secrets or other users' uploads, and writing into the webroot, are the consequences.

## Example
```java
bad:  Path p = Paths.get(uploadDir, req.getParameter("name"));
      return Files.readAllBytes(p);
good: Path base = Paths.get(uploadDir).toAbsolutePath().normalize();
      Path p = base.resolve(req.getParameter("name")).normalize();
      if (!p.startsWith(base)) throw new IllegalArgumentException("outside base");
      return Files.readAllBytes(p);
```

## Limits
Applies when a path component originates outside the code. A path from configuration, a constant, or an id looked up to a server-generated name is not flagged. A `startsWith` on the normalized (or real) `Path` against a normalized base is the correct check; `startsWith` on the raw string is not, because `/data/uploads-private` starts with `/data/uploads` textually while `Path.startsWith` compares name elements. Class-path resources read with a constant name are out of scope. A value first reduced to an allowlisted set (`[a-z0-9-]+`, no separators) before joining is an acceptable form when the base is fixed.

## Validator
On the triggered hunk find each path or file construction with a non-constant component and each `getRealPath` call, and trace the component to its origin in the file. Where it originates in a request or upload, look between construction and the file operation for `normalize` or `toRealPath` followed by `startsWith(base)` on `Path` objects, or for a reduction to an allowlist without separators. Validator question: **can a request choose a path component that lets the operation touch a file outside the directory the code intended?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: SEC-15`, severity critical, `file`, `symbol`, `code` = the path construction and the file operation quoted verbatim from the diff, `fix` = the resolve-normalize-startsWith sequence against the base, `rationale` naming the traversal the raw component allows).

## Source
`java.nio.file.Path#normalize` Javadoc, Java SE 21 — "Eliminating ".." and a preceding name from a path may result in the path that locates a different file than the original path. This can arise when the preceding name is a symbolic link"; `#toRealPath` — an absolute path with symbolic links resolved, throwing if the file does not exist; `#startsWith(Path)` — "this path starts with the same name elements as the given path". Jakarta Servlet `ServletContext#getRealPath` Javadoc — "This method bypasses both implicit (no direct access to WEB-INF or META-INF) and explicit (defined by the web application) security constraints. Care should be taken both when constructing the path (e.g. avoid unsanitized user provided data)". OWASP ASVS 5.0 requirement 5.3.2. OWASP File Upload Cheat Sheet, "Filename Safety". SEI CERT FIO16-J; CWE-22.

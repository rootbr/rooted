---
title: Every conversion between bytes and characters names its Charset instead of relying on the platform default
rule_id: REL-09
domain: reliability
triggers: ['[.]getBytes\(\)', 'new String\(\w+(,\s*\w+,\s*\w+)?\)', 'new InputStreamReader\([^,)]*\)', 'new OutputStreamWriter\([^,)]*\)', 'new FileReader\(', 'new FileWriter\(', 'new PrintWriter\(', 'new Scanner\(']
scope: hunk
check_kind: mechanical
severity_default: minor
---

# Every conversion between bytes and characters names its Charset instead of relying on the platform default

## Thesis
A `String` decoded from bytes, a `byte[]` encoded from a `String`, and a `Reader`, `Writer`, `Scanner` or `PrintStream` wrapped around a byte stream passes an explicit `Charset` — normally `StandardCharsets.UTF_8` — rather than the no-argument overload that uses `Charset.defaultCharset()`.

## Rationale
The no-argument forms decode and encode with the virtual machine's default charset. Since Java 18 that default is UTF-8 "unless changed in an implementation specific manner": the launcher option `-Dfile.encoding=COMPAT` derives it from the operating system's locale, and an older runtime uses the locale directly. Text written on one machine and read on another, or by a process started with a different locale, is then decoded with a different mapping, and every non-ASCII character is corrupted with no exception — behaviour that "will cause the application behavior to vary between platforms". Naming the charset makes the bytes the same everywhere and documents the wire or file format.

## Example
```java
bad:  byte[] payload = text.getBytes();
      String body = new String(bytes);
      Reader in = new InputStreamReader(socket.getInputStream());
good: byte[] payload = text.getBytes(StandardCharsets.UTF_8);
      String body = new String(bytes, StandardCharsets.UTF_8);
      Reader in = new InputStreamReader(socket.getInputStream(), StandardCharsets.UTF_8);
```

## Limits
A project context that fixes the runtime at Java 18 or later and states that `file.encoding` is never set to `COMPAT` may treat the finding as a documentation suggestion. Console output through `System.out`, whose charset is meant to follow the terminal, is out of scope. A conversion that must follow the platform's charset by design — reading a locale-specific system file — is correct with a comment saying so. `Files.readString`, `Files.writeString`, `Files.readAllLines(Path)`, `Files.lines(Path)` and `Files.newBufferedReader(Path)` are UTF-8 by contract and are not flagged.

## Validator
On the triggered hunk find each `getBytes()`, `new String(byte[]...)`, `InputStreamReader`, `OutputStreamWriter`, `FileReader`, `FileWriter`, `PrintWriter`, `PrintStream` or `Scanner` call and check whether a `Charset` or charset name argument is present. Validator question: **does this byte-to-character or character-to-byte conversion omit the charset?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: REL-09`, severity minor, `file`, `symbol`, `code` = the conversion quoted verbatim from the diff, `fix` = the same call with `StandardCharsets.UTF_8` (or the format's documented charset), `rationale` naming the platform-dependent default it replaces).

## Source
`java.nio.charset.Charset#defaultCharset()` Javadoc, Java SE 21 — "The default charset is UTF-8, unless changed in an implementation specific manner"; implementation note — "An implementation may override the default charset with the system property file.encoding on the command line. If the value is COMPAT, the default charset is derived from the native.encoding system property, which typically depends upon the locale and charset of the underlying operating system". `java.lang.String#String(byte[])`, `#getBytes()`, `java.io.InputStreamReader#InputStreamReader(InputStream)`, `java.io.FileReader#FileReader(File)` — each documented as using the default charset. `java.nio.file.Files#readString(Path)` — "This method is equivalent to: readString(path, StandardCharsets.UTF_8)"; `#writeString`, `#readAllLines(Path)`, `#lines(Path)` and `#newBufferedReader(Path)` carry the same UTF-8 equivalence. SpotBugs `DM_DEFAULT_ENCODING` — "This will cause the application behavior to vary between platforms"; Error Prone `DefaultCharset`.

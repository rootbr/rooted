---
title: A temporary file is created through tempfile's mkstemp, mkdtemp, NamedTemporaryFile, TemporaryFile or TemporaryDirectory, never through tempfile.mktemp or by opening a path written as a literal under /tmp, /var/tmp or another publicly writable directory
rule_id: PY-95
domain: input
step: [implement, review]
applies_to: [python]
triggers: ['\bmktemp\(', '["''](?:/tmp|/var/tmp|/usr/tmp|/dev/shm)(?:/|["''])', 'environ(?:\[|[.]get\()\s*["''](?:TMPDIR|TMP|TEMP)["'']']
scope: hunk
check_kind: mechanical
severity_default: major
---

# A temporary file is created through tempfile's mkstemp, mkdtemp, NamedTemporaryFile, TemporaryFile or TemporaryDirectory, never through tempfile.mktemp or by opening a path written as a literal under /tmp, /var/tmp or another publicly writable directory

## Thesis
A Python temporary file or directory is created by tempfile.mkstemp or tempfile.mkdtemp, or by TemporaryFile, NamedTemporaryFile or TemporaryDirectory, which create it under the same rules, and the program works with the path that call returns; a name returned by tempfile.mktemp, a path written as a literal under /tmp, /var/tmp, /usr/tmp, /dev/shm or another publicly writable directory, and a fixed name joined to the value of TMPDIR, TMP or TEMP are never where the program creates a temporary file.

## Rationale
tempfile.mktemp returns a pathname of a file that does not exist at the time the call is made and leaves the caller to create the file; another process can create a file with the same name between the time the function returns and the time the caller creates it. The function is deprecated since Python 2.3, with mkstemp named in its place, and its use may introduce a security hole: by the time the program does anything with the name, someone else may have beaten it to the punch. When an application creates files in a publicly writable directory such as /tmp with predictable names, an attacker can create a file with the same name before the application does, potentially causing the application to read or write attacker-controlled content, and an attacker who discovers a hard-coded path can replace the contents of the file or directory with a malicious payload. mkstemp creates a temporary file in the most secure manner possible: there are no race conditions in the file's creation, assuming that the platform properly implements the os.O_EXCL flag for os.open, and the file is readable and writable only by the creating user ID. mkdtemp creates a directory with no race conditions in its creation, readable, writable and searchable only by the creating user ID. TemporaryFile creates its file securely using the same rules as mkstemp, NamedTemporaryFile operates exactly as TemporaryFile with a name visible in the file system, TemporaryDirectory creates its directory using the same rules as mkdtemp, and the file names the module uses include a string of random characters, which allows those files to be securely created in shared temporary directories.

## Example
```python
bad:  out = open(tempfile.mktemp(suffix=".csv"), "w")
      report = open("/tmp/report.csv", "w")
      cache = open(os.environ["TMPDIR"] + "/cache.db", "wb")
good: with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False) as out:
          out.write(rows)
      fd, cache_path = tempfile.mkstemp(suffix=".db")
```

## Limits
A literal directory passed as the dir= argument of a tempfile function is outside this rule, since tempfile still creates the file under its own random name: one position counts `tempfile.TemporaryFile(dir="/tmp/my_subdirectory", mode="w+")` compliant; the stricter position reports any string starting with a configured temporary path, at medium confidence. NamedTemporaryFile with delete=False is the easy replacement for mktemp. A temporary file created by other functions is acceptable as long as strong security controls are applied: a non-public directory, a unique file name, an unpredictable name generated with a cryptographically secure random generator, and a creation that fails if the target file already exists. The race freedom of mkstemp holds where the platform properly implements os.O_EXCL.

## Validator
Grep the hunk for `mktemp(` (tempfile.mktemp, or mktemp imported from tempfile), for string literals that start with /tmp, /var/tmp, /usr/tmp or /dev/shm, and for reads of TMPDIR, TMP or TEMP through os.environ or os.environ.get. For each hit, read the lines of the hunk that use its value: a mktemp name that is then opened, created or written, a literal path that is opened, created, written or made a directory, and a fixed name joined to the environment value and then opened are findings; a literal or environment value passed as the dir= argument of a tempfile function, and a path that is only compared, displayed or logged, are not. Validator question: **Does the hunk create or open a temporary file or directory at a name from tempfile.mktemp, at a literal path under a publicly writable directory, or at a fixed name joined to TMPDIR, TMP or TEMP?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-95`, severity major, `file`, `symbol`, `code` = the mktemp call, the literal path or the environment-built path together with the call that opens or creates it, verbatim from the diff, `fix` = the file created by `tempfile.NamedTemporaryFile(..., delete=False)`, `tempfile.mkstemp()` or `tempfile.mkdtemp()` in place of the chosen name, `rationale` = another process can create a file at a predictable or not-yet-created name before the program does and so control what the program reads or writes).

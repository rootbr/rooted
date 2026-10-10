---
title: The common directory of several paths is computed with os.path.commonpath, never os.path.commonprefix, which compares character by character and can return an invalid path
rule_id: PY-40
domain: code
step: [implement, review]
applies_to: [python]
triggers: ['\bos[.]path[.]commonprefix\(', '(?<![.\w])commonprefix\(']
scope: hunk
check_kind: mechanical
severity_default: major
---

# The common directory of several paths is computed with os.path.commonpath, never os.path.commonprefix, which compares character by character and can return an invalid path

## Thesis
Code that needs the common directory of several file-system paths calls os.path.commonpath, which returns the longest common sub-path as a valid path, and never os.path.commonprefix, which returns the longest string prefix taken character by character.

## Rationale
os.path.commonprefix compares strings character by character rather than path components, so for /usr/lib and /usr/local/lib it returns /usr/l, which is not a valid directory; it may return invalid paths, and for a common path prefix its algorithm is not secure. It is deprecated from Python 3.15 in favour of os.path.commonpath for path prefixes, because its name and its module mislead: it is not safe to use for path prefixes despite being included in a module about path manipulation, which makes it easy to introduce path traversal vulnerabilities by accident. os.path.commonpath compares path components and returns /usr for the same pair.

## Example
```python
bad:  root = os.path.commonprefix(["/usr/lib", "/usr/local/lib"])
      base = commonprefix([src_dir, build_dir])
good: root = os.path.commonpath(["/usr/lib", "/usr/local/lib"])
      base = commonpath([src_dir, build_dir])
```

## Limits
A commonprefix call over strings that are not paths, such as version numbers or identifiers, is outside the rule; there the two functions differ, as commonprefix gives "123" for "12345" and "12378" where commonpath gives "". The replacement changes the error behaviour as well: commonpath raises ValueError if the paths contain both absolute and relative pathnames, lie on different drives, or are empty, where commonprefix returns the empty string for an empty list, so a call site that can receive such input meets an exception where it used to receive a string.

## Validator
Grep the hunk for os.path.commonprefix( and for a bare commonprefix( imported from os.path. Open the call and trace its argument to where the list is built: values from directory listings, Path objects, path joins, configuration of directories or names such as path, dir, file or root mark file-system paths; version strings, identifiers and other plain strings do not. Validator question: **Does this commonprefix call compute a common prefix of file-system paths?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-40`, severity major, `file`, `symbol`, `code` = the commonprefix call, quoted verbatim from the diff, `fix` = the same call with os.path.commonpath, e.g. `os.path.commonpath(["/usr/lib", "/usr/local/lib"])`, with ValueError handled where the input can mix absolute and relative paths or be empty, `rationale` = commonprefix compares character by character, returns /usr/l for /usr/lib and /usr/local/lib, is not secure for a common path prefix and is deprecated from Python 3.15).

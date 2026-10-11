---
title: A URL the program did not write as a literal is checked for an allowed scheme such as http or https before urllib.request opens it, because the default opener also serves file and ftp URLs
rule_id: PY-100
domain: input
step: [implement, review]
applies_to: [python, service-boundary]
triggers: ['\burlopen\((?!\s*[\x22\x27])', '\burlretrieve\((?!\s*[\x22\x27])', 'urllib[.]request[.]Request\((?!\s*[\x22\x27])']
scope: file
check_kind: semantic
severity_default: major
---

# A URL the program did not write as a literal is checked for an allowed scheme such as http or https before urllib.request opens it, because the default opener also serves file and ftp URLs

## Thesis
In Python, before a URL that the program did not write as a string literal reaches `urllib.request.urlopen`, `urllib.request.urlretrieve` or a `urllib.request.Request` they open, the code checks that the URL's scheme is one the program permits, such as `http:` or `https:`, and rejects every other scheme, among them `file:`, `ftp:` and custom schemes.

## Rationale
`urllib.request.build_opener` puts instances of `ProxyHandler` (if proxy settings are detected), `UnknownHandler`, `HTTPHandler`, `HTTPDefaultErrorHandler`, `HTTPRedirectHandler`, `FTPHandler`, `FileHandler` and `HTTPErrorProcessor` in front of the handlers it is given, unless those handlers contain them, instances of them or subclasses of them. `urlopen` returns a `urllib.response.addinfourl` object for FTP, file and data URLs, so the call that fetches a web page also opens an `ftp:` or a `file:` URL. `FileHandler.file_open` opens the file locally when the URL has no host name or the host name is `'localhost'`, and raises `URLError` when a remote host name is given. Some URL open functions allow `file:` or custom schemes in place of `http:` or `https:`; an attacker may be able to use these schemes to access or modify unauthorized resources and cause unexpected behavior, and allowing `file:` or custom schemes is often unexpected. A check of the scheme against the permitted set before the call ensures that only permitted schemes are used.

## Example
```python
bad:  with urllib.request.urlopen(url) as resp:
          body = resp.read()
good: if urllib.parse.urlsplit(url).scheme not in ("http", "https"):
          raise ValueError("url must use http or https")
      with urllib.request.urlopen(url) as resp:
          body = resp.read()
```

## Limits
A URL the program writes as a string literal shows its scheme in the source and is outside the rule; one position likewise allows the `http` and `https` schemes when the `url` argument of `urlopen`, `urlretrieve` or `Request` is a string literal, including one reached through a resolved binding.

## Validator
Grep the hunk for `urlopen(`, `urlretrieve(` and `urllib.request.Request(` calls whose first argument is not a string literal. For each, open the file and trace the URL argument back to where its value is set: a string literal of the program, directly or through a name bound once to a literal, ends the trace with no finding. When the value comes from input, configuration, a request, a database, a function parameter or a computed string, look on the path from that source to the call for a check that reads the URL's scheme (`urllib.parse.urlsplit(url).scheme`, `urllib.parse.urlparse(url).scheme` or `url.startswith(("http:", "https:"))`) and rejects every scheme outside a permitted set; a check that rejects only `file:` leaves custom schemes open and does not count. Validator question: **Does a URL that the program did not write as a string literal reach `urllib.request.urlopen`, `urlretrieve` or a `Request` they open with no check on its path that rejects every scheme outside a permitted set such as `http` and `https`?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-100`, severity major, `file`, `symbol`, `code` = the `urlopen`, `urlretrieve` or `Request` call quoted verbatim from the diff, `fix` = the scheme check placed before the call, in Python, such as `if urllib.parse.urlsplit(url).scheme not in ("http", "https"): raise ValueError(...)`, `rationale` = where the URL's value comes from and that urllib.request's default opener also opens `file:` and `ftp:` URLs).

## Source
- Ruff S310 suspicious-url-open-usage (astral-sh/ruff crates/ruff_linter/src/rules/flake8_bandit/rules/suspicious_function_call.rs) — 'Some URL open functions allow the use of `file:` or custom schemes (for use instead of `http:` or `https:`). An attacker may be able to use these schemes to access or modify unauthorized resources, and cause unexpected behavior.' (fetched)
- Ruff S310 suspicious-url-open-usage (astral-sh/ruff crates/ruff_linter/src/rules/flake8_bandit/rules/suspicious_function_call.rs) — 'audit all uses of URL open functions and ensure that only permitted schemes are used (e.g., allowing `http:` and `https:`, and disallowing `file:` and `ftp:`).' (fetched)
- astral-sh/ruff crates/ruff_linter/src/rules/flake8_bandit/rules/suspicious_function_call.rs §S310 implementation (astral-sh/ruff crates/ruff_linter/src/rules/flake8_bandit/rules/suspicious_function_call.rs) — 'If the `url` argument is a string literal (including resolved bindings), allow `http` and `https` schemes.' (fetched)
- Bandit B310 urllib_urlopen (PyCQA/bandit bandit/blacklists/calls.py) — "Audit url open for permitted schemes. Allowing use of 'file:'' or custom schemes is often unexpected." (fetched)
- CPython Doc/library/urllib.request.rst §build_opener (python/cpython Doc/library/urllib.request.rst) — 'Instances of the following classes will be in front of the *handler*\s, unless the *handler*\s contain them, instances of them or subclasses of them: :class:`ProxyHandler` (if proxy settings are detected), :class:`UnknownHandler`, :class:`HTTPHandler`, :class:`HTTPDefaultErrorHandler`, :class:`HTTPRedirectHandler`, :class:`FTPHandler`, :class:`FileHandler`, :class:`HTTPErrorProcessor`.' (fetched)
- CPython Doc/library/urllib.request.rst §urlopen (python/cpython Doc/library/urllib.request.rst) — 'For FTP, file, and data URLs, this function returns a :class:`urllib.response.addinfourl` object.' (fetched)
- CPython Doc/library/urllib.request.rst §FileHandler Objects (python/cpython Doc/library/urllib.request.rst) — "Open the file locally, if there is no host name, or the host name is ``'localhost'``." (fetched)
- CPython Doc/library/urllib.request.rst §FileHandler Objects (python/cpython Doc/library/urllib.request.rst) — 'When a remote hostname is given, a :exc:`~urllib.error.URLError` is raised.' (fetched)

---
title: An archive the program did not build is extracted by tarfile with filter='data' while Python 3.13 or older is supported, or with inspected members where filters are missing, and not with filter='fully_trusted'
rule_id: PY-98
domain: input
step: [implement, review]
applies_to: [python]
triggers: ['[.]extractall\(', '[.]extract\(', 'filter\s*=\s*["'']fully_trusted["'']', 'tarfile[.]open\(']
scope: file
check_kind: semantic
severity_default: major
---

# An archive the program did not build is extracted by tarfile with filter='data' while Python 3.13 or older is supported, or with inspected members where filters are missing, and not with filter='fully_trusted'

## Thesis
Python code that extracts an archive it did not build with TarFile.extractall or TarFile.extract passes filter='data' wherever the project supports Python 3.13 or lower; on an interpreter without extraction filters it passes extractall a members function that inspects each member and discards directory traversal sequences and special file types unless they are explicitly needed; and it passes filter='fully_trusted' only for an archive the user trusts completely or that the code verifies itself.

## Rationale
Extracting a tar file can overwrite arbitrary files in various ways, for example by using absolute paths, .. path components, or symlinks that affect later members. The filter argument of TarFile.extract and TarFile.extractall decides how members are modified or rejected before extraction: 'fully_trusted' honours all metadata as specified in the archive, and 'data' ignores or blocks most features specific to UNIX-like filesystems and is intended for extracting cross-platform data archives. When both the filter argument and TarFile.extraction_filter are None, Python 3.12 and 3.13 emit a DeprecationWarning and extract with the 'fully_trusted' filter, and Python 3.14 and later use 'data', which disallows some dangerous features such as links to absolute paths or paths outside of the destination. Extraction filters were added to Python 3.12 but may be backported to older versions as security updates; a backport keeps 'fully_trusted' as its default, because CPython adds no warnings to patch releases, and hasattr(tarfile, 'data_filter') rather than the Python version tells whether the feature is available. The filter is therefore set explicitly only if specific tar features are required, or as filter='data' to support Python versions with a less secure default (3.13 and lower). Where filters are missing, one remedy sets the members argument to a trusted subset of the archive's members, and another defines a members function that inspects each member and discards files that contain directory traversal sequences such as ../ or \.. along with all special file types unless they are explicitly needed.

## Example
```python
bad:  archive = tarfile.open(upload_path)
      archive.extractall(dest_dir)
      archive.extract(member, dest_dir, filter="fully_trusted")
good: archive = tarfile.open(upload_path)
      archive.extractall(dest_dir, filter="data")
      archive.extract(member, dest_dir, filter="data")
```

## Limits
filter='fully_trusted' is the choice where the user trusts the archive completely or the code implements its own complex verification. A project whose supported versions are all Python 3.14 or later gets 'data' as the default filter, so a call there without filter is outside this rule. The filter is not the whole defence, and this rule does not check the rest: none of the available filters blocks all dangerous archive features, even with filter='data' tarfile is not suited for extracting untrusted files without prior inspection, and the pre-defined filters do not prevent denial-of-service attacks; further checks are needed, among them extracting to a new temporary directory and limiting the number of extracted files, the total size of extracted data and the size of individual files.

## Validator
Grep the file for `.extractall(` and `.extract(` on a TarFile (a tarfile.open result or a TarFile instance; a zipfile call is not this rule), for filter='fully_trusted', and for assignments to extraction_filter. Read the supported Python versions where the file or the diff shows them (a requires-python or python_requires line, a trove classifier, a sys.version_info branch around the call); where none is visible, the call counts as supporting Python 3.13 or lower, the case that calls for filter="data". Trace where the archive comes from. The first case is an archive the program did not build (an upload, a download, a path a user supplies) extracted while a supported version is 3.13 or lower with no filter='data', no filter=tarfile.data_filter and no extraction_filter set to tarfile.data_filter, and, on an interpreter without filters, no members function that inspects each member. The second case is filter='fully_trusted' on such an archive while nothing in the code verifies it or establishes that the user trusts it completely. Validator question: **Does the file extract with tarfile an archive the program did not build without the 'data' filter while Python 3.13 or lower is supported (and, where filters are missing, without a members function that inspects each member), or with filter='fully_trusted' for an archive it neither verifies nor completely trusts?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-98`, severity major, `file`, `symbol`, `code` = the extractall or extract call with the tarfile.open it reads from, verbatim from the diff, `fix` = the same call with `filter="data"`, or with `members=` a function that inspects each member where filters are missing, `rationale` = without a filter Python 3.12 and 3.13 extract with 'fully_trusted', so absolute paths, .. components and symlinks in the archive can overwrite files outside the destination).

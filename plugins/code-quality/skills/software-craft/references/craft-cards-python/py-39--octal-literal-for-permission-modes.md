---
title: A numeric permission mode passed to os.chmod, os.mkdir, os.makedirs, os.open, os.umask or a pathlib chmod, mkdir or touch call is a 0o-prefixed octal literal, except a plain 0
rule_id: PY-39
domain: code
step: [implement, review]
applies_to: [python]
triggers: ['\bos[.](chmod|fchmod|lchmod|mkdir|makedirs|open|umask)\(.*\b[1-9]\d{2,3}\b', '[.](chmod|mkdir|touch)\(.*\bmode\s*=\s*[1-9]\d{2,3}\b', '[.]chmod\(\s*[1-9]\d{2,3}\s*\)']
scope: hunk
check_kind: mechanical
severity_default: major
---

# A numeric permission mode passed to os.chmod, os.mkdir, os.makedirs, os.open, os.umask or a pathlib chmod, mkdir or touch call is a 0o-prefixed octal literal, except a plain 0

## Thesis
An integer literal passed as the permission mode to os.chmod, os.fchmod, os.lchmod, os.mkdir, os.makedirs, os.open, os.umask or the chmod, mkdir or touch method of a pathlib.Path is written with the 0o prefix, as in 0o755; the single digit 0 may stand without it.

## Rationale
Numeric modes are made up of one to four octal digits, which describe user, group and other permissions in base 8. When the same digits are written without the 0o prefix, Python treats them as decimal: os.chmod(path, 755) applies decimal 755, which is octal 0o1363, not the common executable mode 0o755, and 644 corresponds to 0o1204 rather than 0o644. The chmod command reads 755 as octal, so the digits that are right at the command line are wrong in Python. The resulting mode is not the permission set the author usually intends: files or directories may be more or less accessible than intended, secrets or configuration files can end up readable or writable by unintended users, and scripts or services may fail when an expected execute or write bit is missing. The literal 0 is clear on its own and does not need an octal prefix.

## Example
```python
bad:  os.chmod(script_path, 755)
      Path(cache_dir).mkdir(mode=700, parents=True)
      Path(config_path).chmod(644)
good: os.chmod(script_path, 0o755)
      Path(cache_dir).mkdir(mode=0o700, parents=True)
      Path(config_path).chmod(0o644)
```

## Limits
The rule covers integer literals passed as the mode; a mode held in a name or built from stat constants is outside it. Zero may omit the prefix only as the single digit 0: a multi-digit zero such as 000 is still flagged and written 0o000. A decimal literal can name a likely mode on purpose, as 493 is 0o755 and 256 is 0o400, and rewriting it as that octal literal keeps the runtime behaviour unchanged; intentional decimal mode literals are rare, and one is kept as decimal only after review confirms the decimal value is deliberate rather than a mistaken octal.

## Validator
Grep the hunk for os.chmod, os.fchmod, os.lchmod, os.mkdir, os.makedirs, os.open, os.umask and the chmod, mkdir and touch methods of a Path, and find the argument that carries the mode: the second positional argument of os.chmod, os.fchmod, os.lchmod, os.mkdir and os.makedirs, the third of os.open, the only one of os.umask and Path.chmod, the first or mode= of Path.mkdir and Path.touch. Skip a mode that is a name, an expression of stat constants, a 0o literal or the single digit 0. Validator question: **Is the mode argument an integer literal written without the 0o prefix, other than the single digit 0?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-39`, severity major, `file`, `symbol`, `code` = the call with its mode literal, quoted verbatim from the diff, `fix` = the call with the mode as a 0o literal, e.g. `os.chmod(script_path, 0o755)`, or the 0o form of the same value where review shows a decimal mode was deliberate, `rationale` = Python reads the literal as decimal, so 755 applies 0o1363 rather than the intended 0o755 and leaves the file with permissions the author did not intend).

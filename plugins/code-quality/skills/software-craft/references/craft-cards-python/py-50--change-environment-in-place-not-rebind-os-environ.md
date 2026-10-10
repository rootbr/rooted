---
title: Code that changes the process environment modifies os.environ in place or passes env= to the subprocess, and never assigns a new mapping to os.environ
rule_id: PY-50
domain: design
step: [implement, review]
applies_to: [python]
triggers: ['\bos[.]environ\s*=(?!=)', '\benviron\s*=\s*(\{|dict\()']
scope: hunk
check_kind: mechanical
severity_default: major
---

# Code that changes the process environment modifies os.environ in place or passes env= to the subprocess, and never assigns a new mapping to os.environ

## Thesis
Python code that changes the process environment modifies the `os.environ` mapping in place, by item assignment, `update`, `del`, `pop` or `clear`, or passes a custom environment to a subprocess through the `env` argument of `subprocess.Popen`, and assigns no new object to `os.environ`.

## Rationale
`os.environ` is a mapping that represents the process environment, and it may be used to modify the environment as well as to query it: `putenv` is called automatically when the mapping is modified, and `unsetenv` when an item is deleted or when `pop` or `clear` is called. Reassigning `os.environ` does not clear the environment; it merely updates `os.environ` for the current process, so subprocesses see outdated variables, in disagreement with the current process. Calling `putenv` directly does not change `os.environ`, which is why the documentation advises modifying `os.environ`.

## Example
```python
bad:  os.environ = {"PATH": "/usr/bin"}
      subprocess.run(["make"])
good: subprocess.run(["make"], env={**os.environ, "PATH": "/usr/bin"})
      os.environ["PATH"] = "/usr/bin"  # when the process itself needs it
```

## Limits
The rule concerns assignment to `os.environ`; reading the mapping stays outside it. To empty the environment, `os.environ.clear()` does it in place. The documentation notes that on some platforms, including FreeBSD and macOS, setting `environ` may cause memory leaks, and refers to the system documentation for `putenv`.

## Validator
Grep the hunk for `os.environ =` that is not a comparison, and for `environ = {` or `environ = dict(`. For a bare `environ =` match, trace whether the target is the `os` module's `environ` reached through an alias (`import os as o`, then `o.environ = {...}`); an unrelated local name passes. Open the enclosing function to see whether a subprocess call follows the assignment. Validator question: **Does the hunk assign a new object to the `os` module's `environ` attribute?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-50`, severity major, `file`, `symbol`, `code` = the assignment to `os.environ`, verbatim, `fix` = the change made in place, such as `os.environ["PATH"] = "/usr/bin"` or `os.environ.clear()` followed by item assignments, or the subprocess call with `env={**os.environ, "PATH": "/usr/bin"}`, `rationale` = reassigning `os.environ` does not clear the environment, so subprocesses see outdated variables).

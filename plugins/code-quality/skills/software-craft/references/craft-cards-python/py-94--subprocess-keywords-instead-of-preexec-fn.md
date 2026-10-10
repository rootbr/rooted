---
title: A subprocess call uses env, start_new_session or process_group instead of a preexec_fn that sets the environment, session or process group, and passes no preexec_fn at all in an application that runs threads
rule_id: PY-94
domain: errors
step: [implement, review]
applies_to: [python]
triggers: ['\bpreexec_fn\s*=', '\bos[.](?:setsid|setpgrp|setpgid)\b']
scope: hunk
check_kind: mechanical
severity_default: major
---

# A subprocess call uses env, start_new_session or process_group instead of a preexec_fn that sets the environment, session or process group, and passes no preexec_fn at all in an application that runs threads

## Thesis
A Python `subprocess` call modifies the child's environment through `env` and makes the child call `setsid()` or `setpgid()` through `start_new_session` or `process_group`, not through a `preexec_fn` that changes the environment or calls `os.setsid` or `os.setpgid`; in an application that runs threads, it passes no `preexec_fn` at all.

## Rationale
A `preexec_fn` callable is called in the child process just before the child is executed (POSIX only). The `preexec_fn` parameter is not safe to use in the presence of threads in the application: the child process could deadlock before exec is called. The `env` parameter takes the place of an environment change made in a `preexec_fn`; `start_new_session=True` makes the `setsid()` system call in the child process prior to the execution of the subprocess, and `process_group` set to a non-negative integer makes the `setpgid(0, value)` system call there; these task-specific arguments are not prone to deadlocks and are more explicit. `preexec_fn` is also targeted for deprecation, and it is no longer supported in subinterpreters, where its use raises `RuntimeError`.

## Example
```python
bad:  subprocess.Popen(cmd, preexec_fn=os.setsid)
      subprocess.Popen(cmd, preexec_fn=lambda: os.setpgid(0, 0))
good: subprocess.Popen(cmd, start_new_session=True)
      subprocess.Popen(cmd, process_group=0)  # Python 3.11 and later
      subprocess.Popen(cmd, env={**os.environ, "LANG": "C"})
```

## Limits
`process_group` was added in Python 3.11, so the keyword replacement for a `preexec_fn` that calls `os.setpgid` needs Python 3.11 or later. Where a `preexec_fn` must be used for work that `env`, `start_new_session` and `process_group` do not cover, it is kept trivial and calls into as few libraries as possible; in the presence of threads the child process could still deadlock before exec is called.

## Validator
Grep the hunk for `preexec_fn=` in calls to `subprocess.Popen`, `subprocess.run`, `subprocess.call`, `subprocess.check_call` or `subprocess.check_output`. Read the callable passed: a call to `os.setsid`, `os.setpgid` or `os.setpgrp`, or a change to `os.environ`, has a keyword replacement. For any other callable, search the application for `threading.Thread`, `concurrent.futures.ThreadPoolExecutor` or a server that runs worker threads, to settle whether it runs threads. Validator question: **Does a subprocess call in the hunk pass a `preexec_fn` that sets the child's session, process group or environment, or pass any `preexec_fn` in an application that runs threads?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-94`, severity major, `file`, `symbol`, `code` = the subprocess call with its `preexec_fn=` argument, `fix` = the call with `start_new_session=True`, `process_group=0` (Python 3.11 and later) or `env={...}` in place of the `preexec_fn`, `rationale` = that `preexec_fn` is not safe in the presence of threads, where the child process could deadlock before exec is called, and that a keyword argument does the same work).

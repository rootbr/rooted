---
title: A Python copy of os.environ is made with os.environ.copy(), never with copy.copy(os.environ), whose mutations still change the process environment
rule_id: PY-152
domain: code
step: [implement, review]
applies_to: [python]
triggers: ['\bcopy[.]copy\s*\(\s*os[.]environ\b', '\bcopy\s*\(\s*(os[.])?environ\s*\)']
scope: hunk
check_kind: mechanical
severity_default: major
---

# A Python copy of os.environ is made with os.environ.copy(), never with copy.copy(os.environ), whose mutations still change the process environment

## Thesis
A Python copy of the process environment is made with `os.environ.copy()`, never by passing `os.environ` to the copy module's `copy` function, because `os.environ` is a proxy object and item assignments to its shallow copy still change the process environment.

## Rationale
`os.environ` is not a dict object but a proxy object over the process environment: assignments to its items are automatically translated into calls to `putenv`, and such changes to the environment affect subprocesses started with `os.system`, `popen`, or `fork` and `execv`. `copy.copy(os.environ)` makes a shallow copy of that proxy, and mutating the shallow copy also mutates the original object, so an item set on what the code treats as a private copy reaches the environment of the process and of the subprocesses it starts.

## Example
```python
bad:  env = copy.copy(os.environ)
      env["DEBUG"] = "1"
      subprocess.run(command, env=env)
good: env = os.environ.copy()
      env["DEBUG"] = "1"
      subprocess.run(command, env=env)
```

## Limits
The rule covers every `copy.copy` of `os.environ`, whether or not the hunk already assigns to the copy, since any later item assignment to the shallow copy also mutates the original. Replacing the call with `os.environ.copy()` may prevent modifications of the copy from affecting the original data, so code that relied on that write-through may change behaviour; such code assigns to items of `os.environ` itself, which is preferable to calling `putenv` directly.

## Validator
Grep the hunk for `copy.copy(` or a bare `copy(` whose argument is `os.environ` or a name `environ`; open the file's imports to confirm that `copy` is the copy module's `copy` function and that `environ` is `os.environ`. Validator question: **Does the hunk pass `os.environ` to the copy module's `copy` function?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-152`, severity major, `file`, `symbol`, `code` = the copy call on `os.environ` verbatim from the diff, `fix` = `env = os.environ.copy()`, `rationale` = names that `os.environ` is a proxy whose item assignments become `putenv` calls, so its shallow copy still writes to the process environment).

## Source
- Ruff PLW1507 shallow-copy-environ (astral-sh/ruff crates/ruff_linter/src/rules/pylint/rules/shallow_copy_environ.rs) — '`os.environ` is not a `dict` object, but rather, a proxy object. As such, mutating a shallow copy of `os.environ` will also mutate the original object.'; 'If the program modifies the shallow copy at some point, changing it to a deep copy may prevent those modifications from affecting the original data' (fetched)
- Pylint shallow-copy-environ (W1507) (pylint-dev/pylint pylint/checkers/stdlib.py) — 'Using copy.copy(os.environ). Use os.environ.copy() instead.'; 'os.environ is not a dict object but proxy object, so shallow copy has still effects on original object.' (fetched)
- CPython Doc/library/os.rst §putenv and §os.environ (https://raw.githubusercontent.com/python/cpython/main/Doc/library/os.rst) — 'Such changes to the environment affect subprocesses started with :func:`os.system`, :func:`popen` or :func:`fork` and :func:`execv`.'; 'Assignments to items in :data:`os.environ` are automatically translated into corresponding calls to :func:`putenv`'; 'so it is actually preferable to assign to items of :data:`os.environ`' (fetched)

---
title: A build, install or test command in a script, CI job or Makefile runs python -m build or pip and never a python setup.py command such as install, develop, sdist, bdist_wheel or test
rule_id: PY-109
domain: tooling
step: [implement, review]
applies_to: [python, build-config]
triggers: ['setup[.]py\s+(install|develop|sdist|bdist_wheel|bdist_egg|test|upload)\b', '["'']setup[.]py["'']\s*,\s*["''](install|develop|sdist|bdist_wheel|test)["'']']
scope: hunk
check_kind: mechanical
severity_default: major
---

# A build, install or test command in a script, CI job or Makefile runs python -m build or pip and never a python setup.py command such as install, develop, sdist, bdist_wheel or test

## Thesis
A command that a script, a CI job, a Makefile, a Dockerfile or a subprocess call runs to build, install or test a Python project builds the sdist and the wheel with `python -m build`, installs with `python -m pip install .` (or `python -m pip install --editable .` for an editable install), and invokes no `python setup.py <command>` — neither `install`, `develop`, `sdist`, `bdist_wheel` and `test` nor any other setuptools command.

## Rationale
Running `python setup.py` and using `setup.py` as a command line tool are deprecated: on recent versions of setuptools, running `python setup.py` directly as a script is considered deprecated, and commands run directly via `python setup.py <command>` are to be avoided. `python setup.py install`, `python setup.py develop`, `python setup.py sdist` and `python setup.py bdist_wheel` are named as commands that must not be run anymore. The documented replacements are `python -m pip install .` for `install`, `python -m pip install --editable .` for `develop`, and `python -m build` for `sdist` and `bdist_wheel`; `python -m build` requires the `build` dependency and builds both the source distribution and the wheel, as recommended for every build and publication of a project. setuptools' `test` command is deprecated and will be removed in a future version.

## Example
```python
bad:  subprocess.run(["python", "setup.py", "sdist", "bdist_wheel"], check=True)
      subprocess.run(["python", "setup.py", "install"], check=True)
good: subprocess.run([sys.executable, "-m", "build"], check=True)
      subprocess.run([sys.executable, "-m", "pip", "install", "."], check=True)
```

## Limits
Writing a `setup.py` file to configure a package build — for example to specify binary extensions or customize commands — stays valid setuptools configuration; the rule reaches the command line that runs `setup.py`, not the file's contents.

## Validator
Grep the hunk for `setup.py` followed by a command name in a shell script, a CI step, a Makefile recipe, a Dockerfile `RUN` line, a tox or nox session, or a subprocess argument list such as `"setup.py", "install"`. Skip a comment, a changelog or prose that names the command without running it, and the body of a `setup.py` file itself. Validator question: **Does an added line run `python setup.py <command>` — `install`, `develop`, `sdist`, `bdist_wheel`, `bdist_egg`, `test`, `upload` or another setuptools command — as a build, install, test or publish step?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-109`, severity major, `file`, `symbol`, `code` = the added line that runs `setup.py` with its command, `fix` = the same step as `python -m build`, `python -m pip install .` or `python -m pip install --editable .`, and for `test` the project's test runner, `rationale` = running `python setup.py <command>` directly is deprecated in setuptools, and the named replacement for that command).

## Source
- PyPA guide discussions/setup-py-deprecated §Is setup.py deprecated? (pypa/packaging.python.org source/discussions/setup-py-deprecated.rst) — 'However, ``python setup.py`` and the use of :file:`setup.py` as a command line tool are deprecated.' (fetched)
- PyPA guide discussions/setup-py-deprecated §Is setup.py deprecated? (pypa/packaging.python.org source/discussions/setup-py-deprecated.rst) — 'This means that commands such as the following **MUST NOT** be run anymore' (fetched); the list names install, develop, sdist and bdist_wheel.
- PyPA guide discussions/setup-py-deprecated §What commands should be used instead? (pypa/packaging.python.org source/discussions/setup-py-deprecated.rst) — '``python -m pip install --editable .``' (fetched); the table cell that replaces `python setup.py develop`.
- PyPA guide discussions/setup-py-deprecated §What commands should be used instead?, footnote needs-build (pypa/packaging.python.org source/discussions/setup-py-deprecated.rst) — 'This requires the :ref:`build` dependency. It is recommended to always build and publish both the source distribution and wheel of a project, which is what ``python -m build`` does.' (fetched); the footnote is attached to the table cell that replaces both `python setup.py sdist` and `python setup.py bdist_wheel` with `python -m build`.
- PyPA guide discussions/setup-py-deprecated, the paragraph after the replacement table (pypa/packaging.python.org source/discussions/setup-py-deprecated.rst) — 'Nowadays, the recommended method is to use :ref:`pip` directly with a command like this one: ``python -m pip install .``.' (fetched)
- setuptools docs/deprecated/commands.rst, the warning before the command reference (pypa/setuptools docs/deprecated/commands.rst) — 'While it is perfectly fine that users write ``setup.py`` files to configure a package build (e.g. to specify binary extensions or customize commands), on recent versions of ``setuptools``, running ``python setup.py`` directly as a script is considered **deprecated**. This also means that users should avoid running commands directly via ``python setup.py <command>``.' (fetched)
- setuptools docs/deprecated/commands.rst §``test`` - Build package and run a unittest suite (pypa/setuptools docs/deprecated/commands.rst) — '``test`` is deprecated and will be removed in a future version.' (fetched)

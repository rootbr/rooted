---
title: A command a Python distribution installs is declared as a console_scripts entry point in [project.scripts] rather than as a pre-made script file in the setup() scripts argument
rule_id: PY-113
domain: tooling
step: [design, implement]
applies_to: [python, build-config]
triggers: ['^\s*scripts\s*=\s*\[\s*["'']', 'setup\(.*[(,]\s*scripts\s*=', '^\s*script-files\s*=', '^\s*\[project[.](scripts|gui-scripts)\]']
scope: hunk
check_kind: semantic
severity_default: minor
---

# A command a Python distribution installs is declared as a console_scripts entry point in [project.scripts] rather than as a pre-made script file in the setup() scripts argument

## Thesis
A command-line command that a Python distribution installs is declared as a `console_scripts` entry point — `name = "module:function"` in the `[project.scripts]` table, or the `console_scripts` group of setuptools' `entry_points` — and a command launched from within a graphical application in `[project.gui-scripts]`, rather than as a pre-made script file listed in the `scripts` keyword of `setup()` or in setuptools' `script-files`.

## Rationale
The `[project.scripts]` table corresponds to the `console_scripts` group of the entry points specification: the key is the entry point's name and the value is the object reference. When pip or another console_scripts-aware installer installs the distribution, it creates a command-line wrapper for each entry point: `spam-cli = "spam:main_cli"` gives a `spam-cli` command that does the equivalent of `import sys; from spam import main_cli; sys.exit(main_cli())`. The referenced function is called with no arguments, may return an integer used as the process exit code, and returning `None` is equivalent to returning `0`. On Windows, `console_scripts` are wrapped in a console executable attached to a console that can use `sys.stdin`, `sys.stdout` and `sys.stderr`, and a script launched from within a graphical application makes a terminal pop up, which `[project.gui-scripts]` prevents. `setup()` supports a `scripts` keyword for pointing to pre-made scripts to install, but the recommended approach to achieve cross-platform compatibility is `console_scripts` entry points; `script-files`, the `pyproject.toml` equivalent of the `scripts` keyword in setuptools, is discouraged, with `project.scripts` to be used whenever possible. A `console_scripts` or `gui_scripts` group written under `[project.entry-points]` is ambiguous with these two tables, and a build back-end raises an error for it.

## Example
```python
bad:  setup(
          name="tool",
          scripts=["bin/tool"],
      )
good: [project.scripts]
      tool = "tool.cli:main"
```

## Limits
Where an entry point is not possible, `script-files` stays available, discouraged, with `project.scripts` asked for whenever possible. A package's `__main__.py` that makes it runnable as `python -m package` is a separate mechanism from an installed command and not a finding.

## Validator
Grep the hunk for a `scripts=` keyword in a `setup()` call, a `scripts =` entry in the `[options]` section of `setup.cfg`, or `script-files` under `[tool.setuptools]`; open each listed file and check whether it is a Python script whose body calls a function of the package. Validator question: **Does the change install a command through `scripts` or `script-files` whose file runs a Python function that a `[project.scripts]` entry point could reference?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-113`, severity minor, `file`, `symbol`, `code` = the `scripts=` or `script-files` line verbatim, `fix` = a `[project.scripts]` entry `name = "package.module:function"` that replaces the script file, `rationale` = installers generate a cross-platform wrapper for each `console_scripts` entry point that passes the function's return value to `sys.exit`, while `scripts` installs the pre-made file as it is).

## Source
- PyPA guide guides/distributing-packages-using-setuptools §setup() args, scripts (pypa/packaging.python.org source/guides/distributing-packages-using-setuptools.rst) — 'keyword for pointing to pre-made scripts to install, the recommended approach to achieve cross-platform compatibility is to use :ref:`console_scripts` entry points (see below).' (fetched)
- PyPA entry points specification, introduction (pypa/packaging.python.org source/specifications/entry-points.rst) — 'Distributions can specify ``console_scripts`` entry points, each referring to a function. When *pip* (or another console_scripts aware installer) installs the distribution, it will create a command-line wrapper for each entry point.' (fetched)
- PyPA entry points specification §Use for scripts (pypa/packaging.python.org source/specifications/entry-points.rst) — 'The object reference points to a function which will be called with no arguments when this command is run. The function may return an integer to be used as a process exit code, and returning ``None`` is equivalent to returning ``0``.' (fetched)
- PyPA entry points specification §Use for scripts (pypa/packaging.python.org source/specifications/entry-points.rst) — 'The difference between ``console_scripts`` and ``gui_scripts`` only affects Windows systems. ``console_scripts`` are wrapped in a console executable, so they are attached to a console and can use :py:data:`sys.stdin`, :py:data:`sys.stdout` and :py:data:`sys.stderr` for input and output.' (fetched)
- PyPA guide guides/writing-pyproject-toml §Creating executable scripts (pypa/packaging.python.org source/guides/writing-pyproject-toml.rst) — 'In this example, after installing your project, a ``spam-cli`` command will be available. Executing this command will do the equivalent of ``import sys; from spam import main_cli; sys.exit(main_cli())``.' (fetched)
- PyPA guide guides/writing-pyproject-toml §Creating executable scripts (pypa/packaging.python.org source/guides/writing-pyproject-toml.rst) — 'On Windows, scripts packaged this way need a terminal, so if you launch them from within a graphical application, they will make a terminal pop up. To prevent this from happening, use the ``[project.gui-scripts]`` table instead of ``[project.scripts]``.' (fetched)
- PyPA pyproject.toml specification §Entry points (pypa/packaging.python.org source/specifications/pyproject-toml.rst) — 'The ``[project.scripts]`` table corresponds to the ``console_scripts`` group in the :ref:`entry points specification <entry-points>`. The key of the table is the name of the entry point and the value is the object reference.' (fetched)
- PyPA pyproject.toml specification §Entry points (pypa/packaging.python.org source/specifications/pyproject-toml.rst) — 'Build back-ends MUST raise an error if the metadata defines a ``[project.entry-points.console_scripts]`` or ``[project.entry-points.gui_scripts]`` table, as they would be ambiguous in the face of ``[project.scripts]`` and ``[project.gui-scripts]``, respectively.' (fetched)
- setuptools docs/userguide/pyproject_config.rst, the [tool.setuptools] key table, script-files row (pypa/setuptools docs/userguide/pyproject_config.rst) — '**Discouraged** - equivalent to the ``script`` keyword in ``setup.py``. Whenever possible, please use ``project.scripts`` instead.' (fetched)
- setuptools docs/userguide/entry_point.rst §Console Scripts (pypa/setuptools docs/userguide/entry_point.rst) — 'Instead of this approach using ``__main__.py``, you can also create a user-friendly CLI executable that can be called directly without ``python -m``.' (fetched)

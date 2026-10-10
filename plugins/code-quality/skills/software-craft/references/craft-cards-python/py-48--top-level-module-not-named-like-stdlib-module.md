---
title: A top-level module or package the project adds does not take the name of a standard-library module
rule_id: PY-48
domain: design
step: [design, review]
applies_to: [python]
triggers: ['signal:added_file']
scope: file
check_kind: mechanical
severity_default: major
---

# A top-level module or package the project adds does not take the name of a standard-library module

## Thesis
A module or package that a change adds at the top level of a Python project's import tree, its path taken relative to the project root or a `src` directory (`logging.py`, `logging/__init__.py`), has a name that no standard-library module has.

## Rationale
When a module is imported, Python first searches the built-in modules listed in `sys.builtin_module_names` and then the directories in `sys.path`; the directory containing the script being run is placed at the beginning of that path, ahead of the standard library path, so a module in that directory is loaded and a library module of the same name is not, which is an error unless the replacement is intended. Apart from the import, reusing a standard-library module name increases the difficulty of reading and maintaining the code and can cause non-obvious errors: readers may mistake the first-party module for the standard-library module and vice versa.

## Example
```python
bad:  # random.py, new at the project root
      import random
      def roll():
          return random.choice(range(1, 7))
good: # dice.py, new at the project root
      import random
      def roll():
          return random.choice(range(1, 7))
```

## Limits
Only the path relative to the project root or `src` directories counts, so a top-level `logging.py` or `logging/__init__.py` clashes with the standard `logging` module while a nested `utils/logging.py` passes; a project that sets the `lint.flake8-builtins.strict-checking` option considers only the last component of the module name, which flags the nested module too. A project marks standard-library names it accepts through the `lint.flake8-builtins.allowed-modules` option. Stub files are exempt, as the name of a stub module is out of the control of the author of the stub file. An intended replacement of a library module is not an error.

## Validator
For each file the diff adds, take its path relative to the project root or the `src` directory and its first component, `name.py` or `name/__init__.py`, and compare `name` with `sys.stdlib_module_names`, leaving out the names the project lists in `allowed-modules`; skip `.pyi` stub files. Validator question: **Does the change add a top-level module or package, outside a stub file and outside the project's allowed modules, whose name equals a standard-library module name?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-48`, severity major, `file`, `symbol`, `code` = the added module's path, verbatim, `fix` = the module renamed for its job, such as `random.py` to `dice.py`, with the imports of it updated, `rationale` = the standard-library module the name hides or makes a reader mistake).

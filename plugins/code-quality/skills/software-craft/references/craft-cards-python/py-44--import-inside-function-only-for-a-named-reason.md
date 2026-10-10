---
title: An import statement inside a function or class body is there only to avoid a circular dependency, defer a costly module load or keep a dependency unloaded in some runtime environment
rule_id: PY-44
domain: design
step: [implement, review]
applies_to: [python]
triggers: ['^\s+import\s+[\w.]+', '^\s+from\s+[\w.]+\s+import\s']
scope: file
check_kind: semantic
severity_default: minor
---

# An import statement inside a function or class body is there only to avoid a circular dependency, defer a costly module load or keep a dependency unloaded in some runtime environment

## Thesis
A Python import statement stands at the top level of its module. An import inside a function or class body stays there only for one of the reasons that typically place an import within a function: to avoid a circular dependency, to defer a costly module load, or to avoid loading a dependency altogether in a certain runtime environment; an import placed there for none of these moves to the top of the file.

## Rationale
Import statements have effects that are global in scope. An import statement is executed where it stands: it finds the module, loading and initializing it if necessary, and defines a name in the current namespace for the scope where the statement occurs, so an import inside a function body loads its module and binds a local name when that function runs. An import at the top level makes it easier to identify the dependencies of a module and ensures that any invalid import is caught regardless of whether a specific function is called or class is instantiated.

## Example
```python
bad:  def report_version():
          import sys
          from platform import python_version
          print(python_version(), file=sys.stderr)
good: import sys
      from platform import python_version
      def report_version():
          print(python_version(), file=sys.stderr)
```

## Limits
The placement is contested. The stricter position reports an import statement used anywhere other than the module top level, says to move it to the top of the file and holds that imports are always put at the top of the file; it names no exception for a function body. The other position names the three reasons an import statement would typically be placed within a function: to avoid a circular dependency, to defer a costly module load, or to avoid loading a dependency altogether in a certain runtime environment. The separating condition is that reason: an import inside a function or class body that serves one of the three stays, one that serves none goes to the top of the file. The rule judges where the import stands, not the circular dependency an import inside a function avoids.

## Validator
Grep the hunk for an indented `import` or `from ... import` line. Open the enclosing block and confirm it is a def or class body; an import inside a module-level `if`, `try` or `with` block is at the top level. Then trace the reason in the file: a comment at the import or an `except ImportError` guard naming it, a module whose own imports reach back to this file (a circular dependency), a module costly to load used only in a function off the module's import-time path (a deferred load), or a dependency optional or absent in some runtime environment (a guarded or extra dependency). Validator question: **Does an import inside a function or class body serve none of the three reasons, avoiding a circular dependency, deferring a costly module load, avoiding loading a dependency in a certain runtime environment?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-44`, severity minor, `file`, `symbol` = the enclosing function or class, `code` = the import line inside the body verbatim from the diff, `fix` = the import moved into the module's import block at the top of the file, `rationale` = names that none of the three reasons applies, and that a top-level import shows the module's dependency and is caught as invalid whether or not the function is called).

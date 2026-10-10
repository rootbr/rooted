---
title: A def, class or import does not rebind a name that an earlier def, class or import of the same scope bound and nothing read in between
rule_id: PY-45
domain: design
step: [implement, test, review]
applies_to: [python]
triggers: ['^\s*(async\s+)?def\s+\w+\s*\(', '^\s*class\s+\w+', '^\s*import\s+[\w.]+(\s+as\s+\w+)?\s*$', '^\s*from\s+[\w.]+\s+import\s+.*\bas\s+\w+']
scope: file
check_kind: semantic
severity_default: major
---

# A def, class or import does not rebind a name that an earlier def, class or import of the same scope bound and nothing read in between

## Thesis
Within one Python module, class body or function body, each `def`, `class` and `import` statement binds a name that no earlier `def`, `class` or `import` of that scope bound and left unused; a later one that redefines such an unused name, such as a duplicated method or test, a module imported more than once, or an import alias that shadows another import, is the finding.

## Rationale
A function definition is an executable statement whose execution binds the function name in the current local namespace to a function object; a class definition binds the class name to the class object in the original local namespace; an import binds the module's name, or the name following `as`, in the current namespace just as an assignment statement would. A name that is already bound is rebound, so the later statement replaces the earlier binding and the earlier function, class or module is no longer reachable by that name. In a class body the saved local namespace becomes the class's attribute dictionary, so of two methods with one name only the later remains on the class. Redefinitions of unused names are unnecessary and often indicative of a mistake.

## Example
```python
bad:  import json
      from fastjson import codec as json
      class RefundTest(unittest.TestCase):
          def test_rejected(self): ...
          def test_rejected(self): ...
good: import json
      from fastjson import codec as fast_json
      class RefundTest(unittest.TestCase):
          def test_rejected_when_expired(self): ...
          def test_rejected_when_partial(self): ...
```

## Limits
A definition whose decorator reads the earlier binding does not redefine an unused name: decorator expressions are evaluated when the function is defined, in the scope that contains the definition, and only their returned value is bound to the function name, so `@value.setter` on a second `def value` reads the property `value` first. `@overload`-decorated definitions are for the benefit of the type checker only and are overwritten by the non-`@overload` definition. A plain reassignment of a variable, `count = 1` followed by `count = 2`, is outside the rule, while a stricter, still experimental position also flags annotated variable redeclarations such as `count: int = 1` followed by `count: int = 2`. Dummy variables, the names matching `lint.dummy-variable-rgx`, are ignored.

## Validator
Grep the hunk for `def`, `class`, `import` and `import ... as` lines and note each name they bind. Open the enclosing scope (the module, the class body or the function body) and search it for an earlier `def`, `class` or `import` binding the same name. Trace the code between the two: a call, an attribute access, a decorator such as `@name.setter`, or any other expression reading the name means it was used. Pass over `@overload`-decorated definitions and two bindings on alternative branches of an `if` or a `try`/`except ImportError`, where only one runs. Validator question: **Does a def, class or import statement bind a name that an earlier def, class or import of the same scope bound on the same path, with no read of that name in between?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-45`, severity major, `file`, `symbol` = the rebound name, `code` = both binding lines verbatim from the diff, `fix` = the duplicate removed, the second definition renamed for what it does differently, as `test_rejected_when_expired` and `test_rejected_when_partial`, or the shadowing import given its own alias, `rationale` = names that the later binding replaces the earlier one, which is then unreachable by that name).

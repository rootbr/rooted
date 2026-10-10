---
title: A Python statement never consists of a bare comparison, name, attribute, subscript, arithmetic expression or collection literal whose value is discarded
rule_id: PY-144
domain: code
step: [implement, review]
applies_to: [python]
triggers: ['^\s*[A-Za-z_][\w.\[\]]*\s*(==|!=|<|>|<=|>=)\s*[^=]', '^\s*(?!(?:pass|break|continue|return|raise|yield|else|try|finally|global|nonlocal|await)\b)[A-Za-z_][\w.]*\s*(#.*)?$', '^\s*\[[^\]]*\]\s*(#.*)?$']
scope: hunk
check_kind: mechanical
severity_default: major
---

# A Python statement never consists of a bare comparison, name, attribute, subscript, arithmetic expression or collection literal whose value is discarded

## Thesis
A Python statement that consists only of a comparison, a name, an attribute, a subscript, an arithmetic expression or a collection literal, such as `x == 1`, `self.flush` or `[1, 2, 3]` on its own line, is corrected into the assignment, call or assertion it was meant to be, or removed.

## Rationale
Python admits any expression as a statement: an expression statement evaluates the expression; its uses are computing and writing a value, mostly interactively, and calling a procedure, and other uses are allowed. A comparison typed in place of an assignment, such as `self.retries == 0` meant as a reset, or an attribute written where its call was meant, therefore runs and has no effect on the program, so the intended reset or call does not happen. Such a statement can be caused by mistyping, a copy-and-paste error or a refactoring that left it behind; where it is not an error, it is redundant.

## Example
```python
bad:  def reset(self):
          self.retries == 0
          self.flush
good: def reset(self):
          self.retries = 0
          self.flush()
```

## Limits
A call, which commonly runs for its side effect, and the pass and Ellipsis placeholders, which are meant to have no effect and may mark a missing implementation, are outside the rule. An expression needed to trigger a side effect, such as an attribute access inside a block that expects it to raise, is a deliberate use; assigned to an anonymous variable, as `_ = obj.attribute`, it shows that the value is ignored on purpose. An operator expression on a type that redefines the operator with a side effect, such as a pipeline built with `|` and `>>`, has an effect and is outside the rule. The last top-level expression of a notebook cell, whose repr the notebook prints as the cell's output, is outside the rule. A string literal standing alone is outside the rule, because the positions on it differ: one reports a string used as a statement as having no effect, the other leaves it unreported by default because some projects use string literals as comments.

## Validator
In each added line, find a statement that consists of an expression alone: a bare comparison, a bare dotted name, a subscript, an arithmetic expression, or a list, tuple, set or dict display. Open the hunk around it and confirm that the expression is not a call, an await, a yield, a string literal or Ellipsis, that the line is not the last top-level expression of a notebook cell, and that the operator is not one the project's types redefine with a side effect. Read the surrounding statements to name what was meant: an assignment for a comparison, a call for an attribute, an assert for an invariant check. Validator question: **Does the hunk add a statement that is only a comparison, name, attribute, subscript, arithmetic expression or collection literal, whose value nothing uses?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-144`, severity major, `file`, `symbol`, `code` = the statement quoted verbatim from the diff, `fix` = the statement it was meant to be, such as `self.retries = 0`, `self.flush()` or `assert x == 1`, or its removal, `rationale` = the kind of expression, the fact that its value is discarded, and the effect the line appears meant to have).

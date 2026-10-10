---
title: A declared local variable is used, and one that is never read is removed rather than kept or silenced with a blank assignment, an underscore name or a suppression
rule_id: CODE-25
domain: code
step: [implement, refactor]
applies_to: [universal]
triggers: ['(^\s*(let\s+)?_\s*=\s*[A-Za-z_][\w.]*\s*;?\s*$|\b(let|const|var)\s+(mut\s+)?_[a-z]\w*\s*(:[^=]+)?=|^\s+_[a-z]\w*\s*=[^=]|\b(unused|ignored)[A-Z_]\w*\s*(:[^=]+)?=[^=])', '(pylint:\s*disable=[\w, -]*\b(unused-variable|W0612)\b|@SuppressWarnings\([^)]*[\x22'']unused|#!?\[(allow|expect)\([^)]*\bunused(_variables)?\b|eslint-disable\S*\s[^*]*\bno-unused-vars\b|noqa:[\w, ]*\bF841\b)']
scope: file
check_kind: mechanical
severity_default: minor
---

# A declared local variable is used, and one that is never read is removed rather than kept or silenced with a blank assignment, an underscore name or a suppression

## Thesis
Every local variable declared in a routine body has its value read: in an expression, a call argument, a return, or an assignment to another variable. A local that is only declared, only assigned to, only updated from its own value, or only assigned to the blank identifier is never read. A never-read local is removed, its binding dropped and any side effect of its initializer, such as a call that changes state, kept, or it is used where its value was meant to go, rather than kept with its compiler or linter warning silenced by an assignment to the blank identifier, a name prefixed with an underscore, "unused" or "ignored", or a suppression comment or attribute.

## Rationale
A variable that is initialized but never read is at least a wasted computation and perhaps a sign of a larger bug: a variable declared for a calculation and then forgotten may leave the program not working as expected. Such a variable is most likely an error left by an incomplete refactoring; it takes up space in the code and can confuse readers, and a reader who takes it for a mistake may try to fix the code and potentially introduce a new bug. One language makes declaring a local without using it a compile error, and compilers and linters of other languages report it. The blank assignment is the workaround for code under active development: assigning the unused variable to the blank identifier silences the error, blank assignments identify code as a work in progress, and what they silence should eventually be used or removed. An underscore prefix silences the same warning, which may signal a mistake or unfinished code, and a suppression annotation is the escape for a false positive; each silences the report and leaves the variable as unused as before. Once the variable is confirmed not to belong to an unfinished implementation, the fix is to remove it.

## Example
```typescript
bad:  const _started = Date.now();
      // eslint-disable-next-line @typescript-eslint/no-unused-vars
      const count = items.length;
      return sum(items);
good: return sum(items);
```

## Limits
A slot that a multiple assignment, a destructuring, a pattern match, a loop header or a resource statement requires takes the blank identifier, an underscore name or the unnamed pattern when its value is not needed; that marks the value as unused without creating a dummy variable, and the rule accepts it. A binding that exists so that the value it holds lives to the end of the scope, such as a lock guard or a resource torn down when the scope ends, works through its lifetime, and the rule accepts it; where a discard into the blank pattern drops the value at once, an underscore-prefixed name is the documented form that keeps it to the end of the scope. A blank discard of a value a call returns names no variable and is outside the rule. Checkers differ on a standalone local whose name marks it as unused: several exempt by default a name prefixed with an underscore, "unused" or "ignored" as intentionally unread, while another reports it unless an ignore pattern is configured; a project context that adopts the exemption for standalone locals rejects the finding for a marked local, and an unmarked never-read local is still flagged. Routine parameters, fields, imports and unused routines and types are outside the rule, which covers variables declared in a routine body.

A local named as unused that receives the result of a call whose dropped result a must-use check reports, made only so that the call fails fast on a bad argument, such as an early check that a format string is valid, is the documented form of a deliberate discard and is outside the rule.

## Validator
Grep the added lines for an assignment of a bare variable to the blank identifier, a declaration or assignment of a name prefixed with an underscore, "unused" or "ignored", and a comment or attribute that suppresses the unused-variable check; note as well every other local declared on the added lines of that hunk. Open the file, find the enclosing routine, and search it for a read of each such variable's value: in an expression, a call argument, a return, or an assignment to another variable. An assignment to the variable, an update of it from its own value and an assignment of it to the blank identifier are not reads. Skip a slot that a multiple assignment, a destructuring, a pattern match, a loop header or a resource statement requires; a binding held to the end of its scope so that a lock or resource it owns is released then; a blank discard of a call's returned value; when the project context adopts an exemption for marked names, a local whose name marks it as unused; and a local named as unused that holds the result of a must-use call made only to fail fast on a bad argument. Validator question: **Does an added line declare a local variable whose value is never read in its routine, or silence the warning about such a variable with a blank assignment, a name marked as unused or a suppression, outside a required pattern slot and a binding held for its release at the end of the scope?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: CODE-25`, severity minor, `file`, `symbol`, `code` = the declaration of the never-read variable and any line that silences its warning, quoted verbatim from the diff, `fix` = the routine with the variable's binding and its silencing removed and any side effect of its initializer, such as a call that changes state, kept, or with the variable read where its value was meant to go, in the file's language, `rationale` = which variable is never read, what its initializer computes for nothing, and any read it appears to have been meant for).

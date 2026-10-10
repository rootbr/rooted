---
title: A local variable is declared close to its first use, not at the start of its block ahead of code that does not use it, and is initialized in its declaration or immediately after it
rule_id: CODE-21
domain: code
step: [implement, refactor]
applies_to: [universal]
triggers: ['^\s*(final\s+)?((int|long|short|byte|char|float|double|boolean|String|[A-Z][\w.]*(<[^;=]*>)?)(\[\])*|var|let)\s+[A-Za-z_$][\w$]*\s*;\s*$', '^\s*var\s+[A-Za-z_]\w*(\s*,\s*[A-Za-z_]\w*)*\s+[\w.*\[\]]+\s*$', '^\s*let\s+(mut\s+)?[A-Za-z_]\w*\s*(:\s*[^=;]+)?;\s*$', '^\s*(?:(?:let|var|const|final|auto)\s+)?(?:mut\s+)?(?:[\w<>\[\]]+\s+)?[A-Za-z_]\w*(?:\s+[\w.*\[\]]+)?\s*(?::\s*[^=]+)?(?::=|=)\s*(null|nil|undefined|0|false|[\x22\x27]{2})\s*;?\s*$', '^\s*let\s+(mut\s+)?[A-Za-z_]\w*\s*(:\s*[^=;]+)?=\s*None\s*;\s*$']
scope: hunk
check_kind: semantic
severity_default: minor
---

# A local variable is declared close to its first use, not at the start of its block ahead of code that does not use it, and is initialized in its declaration or immediately after it

## Thesis
Each local variable is declared close to the point where it is first used, within reason, rather than habitually at the start of its block, to minimize its scope. It is initialized as soon as possible, typically by an initializer in its declaration or by an assignment immediately after the declaration. A declaration is premature when a statement that may return or throw, and that refers to no variable the declaration binds, lies between it and the variable's first use, the first statement that reads or assigns it, and no statement before that exit may change a variable, a field or other state that the declaration's initializer reads.

## Rationale
A block-scoped local belongs to its block and is not used before its declaration, so where the declaration stands sets how much of the block the variable spans, and declaring it close to its first use minimizes its scope. The gain is in readability, not in speed: an optimizing runtime can reorder code and does not care whether a declaration is premature. Close means within reason, not a measured distance; a distance check run with its defaults flags a declaration not marked final when the statement of its own block that holds the first use comes more than three statements after it, counting that statement and leaving out other variables declared or initialized in between, and that tool default, with those two conditions, serves as the bound where the project states none. Assigning the first value in the declaration is less repetitive than declaring the variable and assigning it later, and a value chosen by a branch still fits there as a conditional or match expression used as the initializer; a conditional that assigns the variable on every reachable path, written as the statement after the declaration, also initializes it. What an early declaration without an initializer costs depends on the language: where a declaration with no explicit initialization gives the variable its type's zero value (false, 0, the empty string, nil), a read placed before the intended assignment sees that zero value, while where a local can be used only after it has been initialized through all reachable control-flow paths, the same read is an error.

## Example
```go
bad:  var name string
      if id == "" {
          return errMissingID
      }
      name = lookup(id)
good: if id == "" {
          return errMissingID
      }
      name := lookup(id)
      ...
```

## Limits
A distance the project context states governs the finding; under the default bound of three, as under the distance check's defaults, a declaration that cannot be reassigned, such as one marked final, is not measured, and neither is a first use inside a bare nested block. A declaration whose initializer has side effects that must happen before the statements that follow, such as reading a clock to time them, stays where it is, and so does a declaration whose initializer reads a variable, a field or other state that a statement before the variable's first use may change, such as a snapshot taken before an update, since moving it changes the value it holds. A declaration that binds several variables at once stays where it is when the statement after it refers to one of them, as when a call's value and its error are declared together and the error is checked, and returned on, before the value is used. A variable whose value is needed outside the conditional that produces it is not narrowed into that conditional, and a scope is not narrowed where narrowing it would add nesting. Where a declaration without an initializer gives the variable its type's zero value, a declaration whose zero value is the intended empty value, ready for later use, such as a counter starting at zero or an output argument the next call fills, counts as initialized; it still stands close to its first use. Where any binding of a name anywhere in a function body makes the name local to the whole body, as in a language without declarations, or where a function-scoped declaration is hoisted to the top of its routine, moving the binding does not change its scope, and the rule does not reach the binding's position. There a block-scoped declaration form, where the language has one, replaces the hoisted form, and a lint convention that writes hoisted declarations at the top of the routine to show their real scope is a documented project tolerance. Fields, module-level variables, parameters, shadowing and the reuse of one variable for two purposes are outside this rule.

## Validator
Grep the added lines for a local declaration without an initializer, a declaration initialized with a null-like or zero-like placeholder, and a block-scoped declaration written at the start of a block. For each, read the hunk from the declaration down to the variable's first use, and decide only on what the hunk shows. Skip a field, a module-level variable, a parameter, a binding in a language without declarations, a hoisted function-scoped declaration, a declaration whose initializer has side effects that must run before the statements that follow, a declaration whose initializer reads a variable, a field or other state that a statement before the first use may change, a declaration one of whose variables the statement after it refers to, such as a value declared together with the error that statement checks, and a variable whose value is needed outside the conditional that produces it. Treat a declaration whose zero value is the intended starting value as initialized: the last part of the question does not reach it, and the first two parts still do. Count the statements of the declaring block after the declaration up to and including the one that holds the first use, leaving out other variables declared or initialized in between, and take as the bound the distance the project context states, or three when it states none; under the bound of three, measure no declaration that cannot be reassigned and no first use inside a bare nested block. Validator question: **Does a statement that may return or throw, and that refers to no variable the declaration binds, stand between an added local declaration and the variable's first use, does the count to its first use exceed the bound, or is the variable declared without an initializer and first assigned only after other statements?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: CODE-21`, severity minor, `file`, `symbol`, `code` = the added declaration quoted verbatim from the diff, `fix` = the declaration moved to the variable's first use and given its first value there as an initializer, in the file's language, `rationale` = the statement that may return or throw, or the statements that do not use the variable, standing between the declaration and its first use, or the later assignment that belongs in the declaration).

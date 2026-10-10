---
title: A variable or constant is declared in the narrowest scope that holds all its uses, unless narrowing it would deepen nesting or its value is needed after that scope
rule_id: CODE-22
domain: code
step: [design, implement, refactor]
applies_to: [universal]
triggers: ['\b(const|static|final|readonly)\s+(mut\s+)?([\w<>\[\]?.]+(,\s*[\w<>\[\]?.]+)*\s+)?[A-Z][A-Z0-9_]*\s*[:=]', '^((const|let|static)\s+(mut\s+)?)?[A-Za-z_$][\w$]*\s*(:\s*[^=\n]+)?=(?!=)', '\b(const|let|var)\s+(mut\s+)?[A-Za-z_$({\[]|\b[A-Za-z_]\w*(\s*,\s*[A-Za-z_]\w*)*\s*:=|^\s*(private|protected)\s+(static\s+)?(?!final\b|readonly\b)[\w<>\[\],.?: ]*\b[a-z]\w*\s*;']
scope: file
check_kind: semantic
severity_default: minor
---

# A variable or constant is declared in the narrowest scope that holds all its uses, unless narrowing it would deepen nesting or its value is needed after that scope

## Thesis
Each variable and each constant is declared in the smallest scope that contains all its uses. A variable that only one block, loop or conditional uses is declared inside it, in that statement's own initializer where the language offers one. A variable whose value one loop iteration or one call of its routine leaves for the next stays declared outside that loop body or routine. A private field that every routine using it assigns before it first reads it becomes a local variable of those routines. In a language with a constant declaration usable inside a routine, a constant whose value is a literal, or an expression over literals and other constants, is declared inside the routine that uses it unless several routines or files use it or it is part of the module's external contract. Where the language offers both a block-scoped and a function-scoped declaration form, the block-scoped form is used. The declaration stays in the wider scope when narrowing it would conflict with reducing nesting, or when its value is needed outside the narrower scope.

## Rationale
A name declared in a larger scope than its uses stays accessible after its last intended use: a loop variable declared before its loop is still visible after it, and a value bound at the top of a long routine can be used anywhere below. The costs are readability, resources the name holds retained for much longer than needed where leaving a scope releases them, and accidental misuse of the value, such as using a loop variable for another purpose after the loop or an unanticipated later use of an open handle. A function-scoped declaration form makes a variable visible throughout its function rather than its block, which can cause difficult-to-understand bugs. A private field that every routine using it assigns before it first reads it never lets a call observe the value it had before that call, so it might as well not be stored in the enclosing object. The property restored is that no name is declared in an unnecessarily large scope.

## Example
```rust
bad:  const RETRY_LIMIT: u32 = 3;
      fn send(msg: &Msg) -> bool {
          (0..RETRY_LIMIT).any(|_| try_send(msg))
      }
good: fn send(msg: &Msg) -> bool {
          const RETRY_LIMIT: u32 = 3;
          (0..RETRY_LIMIT).any(|_| try_send(msg))
      }
```

## Limits
Narrowing yields to reducing nesting: when moving a declaration into a conditional's initializer would push the rest of the routine into that conditional's branches, rather than handling the error case or special condition first and returning early, the declaration stays in the enclosing scope. A value needed outside the conditional or block, such as a call's result that the following code uses, stays declared outside it. In a language whose only blocks are modules, function bodies and class definitions, a name bound inside a conditional or a loop is a local variable of the whole enclosing function body, so the function body is the narrowest scope available to it. A value built at run time, such as a compiled regular expression or a constructed collection or formatter, stays at class or module level even when one routine uses it, because a routine-local declaration can rebuild it on every call and compiling a pattern has a significant performance cost. A private field that every routine assigns before reading may still be correct in concurrent code, which the single-use-field condition does not account for; a suppression the project documents for such a field rejects the finding. Where a declaration sits within its scope relative to its first use, whether module-level state may be mutable, and how the variable is named are outside this rule. A variable, field or module-level variable that carries a value from one loop iteration or routine call to the next, such as the previous element, a running state or a cache, stays declared outside that loop body or routine, because declaring it inside would reset it on every iteration or call. In a language without a constant declaration usable inside a routine, whose constants are module-level or class-level names written in capitals by convention, a constant stays at module or class level even when one routine uses it.

A private field that generated or built-in equality, hashing, formatting or serialization reads, that a closure or nested type captures, or that another method, a callback or concurrently running code may assign between a routine's assignment and its read carries a value beyond one call and stays a field.

## Validator
Grep the hunk for added declarations: a function-scoped declaration form where the language also has a block-scoped one, a module-level variable, a module- or class-level constant whose value is a literal or an expression over literals and other constants, a private field declared without an initializer, and a variable declared on its own line just before the conditional or loop that uses it. Open the file and find every use of each candidate: for a local, the blocks that read or write it, whether any use follows the conditional or block, and whether a read in a loop body can see a value written in an earlier iteration; for a module-level variable, the routines that use it and whether a call reads a value set before that call; for a module-level or class-level constant, the routines and files that use it and whether it is exported or documented as part of the module's contract; for a private field, whether every routine that uses it assigns it before its first read. Drop a candidate whose value is used outside the narrower scope, a variable or field whose value one loop iteration or routine call leaves for the next, a field that some routine reads before assigning it, a constant exported or documented as part of the module's contract, a module-level or class-level constant in a language without a constant declaration usable inside a routine, a value built at run time, such as a compiled regular expression or a constructed collection, held at class or module level, one whose narrowing would push the routine's remaining code into a nested branch in place of an early return, a local already at function-body level in a language whose only blocks are modules, function bodies and class definitions, and a field the project documents as kept for concurrent access. Validator question: **Is an added variable, field or constant declared with a function-scoped form where a block-scoped form exists, in a larger scope than the smallest block, routine or module scope that holds all its uses, or as a private field that every routine using it assigns before its first read, where narrowing it would neither deepen nesting, nor cut off a use outside the narrower scope, nor reset a value that one loop iteration or routine call leaves for the next?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: CODE-22`, severity minor, `file`, `symbol`, `code` = the added declaration, verbatim from the diff, `fix` = the declaration moved into the smallest block, statement initializer or routine that holds all its uses, or, for a private field that every routine using it assigns before its first read, a local variable in each of those routines, or rewritten with the block-scoped declaration form, in the file's language, `rationale` = the scope the name is declared in, the smaller scope that holds all its uses, and the code outside that smaller scope that can still reach the name).

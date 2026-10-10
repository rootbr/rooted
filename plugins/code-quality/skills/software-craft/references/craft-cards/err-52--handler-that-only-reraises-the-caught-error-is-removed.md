---
title: A handler whose only statement re-raises the caught error unchanged is removed so the error propagates on its own, unless it keeps that error away from a later handler of the same try
rule_id: ERR-52
domain: errors
step: [implement, handle-errors, refactor]
applies_to: [exceptions]
triggers: ['^\s*raise(\s+\w+)?\s*$', '^\s*throw(\s+\w+)?\s*;?\s*\}?\s*$', '\bcatch\s*(\([^)]*\))?\s*\{\s*throw(\s+\w+)?\s*;?\s*\}', '^\s*except\b[^:]*:\s*raise(\s+\w+)?\s*$', '\bresume_unwind\s*\(']
scope: hunk
check_kind: mechanical
severity_default: minor
---

# A handler whose only statement re-raises the caught error unchanged is removed so the error propagates on its own, unless it keeps that error away from a later handler of the same try

## Thesis
A handler of a raised error is removed when its body only re-raises the error it caught, unchanged: a bare re-raise, or a re-raise of its own bound variable, with no cause attached, no wrapping and no statement before it. The enclosing try goes with it unless something else still needs the try: another handler that stays, a cleanup block, or a resource the try manages. The handler is kept when a later handler of the same try would also catch an error it catches, as a handler of a supertype, of the same type, of a subtype or of a type an error can share with it does, because the immediate re-raise then keeps that error away from the later handler.

## Rationale
Unless a later handler of the same try would also catch the error, or no handler above would catch it and the runtime need not then unwind the stack, a handler that only re-raises the error it caught has at best the same effect as omitting it and letting the error bubble up, and it adds code size, runtime complexity and a source of confusion. Catching an error in a function that cannot take a meaningful recovery action leads to complexity and waste; the error is left to propagate until it reaches a function that can handle it. The re-raise that names the caught variable can do worse and lose information. Where the runtime restarts the stack trace at such a re-raise, the list of calls between the function that raised the error and the handler is lost, and where it throws a copy of the error as the handler's declared type, the copy is sliced to that static type; the bare re-raise keeps the original error and its trace.

## Example
```rust
bad:  let total = match catch_unwind(|| sum(&rows)) {
          Ok(total) => total,
          Err(payload) => resume_unwind(payload),
      };
good: let total = sum(&rows);
```

## Limits
An immediate re-raise is correct when a later handler of the same try catches a supertype of the type it names: removing it would hand that subtype to the broader handler. A later handler of the same type, of a subtype or of a type an error can share with it would likewise receive the errors the re-raise lets pass, so removal changes behaviour there as well, and the handler is kept. A handler that does work before re-raising, re-raises only after testing a condition, wraps the error, or raises a new error with the caught one as its cause does something, and is outside the rule. Where the function can act on the error, the alternative to removal is a handler populated with that logic; which logic is appropriate, including whether a log call before the re-raise is enough, is a question the rule leaves open. An error returned as a value and passed on by an explicit return or a propagation operator goes through no handler and is outside the rule. A panic that reaches the function as a value from outside it, such as the result of joining a thread, was caught by no handler of the function: resuming it is how that panic propagates, and the rule does not apply. A handler in the entry function of a program or a thread, which nothing above can catch past, is kept where the runtime need not unwind the stack when no handler matches: there it is what makes the cleanup between the raise and it run. Outside such an entry function the handler is flagged although the function cannot see whether a handler above it catches the error; where none does and the runtime need not unwind the stack, removing the handler also skips that cleanup.

## Validator
Grep the hunk for a re-raise that stands alone in a handler body: a bare re-raise, a re-raise of the handler's bound variable, or a call that resumes, with its payload, a panic that a catching call in the same function caught. Open the enclosing try and read the whole handler body: confirm the re-raise is its only statement and carries no cause and no wrapping. List the later handlers of the same try and check whether any would also catch an error this handler catches: a handler of a supertype, of the same type, of a subtype or of a type an error can share with it. Note whether the try also has another handler that stays, a cleanup block or a managed resource, so the fix keeps the try. Note whether the try sits in the entry function of a program or a thread whose runtime need not unwind the stack when no handler matches; the handler is kept there. Validator question: **Does a handler's body consist only of re-raising the error it caught, unchanged, with no later handler of the same try that would also catch an error it catches, and outside the entry function of a program or a thread whose runtime need not unwind the stack when no handler matches?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: ERR-52`, severity minor, `file`, `symbol`, `code` = the handler verbatim from the diff, from its catch line through the re-raise, `fix` = the same code with the handler removed, and the try with it when nothing else needs it, in the file's language, `rationale` = names that the handler has at best the same effect as no handler wherever a handler above catches the error and, for a re-raise of the bound variable, the trace or type it can lose).

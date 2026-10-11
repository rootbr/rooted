---
title: A change merges no placeholder that halts at run time because the functionality is not yet written, such as todo!() or a raised not-implemented error, on a path production code reaches
rule_id: CHG-37
domain: change
step: [implement]
applies_to: [universal]
triggers: ['(?i)\b(todo|unimplemented)!\s*\(|\braise\s+NotImplementedError\b|\b(throw|raise|panic)\b.*\bnot\s+(yet\s+)?implemented\b|\bpanic\s*\(\s*"(todo|unimplemented)']
scope: callers
check_kind: semantic
severity_default: major
---

# A change merges no placeholder that halts at run time because the functionality is not yet written, such as todo!() or a raised not-implemented error, on a path production code reaches

## Thesis
Each routine that production code reaches is finished when the change merges: it holds no placeholder that fails at run time whenever it is reached and marks functionality still to be written, such as a call or a raised error whose message says the code is not yet implemented.

## Rationale
Such a placeholder lets unfinished code pass type analysis while it is prototyped, and it fails every time it is reached, so the gap surfaces as a failure when a run takes that path. A to-do placeholder's message states the intent to implement the functionality later; the code is unfinished, and unfinished code should not be present in production code. The not-implemented error carries the same in-development use: it is raised while a class is being developed to indicate that the real implementation still needs to be added. One documented use of the linter check for this placeholder is an added restriction in continuous integration.

## Example
```typescript
bad:  export function sumAll(values: number[]): number {
        throw new Error("not yet implemented");
      }
good: export function sumAll(values: number[]): number {
        return values.reduce((total, value) => total + value, 0);
      }
```

## Limits
Test code is outside the rule, which concerns production code. An abstract member of a base class that raises the not-implemented error so that derived classes override it follows a documented convention and is outside the rule. A member deliberately left without implementation, such as one of several interface members the program does not plan to use, is outside the rule when a comment beside its placeholder or the placeholder's message states why it is deliberately left out, or when it is left undefined where the language documents that form for a member not meant to be supported; the rule reaches only a placeholder for work still to come. The linter check for the placeholder is allowed by default, in a category whose checks may flag perfectly reasonable code and are to be considered case by case before enabling; the finder judges each hit by its message, the comment beside it and whether production code reaches it.

## Validator
Grep the hunk for the triggers. For each hit, open the enclosing routine in the hunk and read the placeholder's message and any adjacent comment: count the placeholder as marking functionality still to be written when its message or comment says not yet implemented, to do or later, or says only not implemented and gives no reason, unless the member is abstract and required to be overridden by derived classes, or a comment beside it or its message states why the member is deliberately left out. Skip a test file and test-only code. Trace from the hunk whether production code reaches the routine: a call site outside tests, a public or exported entry point, a registration as a handler, or an implementation of an interface member that production code invokes. Validator question: **Does the hunk add a placeholder that fails when reached and marks functionality still to be written, in a routine that production code reaches?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: CHG-37`, severity major, `file`, `symbol`, `code` = the placeholder line verbatim from the diff, `fix` = the routine with the functionality implemented or, where the member is deliberately not supported, the placeholder with a comment or message stating why, in the file's language, `rationale` = names the functionality the placeholder leaves unwritten and the production path that reaches it).

## Source
- rust-lang/rust `library/core/src/macros/mod.rs`, doc comment of `todo!` — "Indicates unfinished code. This can be useful if you are prototyping and just want a placeholder to let your code pass type analysis."; "This will always [`panic!`]"; "while `todo!` conveys an intent of implementing the functionality later and the message is "not yet implemented", `unimplemented!` makes no such claims" (fetched)
- same file, doc comment of `unimplemented!` — "useful if you are prototyping or implementing a trait that requires multiple methods which you don't plan to use all of"; "We still want to have our program stop running if the unimplemented methods are reached."; its example states each omission: "It makes no sense to `baz` a `MyStruct`, so we have no logic here"; "We can add a message to unimplemented! to display our omission."; `unimplemented!("MyStruct isn't quxable");` (fetched)
- rust-clippy lint `todo` (restriction), `clippy_lints/src/panic_unimplemented.rs` — "The `todo!` macro indicates the presence of unfinished code, so it should not be present in production code."; "Finish the implementation, or consider marking it as explicitly unimplemented."; lint `unimplemented` (restriction), same file — "`unimplemented!` should not be present in production code" (fetched)
- rust-clippy `README.md`, lint categories — `clippy::restriction` default level "allow"; "The contained lints may lint against perfectly reasonable code"; "Lints should be considered on a case-by-case basis before enabling."; "Additional restrictions on CI (e.g. [`clippy::todo`])." (fetched)
- python/cpython `Doc/library/exceptions.rst` (3.12), `NotImplementedError` — "abstract methods should raise this exception when they require derived classes to override the method, or while the class is being developed to indicate that the real implementation still needs to be added."; "It should not be used to indicate that an operator or method is not meant to be supported at all -- in that case either leave the operator / method undefined" (fetched)
- microsoft/TypeScript `src/services/codefixes/helpers.ts` (v5.9.3), `createStubbedMethodBody` — returns `createStubbedBody(Diagnostics.Method_not_implemented.message, quotePreference)`, a block holding `factory.createThrowStatement(...)`; `src/compiler/diagnosticMessages.json` — "Method not implemented.", "Function not implemented." (fetched)
- Caveat: the rule rests on two languages' documentation and one linter; it carries their statement to an equivalent throw or panic whose message says the code is not yet implemented.

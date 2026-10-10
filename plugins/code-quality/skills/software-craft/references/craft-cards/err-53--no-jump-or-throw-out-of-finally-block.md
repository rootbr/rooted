---
title: A finally or other cleanup block does not leave itself through a return, break or continue written in it, nor through an explicit throw where the language then discards the pending error, so the try block's error or result stands
rule_id: ERR-53
domain: errors
step: [implement, handle-errors]
applies_to: [exceptions]
triggers: ['\bfinally\b', '\bfinally\s*(\{|:).*\b(return|break|continue|throw|raise)\b']
scope: hunk
check_kind: mechanical
severity_default: major
---

# A finally or other cleanup block does not leave itself through a return, break or continue written in it, nor through an explicit throw where the language then discards the pending error, so the try block's error or result stands

## Thesis
A finally or other cleanup block completes normally: each return, break or continue written in it targets a point inside the block, and where a throw from the block makes the language discard the error already propagating, the block holds no explicit throw that leaves it, so the error or return value of the try and catch blocks reaches the caller.

## Rationale
While the cleanup block runs, the outcome of the try and catch blocks is held back: an error in flight or a value about to be returned. When the block completes normally, that outcome stands; when it completes abruptly, through a jump to a target outside it or through a throw in a language that does not keep the held error as the new error's context, the statement completes with the block's outcome and the held one is discarded, so an error vanishes or a return value is overridden. The vanished error is the more dangerous half, because a swallowed exception is more likely to slip through testing than an incorrect return value. An analysis of the 8,000 most popular packages of a public package index found 203 such jumps in over 120 million lines; 149 of them (73%) were clearly incorrect and can lead to unintended swallowing of exceptions, and 46 more sat in tests that target the pattern as a feature. An explicit throw from the block hides the active error and makes the original hard to detect and debug, unless the language sets the saved error as the context of the new one; an empirical taxonomy of exception-handling faults in open-source projects names this fault the suppressed exception: the original exception hidden by another exception raised in the same context.

## Example
```java
bad:  int next(Resource resource) {
        try { return resource.read(); }
        finally { resource.release(); return -1; }
      }
good: int next(Resource resource) {
        try { return resource.read(); }
        finally { resource.release(); }
      }
```

## Limits
A jump whose target lies within the block is outside the rule: a break or continue of a loop or switch inside the block, and a return, break or continue inside a function, lambda or class defined in the block. An error thrown implicitly by a method the block calls is outside the rule, which reads only the statements written in the block, though such an error can discard the pending one as well. Where the language sets the saved error as the context of an error raised in the block, the throw form is outside the rule and only return, break and continue count. Where the compiler already rejects a form in the cleanup block, that form cannot occur and only the remaining forms are checked. A generator that uses a return in the cleanup block to override its returned value on purpose carries a suppression comment. The few uses that seem to work as intended, 8 of 203 in the analysis above, either swallow errors on purpose or appear where an active error cannot occur; they are not hard to rewrite: the deliberate swallow as an explicit catch-all handler, the return moved after the cleanup block.

## Validator
Grep the hunk for `finally` and for other cleanup blocks. Open each such block and list every return, break, continue and explicit throw or raise written in it. For each jump, trace its target: skip it when the target is a loop or switch inside the block, or when the statement sits in a function, lambda or class defined in the block. For each explicit throw, check whether the file's language sets the pending error as the context of the new one, and skip it if so. Skip an error that only a called method throws, and a return carrying a suppression comment in a generator that overrides its returned value on purpose. Validator question: **Does a return, break or continue in the cleanup block reach a target outside it, or does an explicit throw in it leave the block in a language that does not keep the pending error as the new error's context?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: ERR-53`, severity major, `file`, `symbol`, `code` = the cleanup-block header and the jump or throw statement quoted verbatim from the diff, `fix` = the cleanup block completing normally, with the return moved after the block or a deliberate swallow written as an explicit catch-all handler, in the file's language, `rationale` = the error or return value of the try or catch block that the statement discards).

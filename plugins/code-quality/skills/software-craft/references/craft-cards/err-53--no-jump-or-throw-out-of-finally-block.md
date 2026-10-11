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

## Source
- SEI CERT Oracle Coding Standard for Java, ERR04-J "Do not complete abruptly from a finally block", rule statement, JLS §14.20.2 quotation, ERR04-J-EX0: "Never use `return` , `break` , `continue` , or `throw` statements within a `finally` block."; "If the `finally` block completes normally, then the `try` statement completes abruptly for reason `R`."; "If the `finally` block completes abruptly for reason `S`, then the `try` statement completes abruptly for reason `S` (and reason `R` is discarded)."; "Control flow statements whose destination is within the `finally` block are perfectly acceptable." (fetched)
- ESLint rule no-unsafe-finally, rule introduction, second example, Rule Details, When Not To Use It: "JavaScript suspends the control flow statements of `try` and `catch` blocks until the execution of `finally` block finishes."; "return 3; // 3 is returned before the error is thrown, which we did not expect"; "It allows indirect usages, such as in `function` or `class` definitions."; "using `return` with `try`/`finally` in generator functions can be used to override the value returned. If you want to use this feature of generator functions, you can disable this rule using an `eslint-disable` comment." (fetched)
- ECMA-262, The try Statement, Runtime Semantics: Evaluation, TryStatement : try Block Catch Finally: "Let _finallyResult_ be Completion(Evaluation of |Finally|). If _finallyResult_ is a normal completion, set _finallyResult_ to _catchResult_." (fetched)
- ECMA-334 C# draft v8, §13.11 The try statement: "It is a compile-time error for a `break`, `continue`, or `goto` statement to transfer control out of a `finally` block."; "It is a compile-time error for a `return` statement to occur in a `finally` block."; "If an exception is thrown during execution of a `finally` block, and is not caught within the same `finally` block, the exception is propagated to the next enclosing `try` statement. If another exception was in the process of being propagated, that exception is lost." (fetched)
- Python Language Reference §8.4, finally clause: "If the finally clause raises another exception, the saved exception is set as the context of the new exception. If the finally clause executes a return, break or continue statement, the saved exception is discarded." (fetched)
- PEP 8, Programming Recommendations: "where the flow control statement would jump outside the finally suite, is discouraged. This is because such statements will implicitly cancel any active exception that is propagating through the finally suite" (fetched)
- PEP 765 (Final, Python 3.14), Motivation and Appendix: "a swallowed exception is more likely to slip through testing, than an incorrect return value"; "The analysis is based on the 8,000 most popular PyPI packages"; "203 instance in over 120 million lines of code"; "73% in our sample (149 of 203)"; "149 were clearly incorrect, and can lead to unintended swallowing of exceptions."; "46 are correct, and appear in tests that target this pattern as a feature"; "8 seem like they could be correct - either intentionally swallowing exceptions or appearing where an active exception cannot occur. Despite being correct, it is not hard to rewrite them"; "deliberately swallowing exceptions can be more explicitly done with `except BaseException:`, and `return` which doesn't swallow exceptions can be moved after the `finally` block" (fetched)
- Error Prone bug pattern Finally, first and second paragraphs: "Terminating a finally block abruptly preempts the outcome of the try and catch blocks, and will cause the result of any previously executed return or throw statements to be ignored. Finally blocks should be written so they always complete normally."; "If closing the input stream *also* fails, then the exception that was thrown in the catch block will be preempted by the exception thrown by `close()`, and the first exception will be lost." (fetched)
- .NET code analysis rule CA2219: "When an exception is raised in a `finally` or fault clause, the new exception hides the active exception, if present. This makes the original error hard to detect and debug." (fetched)
- .NET Framework Design Guidelines, Exception Throwing: "AVOID explicitly throwing exceptions from finally blocks. Implicitly thrown exceptions resulting from calling methods that throw are acceptable." (fetched)
- The Swift Programming Language, Error Handling, Specifying Cleanup Actions: "The deferred statements may not contain any code that would transfer control out of the statements, such as a `break` or a `return` statement, or by throwing an error." (fetched)
- DOI 10.1109/SBES.2014.19, "Categorizing Faults in Exception Handling: A Study of Open Source Projects", as reviewed on neverworkintheory.org ("presents an empirical taxonomy of the ways exceptions are mis-handled"): "Suppressed exception: the original exception is hidden by another exception raised in the same context" (fetched)
- Caveat: the 203-use analysis covers one language whose raise in a finally clause keeps the saved exception as context, so its numbers measure the return, break and continue forms only.

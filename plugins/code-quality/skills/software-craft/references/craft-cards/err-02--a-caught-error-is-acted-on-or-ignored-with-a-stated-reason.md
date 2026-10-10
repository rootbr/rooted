---
title: A caught exception or received error is acted on, or ignored only with a comment stating why that is safe, and an empty handler, a bare pass, a TODO or a printed stack trace does not count as acting
rule_id: ERR-02
domain: errors
step: [implement, handle-errors]
applies_to: [universal]
triggers: ['signal:empty_handler', '\bcatch\s*(\([^)]*\))?\s*\{\s*\}', '[.]catch\(\s*(\([^)]*\)|\w+)\s*=>\s*(\{\s*\}|undefined|null)\s*\)', '\b(catch|except|rescue)\b|\bErr\(\s*_?\w*\s*\)\s*=']
scope: hunk
check_kind: mechanical
severity_default: major
---

# A caught exception or received error is acted on, or ignored only with a comment stating why that is safe, and an empty handler, a bare pass, a TODO or a printed stack trace does not count as acting

## Thesis
Every handler that receives an error — a `catch`, `except` or `rescue` clause, a rejection callback, a branch or match arm taken on a returned error value — acts on it: it recovers so that execution continues in a valid state, returns or rethrows the error, raises an error suited to its own level, or records the error through the program's logging or error-reporting channel. Doing nothing is very rarely correct; where it is, the handler carries a comment stating why dropping the error is safe. An empty body, a lone `pass` or other no-op, a body holding only a TODO or FIXME, a bare return that hands the caller neither the error nor a result that shows the failure, and a stack trace printed before execution carries on are dropped errors, and a comment that only labels the block (`ignore`, `empty`, `TODO`) states no reason.

## Rationale
A dropped error leaves the program running past the point where its assumptions failed: the failing call's work never happened — the rest of a guarded block was skipped, or the code after a call that returned an error runs on a value the call never produced — yet execution proceeds as though it had, and nothing records that it did not, so the state can break its invariants with no trace of the cause. Printing the stack trace writes it to a console stream rather than through the program's logging or error-reporting channel and changes nothing in that execution, so the run that follows is the run of a suppressed error. In 198 sampled user-reported failures of five distributed data-intensive systems, 92% of the 48 catastrophic failures came from incorrect handling of non-fatal errors the software had explicitly signalled, and 35% from trivial mistakes in the handler code that a reader detects without knowledge of the system; the commonest of them, 25% of the catastrophic failures, was a handler that ignored the error, a class that counts a handler that only logs it. Every ignored error but one had been logged, and the handler that took down a 4,000-node production cluster logged the error beside a TODO, so those numbers measure handlers that carry on past an error whether or not they record it — a wider class than this check flags, since a silent handler carries on the same way and also leaves no record of the failure. An empty body cannot be told apart from an unfinished one, so a reader cannot tell a decision from an omission; a comment that states why the error is safe to drop turns the silence into a decision a reviewer can check and dispute.

## Example
```typescript
bad:  try { await store.save(order); } catch (err) {}
      prefetch(order.id).catch(() => {});
good: try { await store.save(order); } catch (err) {
        throw new Error(`saving order ${order.id} failed`, { cause: err });
      }
      prefetch(order.id).catch(() => {
        // prefetch only warms a cache: a miss costs one fetch on first use
      });
```

## Limits
Dropping an error with a stated reason is correct where the error signals an expected, non-exceptional outcome — a parse attempt that falls through to another reading of the input — and where the failure cannot affect later behaviour, such as a failure to release a resource that is never reused, once running out of that resource is handled elsewhere, for which recording it and continuing suffices. In a test, a handler whose empty body is the passing outcome, because the guarded block fails the test when no error arrives, is an assertion rather than a dropped error; the test framework's assert-throws form states it more directly. Linters differ on the mark of deliberate silence — several accept any comment inside the block, one by default accepts only a caught variable named `ignored` or `expected` — and a project context that adopts one of these conventions rejects the finding for a handler that follows it. The check settles silence only: a handler that records the error and continues passes it, although the production-failure study counts log-only handlers among the trivial mistakes; whether execution may continue after a recorded error depends on the program's invariants and is a separate question, as are the breadth of the caught type and whether a raised replacement keeps the original as its cause. A call whose returned error is never bound or tested has no handler to judge and is outside this check. The level a record must take when a handler suppresses an error it does not anticipate is judged by its own rule; a record at any level settles silence here. A failed release of a file or output stream the code wrote to can be the only report of lost data, and whether its error may be dropped is judged by its own rule.

## Validator
In the hunk's added lines, find each handler: a `catch`, `except` or `rescue` clause, a rejection callback, and a branch or match arm taken on a returned error value. Read the handler's whole body in the hunk. Count it as acting when it recovers with a value or state the following code uses, returns or rethrows the error, raises a new error, or records the error through a logger or error reporter; a console call that prints the error with its stack trace counts as a record only where the console is the program's logging channel — the project context says so, or the hunk records its other errors the same way — and as a printed stack trace otherwise. Count it as dropping when the body is empty, holds only `pass` or another no-op, holds only a TODO or FIXME comment, holds only a bare `return` that hands the caller neither the error nor a result that shows the failure, or prints a stack trace and falls through. A dropping body passes when a comment in it states why losing the error is safe; a comment that only labels the block does not. Skip a test handler whose empty body is the passing outcome because the guarded block fails the test when no error arrives, and a handler that follows a silence convention the project context states. Validator question: **Does a handler added in this hunk drop the error — an empty body, a lone no-op, only a TODO or FIXME, only a bare return that hands the caller neither the error nor a result that shows the failure, or only a printed stack trace before execution continues — with no comment stating why dropping it is safe?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: ERR-02`, severity major, `file`, `symbol`, `code` = the handler clause and its body quoted verbatim from the diff, `fix` = the handler rewritten in the file's language to recover, propagate the error, raise an error suited to its level, or record the error — or, where dropping it is correct, the same handler with a comment stating why, `rationale` = which dropping form the handler takes and what the following code assumes that the dropped error leaves unestablished).

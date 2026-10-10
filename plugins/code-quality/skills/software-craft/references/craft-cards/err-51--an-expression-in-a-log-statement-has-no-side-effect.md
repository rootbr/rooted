---
title: An expression inside a log statement has no side effect that later code relies on, because the facility may skip evaluating it
rule_id: ERR-51
domain: errors
step: [implement]
applies_to: [universal]
triggers: ['(?i)([.](debug|info|warn|warning|error|trace|fine)\w*|\blog\w*[.]\w+|\b(debug|info|warn|error|trace)!)\(.*(\w\+\+|\+\+\w|\w--(?!-)|--\w|<-\s*\w|\+=|:=|[.](pop|pop_front|next|poll|take|remove|shift|incrementAndGet|getAndIncrement|send|recv)\(|\bnext\()', '(?i)\bis(debug|trace|info|warn|error|level)enabled\(|\bis(loggable|enabledfor)\(|[.]enabled\([^)]*level|\blog_enabled!\(']
scope: hunk
check_kind: semantic
severity_default: minor
---

# An expression inside a log statement has no side effect that later code relies on, because the facility may skip evaluating it

## Thesis
Every expression a log statement evaluates — its message and value arguments, the body of a supplier or closure passed to it, and the statements inside a level guard that wraps it — reads or computes values and leaves unchanged any state the code after the statement relies on. Where code after the log call or its guard relies on the state it changes, an increment or decrement, an assignment, a pop, poll, take or remove on a collection, an advance of an iterator or cursor, a send or receive, or a call to a method that changes state sits in its own statement before the log call or its guard, and the log call receives the result.

## Rationale
A log statement at a disabled level may never evaluate what it holds. A logging macro checks the level before it logs, and an invocation at a level disabled at build time is skipped and not even present in the built program; a level guard skips the calls inside it when the threshold is set above the statement's level; a supplier passed in place of a message is invoked only when the message actually is to be logged based on the effective level, and a value that computes itself for logging is computed only when the line is enabled. A side effect placed there therefore happens at one log level and not at another: the counter keeps its value, the queue keeps its item, the iterator stays where it was, and the code after the statement sees different state depending on how logging is configured. A statement whose arguments run at every level can lose that property: one facility evaluates the arguments of a log call even when it discards the event, and its documentation advises deferring the computation so that it happens only if the value is actually logged, while a static-analysis rule asks for logger calls to be surrounded by log level guards that skip any method calls in them, noting that such method invocations may be expensive or have side effects. A change made for performance can thus remove a side effect the code depended on. A state change in its own statement before the log call runs at every level and leaves the log call free to be guarded, deferred or filtered.

## Example
```go
bad:  if logger.Enabled(ctx, slog.LevelDebug) {
          logger.Debug("dequeued", "job", jobs.Pop())
      }
good: job := jobs.Pop()
      if logger.Enabled(ctx, slog.LevelDebug) {
          logger.Debug("dequeued", "job", job)
      }
```

## Limits
An expression that only reads or computes — a field, a getter, a size, a conversion or formatting call — follows the rule however much it costs; whether a costly argument is deferred so that a discarded event does not build it is judged by its own rule. A name declared or assigned inside a level guard and read only inside it, as when the guard computes a costly value only for the log call it encloses, changes no state the code after the guard relies on and follows the rule. A facility that evaluates every argument whatever the level does not exempt a side effect, because the deferral its documentation advises would skip it. The rule reaches the expressions of the log statement and of a level guard around it; a state change in a statement of its own before the call or the guard follows the rule, and the event's level, its content and whether it warrants a record are judged by their own rules.

## Validator
Grep the added lines for a log call — a level-named method or macro, or a generic log call that takes a level — and for a level guard: an is-enabled or is-loggable check, or an enabled check given a level. For each hit, read the call's arguments and any supplier or closure passed to it, and, for a guard, the statements it encloses in the hunk. Look for a state change: an increment or decrement, an assignment or assignment expression, a compound assignment, a pop, poll, take, shift or remove on a collection, a next or advance on an iterator, cursor or reader, a channel send or receive, an atomic increment, or a call whose name says it mutates. Skip an expression that only reads or computes: a field, a getter, a size, a conversion or formatting call. Read the lines after the log statement, or after the end of the guard, in the hunk and establish whether they rely on the change: they read the counter or the assigned name, they read the collection, iterator, cursor or channel the expression consumed from, or the expression is the only place in the hunk where that state advances. Validator question: **Does an added log statement, or a level guard around one, carry a state change in its arguments, its supplier or its guarded statements that code after the statement relies on?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: ERR-51`, severity minor, `file`, `symbol`, `code` = the added log statement or guard line that carries the state change, verbatim from the diff, `fix` = the state change moved into its own statement before the log call or its guard, with the log call receiving the result, in the file's language, `rationale` = the state change, the guard, macro, supplier or deferral that can skip it, and the later code that relies on the changed state).

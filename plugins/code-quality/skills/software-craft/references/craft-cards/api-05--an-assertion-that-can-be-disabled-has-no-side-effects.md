---
title: An assertion that the build or runtime can disable evaluates its condition without side effects, so the program behaves the same with assertions on and off
rule_id: API-05
domain: interface
step: [implement]
applies_to: [universal]
triggers: ['(\bassert\b(?![!.])|\bdebug_assert\w*!|\bDCHECK\w*\s*\().*(&\s*mut\b|:=|\+\+|--|\bnext\s*\(|[.](?i:pop|shift|unshift|splice|remove|add|append|extend|put|insert|delete|clear|poll|next|send|write|read|update|push|offer|take|discard|set|fill|sort|reverse|enqueue|dequeue|acquire|release|emit|store|swap|drain|retain|truncate|replace|get_mut|fetch_|getAnd|incrementAnd|decrementAnd|compareAnd)\w*\s*\()', '\b(DEBUG|debug|__DEV__|__debug__|NODE_ENV|debug_assertions)\b.*[.](?i:pop|shift|unshift|splice|remove|add|append|extend|put|insert|delete|clear|poll|next|send|write|update|push|offer|take|discard|enqueue|dequeue|store|swap|getAnd|incrementAnd|decrementAnd|compareAnd)\w*\s*\(']
scope: file
check_kind: mechanical
severity_default: major
---

# An assertion that the build or runtime can disable evaluates its condition without side effects, so the program behaves the same with assertions on and off

## Thesis
Every expression of an assertion or contract check that a setting can switch off evaluates without side effects. Such settings include an interpreter's optimize flag, a runtime that leaves assertions off unless a launch option enables them, an optimized or release build, a build option that strips the call, and a debug flag fixed at build or start time that guards the check. That expression removes, pops and assigns nothing, and calls no routine that mutates its receiver or an argument; the one exception is a name it binds that is referenced only from inside assertions. Work the program needs runs in its own statement before the assertion, and the assertion tests the stored result, so the program behaves the same with assertions on and off.

## Rationale
A disabled assertion does not evaluate its expression. Under the optimize flag the code generator emits no code for the assertion statement; a runtime that disables assertions by default in all packages and classes skips them unless a launch option enables them; an optimized build does not execute debug-only assertions unless a compiler option turns them back on; a build that defines the debug flag as false removes the guarded code as dead code; and a build option that drops a call removes the entire call expression, its arguments included. Any side effect of the expression is lost with it, so program behaviour depends on whether assertions are enabled: an element the assertion was to remove stays in the list, the result of the routine might change, and a name bound inside the assertion and read after it may be undefined. A debug-only check that disappears from production builds is verified only where it is enabled, such as in tests and on developer machines; a side effect intended to happen inside it disappears from production along with it, the release build behaves differently from the debug build, and unexpected behaviour can follow. Logic required for correct program function therefore does not rely on an assertion being executed: written as its own statement, the work runs in every configuration, and the assertion tests what it stored.

## Example
```typescript
bad:  if (DEBUG) assert(queue.shift() === job);  // DEBUG is false in release builds
      run(job);
good: const head = queue.shift();
      if (DEBUG) assert(head === job);
      run(job);
```

## Limits
A check documented as running in both debug and release builds, one that cannot be disabled, evaluates its expression in every configuration; a side effect inside it is not lost, and the rule does not reach it. All argument expressions are evaluated before a call is attempted, so an assertion routine that tests the debug flag inside its own body receives its arguments in every configuration, and a build option that removes such calls without removing arguments with side effects does not introduce bugs; the rule reaches a call only where a flag guards it from outside, the build removes the call with its arguments, or an argument is a closure that the routine calls only when the flag is on. A name that the expression binds and that is referenced only from inside assertions, in the assertion's message or a later assertion, is outside the rule. A condition that only reads state follows the rule however costly it is: a check too expensive to be present in a release build is what a debug-only assertion is useful for. An assertion in a test file is outside the rule: test code does not ship, and a test runner that rewrites a test module's assertions into ordinary checks evaluates them in every configuration.

## Validator
Grep the added lines for an assertion whose condition or message removes, pops, pushes, inserts, deletes, clears, advances an iterator, increments, assigns, writes, sends, or passes a mutable reference: an `assert` keyword statement, an assertion macro the build can define away, a debug-only assertion such as `debug_assert` or `DCHECK`, or an assertion call behind a debug, development or non-production flag. Open the file and read the blocks enclosing the assertion to settle whether a setting can switch it off. Skip a test file. A keyword assertion statement, a debug-only or build-definable macro, a block compiled only into debug builds, and a check behind a flag fixed at build or start time can be switched off. A check documented as running in every build, a test framework's assertion method, an assertion routine called with no outside guard and no closure argument, and an assertion-module call with no guard cannot, unless the hunk shows a build option that drops the call with its arguments. Confirm that the expression changes state: a standard mutator of a collection, an iterator, a counter, a lock, a stream or a channel does; a call whose effect the line and the file leave unsettled is not flagged. Skip a name bound inside the assertion when every use of it in the file is inside an assertion. Validator question: **Does an added assertion that a flag, an optimization level or a build can switch off change, in any of its expressions, any state other than a name it binds that only assertions reference?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: API-05`, severity major, `file`, `symbol`, `code` = the assertion line holding the side effect, verbatim from the diff, `fix` = the side-effecting work as its own statement that stores its result, followed by the same assertion testing the stored value, in the file's language, `rationale` = the side effect, the setting that switches the assertion off, and what the program does differently with assertions off).

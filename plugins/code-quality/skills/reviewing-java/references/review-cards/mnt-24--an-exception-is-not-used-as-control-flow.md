---
title: An exception the method itself raises or provokes is not caught in that same method as a branch
rule_id: MNT-24
domain: maintainability
triggers: ['catch\s*\(\s*(NumberFormatException|NoSuchElementException|IndexOutOfBoundsException|ArrayIndexOutOfBoundsException|ClassCastException|NullPointerException|IllegalArgumentException)\b', 'throw new \w+\(', 'catch\s*\(']
scope: file
check_kind: mechanical
severity_default: minor
---

# An exception the method itself raises or provokes is not caught in that same method as a branch

## Thesis
A method does not use an exception it catches itself as a branch, whether it throws the exception with its own `throw` inside the `try` or provokes it from a condition it could have tested — a value that fails a check, a key that may be absent, an index that may be out of range, a reference that may be `null`; the condition is tested with a plain check, an early `return` or an `Optional`, and the `throw`-and-`catch` in one method, which is a `goto`, is not written.

## Rationale
An exception used as a branch hides the actual exceptions of the same type thrown for real failures inside the `try` — the same type raised by a callee for a genuine error, a `NullPointerException` from a bug — so the handler takes the normal branch on a genuine error; the control flow reads backwards, from the `catch` up to the `throw`, and a debugger set to break on exceptions stops on every ordinary iteration. The plain test says what it checks in the condition and leaves the exception path for the failures it was made for.

## Example
```java
bad:  try { for (Line l : lines) { if (l.qty() < 0) throw new BadLine(); total += l.qty(); } }
      catch (BadLine e) { return Optional.empty(); }                        // thrown to be caught one line down
      try { for (int i = 0; ; i++) { use(items[i]); } } catch (ArrayIndexOutOfBoundsException e) { }
good: for (Line l : lines) { if (l.qty() < 0) return Optional.empty(); total += l.qty(); }
      for (int i = 0; i < items.length; i++) { use(items[i]); }
```

## Limits
A library whose only failure signal is an exception (a parser without a result-returning variant, such as `Integer.parseInt`) leaves the caller no choice; catching the specific type immediately around that one call, with a comment, is tolerated. Catching an exception from a remote call to decide a retry is handling, not flow control. The cost of constructing exceptions on a hot path is a separate concern.

## Validator
On the triggered hunk find each `throw` whose enclosing `try` in the same method catches that type, and each `catch` of a predictable-outcome exception type. Open the file to see whether the caught outcome could have been tested before the call. Validator question: **is this exception raised or provoked by the method itself and caught by the method's own catch as a branch?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: MNT-24`, severity minor, `file`, `symbol`, `code` = the try/catch quoted verbatim from the diff, `fix` = the plain test or the early return, `rationale` naming the real failure the catch would swallow).

## Source
PMD `ExceptionAsFlowControl` — "This rule reports exceptions thrown and caught in an enclosing try statement. This use of exceptions as a form of goto statement is discouraged, as that may hide actual exceptions, and obscures control flow, especially when debugging. To fix a violation, add the necessary validation or use an alternate control structure". PMD `AvoidCatchingGenericException` — `NullPointerException` "usually indicates a programming error … Rather than catching it, code should be written to avoid null pointer dereferences through null checks". Caveat: the rule states the throw-and-catch-in-one-try form; the tested-rather-than-caught form (the index loop) rests on its "add the necessary validation" remedy, and a parse whose only failure signal is an exception is not this rule.

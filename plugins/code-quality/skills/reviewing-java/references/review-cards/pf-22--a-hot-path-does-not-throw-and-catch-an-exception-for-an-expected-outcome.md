---
title: A hot path does not throw and catch an exception to decide an expected outcome; it tests the condition or uses a non-throwing API
rule_id: PF-22
domain: performance
triggers: ['catch \((NumberFormatException|NoSuchElementException|IndexOutOfBoundsException|ArrayIndexOutOfBoundsException|ClassCastException|NullPointerException|IllegalArgumentException|DateTimeParseException|ParseException|UnsupportedOperationException)', 'parse(Int|Long|Double)\(', 'catch \([^)]*\)\s*\{\s*(return|continue|break)', 'fillInStackTrace', 'throw new \w*Exception\(']
scope: hunk
check_kind: mechanical
severity_default: minor
---

# A hot path does not throw and catch an exception to decide an expected outcome; it tests the condition or uses a non-throwing API

## Thesis
On a per-request, per-record or per-iteration path, an outcome that occurs routinely — a non-numeric field, a missing key, an end of collection, an invalid format — is detected by a test or a non-throwing API (`Optional`, a `tryParse` helper, `containsKey`, `Iterator.hasNext`, a bounds check, `matcher.matches()` before `parse`) rather than by throwing and catching an exception.

## Rationale
Creating an exception fills in its stack trace: the constructor records the state of every stack frame of the current thread, work proportional to the depth of the stack at the throw site, before the exception is even thrown; catching it then unwinds through each frame. Paid once per bad record on a hot path, that is a fixed cost per iteration that a comparison would replace. The just-in-time compiler may substitute a pre-allocated, trace-less exception for some hot implicit throws in compiled code, which is why the cost sometimes disappears in a benchmark and reappears with a different exception type, a deeper stack or after deoptimization. Exceptions also carry the reader's expectation that the path is rare.

## Example
```java
bad:  int port(String s) {
          try { return Integer.parseInt(s); } catch (NumberFormatException e) { return -1; }
      }
good: int port(String s) {
          return DIGITS.matcher(s).matches() ? Integer.parseInt(s) : -1;
      }
```

## Limits
A genuinely rare failure on a hot path — a corrupted record among millions — is correctly handled by an exception. Validation at an API boundary that runs once per request, and code where no non-throwing alternative exists (some third-party parsers), are out of scope; there a custom exception constructed with `writableStackTrace = false` limits the cost. Whether the exception is swallowed, translated or logged is a separate concern.

## Validator
On the triggered hunk find each `try`/`catch` whose catch block returns a default, continues a loop or otherwise treats the exception as a normal result, and each throw of an exception for a condition the caller expects and handles. Confirm the enclosing code is per request, per record or per iteration. Validator question: **does this hot path throw and catch an exception to signal an outcome that a test or a non-throwing API could report?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PF-22`, severity minor, `file`, `symbol`, `code` = the `try`/`catch` or the throw quoted verbatim from the diff, `fix` = the test or the non-throwing API, `rationale` naming the stack-trace capture per throw).

## Source
`java.lang.Throwable#fillInStackTrace` Javadoc, Java SE 21 — "Fills in the execution stack trace. This method records within this Throwable object information about the current state of the stack frames for the current thread"; `Throwable(String, Throwable, boolean enableSuppression, boolean writableStackTrace)` — the constructor that skips the stack trace when `writableStackTrace` is false. JMH benchmarks `ionutbalosin/jvm-performance-benchmarks`, `.../compiler/StackTraceBenchmark.java` — "the costs of constructing a stack trace are proportional to the depth of the Java stack at the moment of exception instantiation"; with the HotSpot default `-XX:+OmitStackTraceInFastThrow` "the compiler may choose a faster approach using pre-allocated exceptions that do not include a stack trace" for hot exceptions in optimized code; `.../compiler/NpeThrowBenchmark.java` — implicit versus explicit null-pointer exceptions at 0%, 50% and 100% throw rates.

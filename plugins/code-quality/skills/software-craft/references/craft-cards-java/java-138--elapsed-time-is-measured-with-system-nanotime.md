---
title: Elapsed time and timeouts are measured with System.nanoTime, never with the wall clock
rule_id: JAVA-138
domain: tooling
step: [implement]
applies_to: [java]
triggers: ['currentTimeMillis\(\)', 'Instant[.]now\(\)', 'new Date\(\)', 'LocalDateTime[.]now\(\)', 'elapsed', 'nanoTime\(\)']
scope: hunk
check_kind: mechanical
severity_default: major
---

# Elapsed time and timeouts are measured with System.nanoTime, never with the wall clock

## Thesis
A duration — how long an operation took, whether a deadline has passed, how long to wait — is computed as the difference of two `System.nanoTime()` readings (or through a `Ticker`/stopwatch abstraction built on `nanoTime`), not from `System.currentTimeMillis()`, `Instant.now()`, `new Date()` or `LocalDateTime.now()`, which are wall-clock readings.

## Rationale
The wall clock is set by the operating system and can step forward or backward at any moment: an NTP correction, an administrator's change, a virtual-machine migration. A duration computed from two wall-clock readings across such a step is wrong by the size of the step, can be negative, and a timeout loop that compares `currentTimeMillis()` against a deadline can wait far longer than intended or expire at once. `System.nanoTime()` reads the running virtual machine's high-resolution time source, is "not related to any other notion of system or wall-clock time", and is defined only for differences between two readings in the same virtual machine, which is exactly a duration. Its origin is arbitrary, so a single reading has no meaning as a timestamp, which is why the two clocks are not interchangeable in either direction. The comparison form `nanoTime() - start >= timeoutNanos` avoids the overflow that `nanoTime() >= start + timeoutNanos` can hit.

## Example
```java
bad:  long start = System.currentTimeMillis();
      work();
      long elapsedMs = System.currentTimeMillis() - start;
good: long start = System.nanoTime();
      work();
      long elapsedMs = (System.nanoTime() - start) / 1_000_000;
```

## Limits
A wall-clock reading used as a timestamp — a `createdAt` field, a log line, an expiry stored for another process — is correct and is not flagged; the rule is about differences. A test that injects a `Clock` and measures against it is out of scope. A duration that spans processes or machines cannot use `nanoTime` and takes the wall clock with the step risk accepted; a comment naming that trade-off rejects the finding.

## Validator
On the triggered hunk find each wall-clock reading (`currentTimeMillis`, `Instant.now`, `new Date`, `LocalDateTime.now`, `ZonedDateTime.now`) whose value is subtracted from, or compared with, another reading of the same clock in the same process to obtain a duration, a deadline check or a sleep amount. Validator question: **is a wall-clock reading used to compute how much time has passed within this process?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: JAVA-138`, severity major, `file`, `symbol`, `code` = the two readings and the subtraction quoted verbatim from the diff, `fix` = the same measurement with `System.nanoTime()` and the overflow-safe comparison form, `rationale` naming the clock step that makes the difference wrong).

---
title: A runtime invariant names the test, benchmark or production signal that enforces it
rule_id: META-03
domain: meta
triggers: ['^\s*\d+[.]\s+\*\*', '[Ii]nvariant', '(?i)latenc|throughput|allocat|heap|lock|block|p9[059]|hot path', '(?i)enforced by|benchmark|JFR|metric|alert']
scope: file
check_kind: mechanical
severity_default: minor
---

# A runtime invariant names the test, benchmark or production signal that enforces it

## Thesis
An invariant about runtime behaviour — allocation, latency, throughput, memory, blocking, lock hold time — names its evidence handle: the test class, benchmark, JFR event, metric or alert that fails or fires when the rule is broken (`Enforced by …`). A reviewer can read a diff for a structural rule; a runtime rule is verified only by running something, and the invariant says what.

## Rationale
A decision record states how compliance with the decision can be confirmed — an automated or manual fitness function, a design review, a test with a library that checks architecture rules — and lists it, because a record without it is a statement of intent. Architecture and coding rules can be tested automatically with a plain unit-testing framework, so a structural rule has an executable form the config can name. A runtime rule has no lexical signature in a diff: whether a change moved an allocation onto the hot path or raised a p99 shows up only in a benchmark, a profiler event or a production metric. Without a named handle the reviewer can only read-check the change and the rule is never re-verified after the review; with one, a finding cites the run that will fail.

## Example
```java
bad:  3. **tick never blocks**: `RequestLoop#tick` never blocks on I/O.
         Violation: a blocking call inside `RequestLoop#tick`.
good: 3. **tick never blocks**: `RequestLoop#tick` never blocks on I/O.
         Violation: a blocking call inside `RequestLoop#tick`. Enforced by
         `RequestLoopTickBench` (JMH, p99 < 120 µs on the canary) and the
         `jdk.ThreadPark` JFR event recorded on the canary.
```

## Limits
Applies to an invariant whose subject is runtime behaviour. A structural invariant — a dependency direction, a package boundary, a naming or annotation rule — can be checked by reading the diff; naming its ArchUnit rule is welcome and its absence is tolerated. A functional rule on values — a bound a method rejects, a field that stays within a range — is checked by reading the change against the rule and is tolerated without a handle in the same way. A handle named once in an evidence or enforcement section of the same config and referenced by the invariant's number counts as present.

## Validator
Open the config at HEAD and take each numbered invariant the diff adds or changes. Classify it: structural (dependency, package, naming, annotation) or functional (a value bound, a rejected input) versus runtime (allocation, latency, throughput, memory, blocking, locking). For a runtime invariant, grep its text and the config's evidence section for a named test class, benchmark, JFR event, metric or alert. Validator question: **is this a runtime invariant with no named test, benchmark, event, metric or alert that fails when it is broken?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: META-03`, severity minor, `file` = the config path, `symbol` = `Inv <N>` for the invariant's number, `code` = the invariant line quoted verbatim from the diff, `fix` = the invariant with an `Enforced by` clause naming the handle, `rationale` naming that a runtime rule cannot be verified by reading the diff).

## Source
MADR `template/adr-template.md` (`adr/madr`, `main`) §Confirmation — "Describe how the implementation / compliance of the ADR can/will be confirmed. Is there any automated or manual fitness function? If so, list it and explain how it is applied … a design/code review or a test with a library such as ArchUnit can help validate this"; the template marks the section optional and notes it "is included in many ADRs". ArchUnit user guide §Introduction — "ArchUnit's main focus is to automatically test architecture and coding rules, using any plain Java unit testing framework". The runtime/structural bound, and the reading of a rule without a handle as a statement of intent, are the card's narrowing of that optional section; the sources state that compliance is confirmed by a listed fitness function and that rules are testable automatically.

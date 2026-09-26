---
title: A log call's level matches the event, with ERROR for a serious failure that prevents normal execution, WARN for a potential problem, INFO for a reasonably significant message and DEBUG for detailed tracing
rule_id: MNT-32
domain: maintainability
triggers: ['(LOGGER|LOG|logger|log)\w*[.]error\(', '(LOGGER|LOG|logger|log)\w*[.]warn\(', '(LOGGER|LOG|logger|log)\w*[.]info\(', '(LOGGER|LOG|logger|log)\w*[.](debug|trace)\(']
scope: file
check_kind: semantic
severity_default: suggestion
---

# A log call's level matches the event, with ERROR for a serious failure that prevents normal execution, WARN for a potential problem, INFO for a reasonably significant message and DEBUG for detailed tracing

## Thesis
The level of each logging statement matches what the code around it does with the event: `error` for a serious failure — an event of considerable importance that prevents normal program execution, such as an operation that did not complete; `warn` for a potential problem — a condition detected and dealt with, such as a retry that then succeeded, a fallback used, an input rejected; `info` for a reasonably significant message that makes sense to end users and system administrators — started, order placed, job finished with counts; `debug`/`trace` for relatively detailed tracing — per item, per step, per request. An `error` on a retry that then succeeds, and an `info` inside a per-element loop, are mismatches.

## Rationale
Levels are the contract between the code and the people who run it: the severe level describes events of considerable importance that prevent normal execution, the warning level a potential problem of interest to system managers, the info level reasonably significant messages that make sense to end users and administrators, and the fine levels relatively detailed tracing. An `error` on a handled condition pages someone for nothing and trains them to ignore errors; an `info` per element floods the production log and buries the events it was meant to show; a real failure logged at `debug` is invisible. Alerting, retention and sampling are all keyed on the level.

## Example
```java
bad:  catch (Timeout e) { log.error("timeout for {}, retrying", key); result = call(key); }   // the retry succeeds: a potential problem, not a failure
      for (Item i : items) { log.info("processing {}", i.id()); }                          // per element: detailed tracing
good: catch (Timeout e) { log.warn("timeout for {}, retrying", key); result = call(key); }
      log.info("processed {} items for order {}", items.size(), orderId);
```

## Limits
A logging policy in the project context (which events are `warn`, whether `info` is per request) overrides the defaults here. A CLI tool or a batch job may log per item at `info` by design. Secrets or personal data in the message are a different concern.

## Validator
On the triggered hunk read each logging call with the code around it: what follows (`throw`, fallback, `continue`, nothing), whether it sits inside a loop or a per-request path, and what the message describes. Validator question: **does the level disagree with what the surrounding code does with the event — an error that is handled, a per-element info, a failure at debug?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: MNT-32`, severity suggestion, `file`, `symbol`, `code` = the log call quoted verbatim from the diff, `fix` = the same call at the matching level, `rationale` naming the operator consequence — a false page, a flooded log, a hidden failure).

## Source
`java.util.logging.Level` Javadoc, Java SE 21 — `SEVERE` "a message level indicating a serious failure … events that are of considerable importance and which will prevent normal program execution"; `WARNING` "indicating a potential problem … events that will be of interest to end users or system managers"; `INFO` "should only be used for reasonably significant messages that will make sense to end users and system administrators"; `FINE`, `FINER`, `FINEST` "intended for relatively detailed tracing". SLF4J `slf4j-jdk14` `JDK14LoggerAdapter` — `error` maps to `SEVERE`, `warn` to `WARNING`, `info` to `INFO`, `debug` to `FINE`, `trace` to `FINEST`.

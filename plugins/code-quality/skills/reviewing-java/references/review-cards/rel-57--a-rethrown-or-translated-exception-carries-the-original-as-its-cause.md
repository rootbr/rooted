---
title: An exception thrown from a catch block carries the caught exception as its cause, and a caught ExecutionException is reported by its getCause()
rule_id: REL-57
domain: reliability
triggers: ['catch \(', 'throw new \w+\([^)]*getMessage\(\)', 'throw new \w+\(\)', 'ExecutionException', 'getCause\(\)', 'CompletionException']
scope: hunk
check_kind: mechanical
severity_default: minor
---

# An exception thrown from a catch block carries the caught exception as its cause, and a caught ExecutionException is reported by its getCause()

## Thesis
When a catch block throws a new exception — to translate a checked type, to add context, to cross a layer — the new exception is constructed with the caught one as its cause (`new X(message, e)`), not with `e.getMessage()` alone or with no argument; and a caught `ExecutionException` or `CompletionException` is matched and reported by its `getCause()`, never by the wrapper's type, so the task's real failure is what the record shows.

## Rationale
A throwable "can also contain a cause: another throwable that caused this throwable to be constructed", and throwing "a 'wrapped exception' (i.e., an exception containing a cause) allows the upper layer to communicate the details of the failure to its caller". Without the cause, "the stack trace will terminate at the catch block", so the record of the failure begins where it was caught rather than where it happened, and the original type — the one that distinguishes a timeout from a constraint violation from a bug — is gone. `ExecutionException` is "thrown when attempting to retrieve the result of a task that aborted by throwing an exception", and "can be inspected using the getCause() method": a translation or a match on the wrapper's own type reports "task failed" for every failure alike, whatever the task threw.

## Example
```java
bad:  catch (IOException e) { throw new ImportException("import failed: " + e.getMessage()); }
      catch (ExecutionException e) { throw new TaskFailedException(id); }
good: catch (IOException e) { throw new ImportException("import of " + file + " failed", e); }
      catch (ExecutionException e) { throw new TaskFailedException(id, e.getCause()); }
```

## Limits
A deliberately opaque translation at a trust boundary — a security exception that must not reveal its cause to the caller — is correct when the cause is logged inside the boundary and a comment says so. A catch that maps a known exception to a documented result value throws nothing and is out of scope. An exception type without a cause constructor may use `initCause`.

## Validator
On the triggered hunk find each `throw new ...` inside a `catch` and check its arguments for the caught exception; find each catch of `ExecutionException`/`CompletionException` and check that `getCause()` — not the wrapper — is what is passed as the cause, matched on, or named in the record. Validator question: **does this catch block throw a new exception without the caught one as its cause, or match or report an `ExecutionException`/`CompletionException` by the wrapper's type instead of its `getCause()`?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: REL-57`, severity minor, `file`, `symbol`, `code` = the throw or the match quoted verbatim from the diff, `fix` = the caught exception (or its `getCause()`) passed as the cause or matched on, `rationale` naming the stack trace and type that are lost).

## Source
`java.lang.Throwable` class Javadoc, Java SE 21 — "the throwable can also contain a cause: another throwable that caused this throwable to be constructed. The recording of this causal information is referred to as the chained exception facility"; "Throwing a 'wrapped exception' (i.e., an exception containing a cause) allows the upper layer to communicate the details of the failure to its caller"; `#Throwable(String, Throwable)`. `java.util.concurrent.ExecutionException` — "Exception thrown when attempting to retrieve the result of a task that aborted by throwing an exception. This exception can be inspected using the getCause() method". Error Prone `UnusedException` — "Throwing a new exception without supplying the caught one as a cause means the stack trace will terminate at the catch block".

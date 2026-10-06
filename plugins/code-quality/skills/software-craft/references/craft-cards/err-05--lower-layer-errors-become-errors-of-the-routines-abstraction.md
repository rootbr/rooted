---
title: A routine whose abstraction hides a lower layer translates that layer's errors into errors of its own abstraction instead of letting them escape its interface
rule_id: ERR-05
domain: errors
step: [design, handle-errors]
applies_to: [universal]
triggers: ['\b(SQL|Sql|IO|Io|OS|Http|HTTP|Json|JSON|Xml|XML|Remote|Socket|Connection|Timeout)\w*(Exception|Error)\b', '\bexcept\s+\(?\s*(sqlite3|psycopg2?|requests|urllib3|botocore|sqlalchemy|redis)\b', '\bfmt[.]Errorf\([^)]*%w', '\berrors[.](Is|As)\([^)]*\b(sql|io|os|fs|net|http)[.]\w+', '\b(io|sqlx|reqwest|serde_json|rusqlite|hyper|diesel::result)::Error\b']
scope: file
check_kind: semantic
severity_default: minor
---

# A routine whose abstraction hides a lower layer translates that layer's errors into errors of its own abstraction instead of letting them escape its interface

## Thesis
A routine whose interface presents an abstraction built atop a lower layer — a database driver, a file system, a network or serialization library that its callers neither see nor supply — reports that layer's failures as errors of its own abstraction. Its declared, thrown and returned error types, and every error it offers callers to match on, belong to its abstraction; the lower error travels along as the cause, or in the message, where callers or operators need the details. A lower-layer error type reaches the callers only where the interface documents it as part of its contract. At a boundary to another system — RPC, IPC, storage — it is often better to report the boundary's standardized error space, a canonical status such as internal, not-found or permission-denied, than the raw underlying error. The translation covers the lower layer's own failures; a fatal runtime error such as running out of memory passes through untranslated.

## Rationale
An error raised by a lower layer is generally unrelated to the abstraction the upper layer provides: a caller that asked to load an order receives a driver's error code or a file-system path error it has no terms to interpret. Letting that error through also ties the upper interface to its implementation. Where the lower error is a declared error, the upper signature carries it; where callers can match on it, the routine has to keep producing that exact error even after it switches to another database package, because an error exposed for inspection becomes part of the interface. An error of the routine's own abstraction that carries the lower one as a cause callers do not match on, or quotes it in its message, communicates the details of the failure and keeps the freedom to change the implementation without changing the interface, that is, the set of errors the routine reports. Whether the lower error is wrapped for inspection or only quoted in the message decides what programs may come to depend on. At a boundary to another system the client typically cares about the canonical result, not about the exact internal file-system error. The translation stops at the lower layer's own failures: an unexpected cross-type wrapping that hides an out-of-memory error inside a checked error was one of three exception-handling bug hazards found in 6,005 exception stack traces mined from 159,048 issues of 639 Android projects, a hazard that can make the handling code more complex and harm the application's robustness.

## Example
```java
bad:  public Order load(String id) throws SQLException {
          return map(query(id));
      }
good: public Order load(String id) {
          try { return map(query(id)); }
          catch (SQLException e) { throw new StoreException("load order " + id, e); }
      }
```

## Limits
The rule does not reach a lower-layer object the caller supplies: a routine that reads from a reader, a connection or a callback passed in may expose that object's errors, wrapped for inspection, since they belong to the caller's own context. An interface that documents a lower error as part of its contract — committing to return it through any change of implementation, and testing that it does — exposes it correctly. Within one layer, a private helper or an internal routine whose caller is the same layer returns the error unchanged when it has nothing to add, or wraps it with context for its caller to inspect; the translation belongs at the interface that hides the layer. A thin adapter whose abstraction is the lower layer itself has no higher abstraction to translate into. A fixed general-purpose interface that admits no checked error of the lower layer is satisfied by wrapping the lower error in an unchecked error that the implementation's specification names. A project context that declares a lower layer's error types part of its public interface rejects the finding.

## Validator
Grep the hunk for a signature, a catch or except clause, an error return or an error match that names an error type of a lower layer — a driver, file-system, network or serialization error — or that wraps one for callers to inspect. Open the file and decide whether the routine sits on an interface that hides that layer: an exported or public routine of a module or type whose callers neither see nor supply the lower-layer object, or a handler at an RPC, IPC or storage boundary. Trace what the routine lets out: its declared error types, the type it throws or returns on the lower failure, and whether its error chain is offered to callers to match on; read its doc-comment for a documented commitment to the lower error. Check the breadth of a catch that translates, and whether it also sweeps a fatal runtime error into the domain error. Validator question: **Does a routine on an interface that hides a lower layer let that layer's error type reach its callers — declared, rethrown, returned or wrapped for inspection — without the interface documenting it, or fold a fatal runtime error into its own error?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: ERR-05`, severity minor, `file`, `symbol`, `code` = the signature, clause or return that lets the lower error out, quoted verbatim from the diff, `fix` = the lower failure caught and reported as an error of the routine's own abstraction — a canonical status at a system boundary — that carries the lower error as a cause callers do not match on, or quotes it in its message, in the file's language, `rationale` = the lower layer the interface hides and the implementation detail its error type ties the interface to).

## Source
OpenJDK 21 `java.lang.Throwable` class Javadoc, chained-exception paragraphs — "It would be bad design to let the throwable thrown by the lower layer propagate outward, as it is generally unrelated to the abstraction provided by the upper layer"; "It preserves the flexibility to change the implementation of the upper layer without changing its API" (fetched). Google Go Style Guide, Best Practices §Adding information to errors — "it's often better to translate domain-specific errors into a standardized error space (e.g., gRPC status codes) rather than simply wrapping the raw underlying error"; "When you explicitly document and test the underlying errors you expose ... This forms part of your package's contract"; "just return err instead" (fetched). Go project, "Working with Errors in Go 1.13" (golang/website `_content/blog/go1.13-errors.md`) §Whether to Wrap — "Do not wrap an error when doing so would expose implementation details"; "wrapping an error makes that error part of your API"; "Since the caller provided the `io.Reader` to the function, it makes sense to expose the error produced by it" (fetched). CPython tutorial `Doc/tutorial/errors.rst` §Exception Chaining — "This can be useful when you are transforming exceptions" (fetched). DOI 10.1109/MSR.2015.20, abstract — "(i) unexpected cross-type exception wrappings (for instance, trying to handle an instance of Out Of Memory Error "hidden" in a checked exception) which can make the exception-related code more complex and negatively impact the application robustness" (relayed). Caveat: the system-boundary translation is "often better", not absolute, and the fatal-error bound rests on one study of Android apps on one exception model.

---
title: A routine reports failure through the mechanism its language and codebase use for failures, not through a status code or an ad-hoc error field that brings a second convention in
rule_id: ERR-03
domain: errors
step: [design, implement, handle-errors]
applies_to: [universal]
triggers: ['\breturn\s+\{\s*\W?(ok|success|error|err)\W?\s*:|\b(ok|success)\W?\s*:\s*(false|False)\b', '\breturn\s+(.*,\s*)?-1\b', '(?i)\b(error|err|status|ret)_?code\b\s*[=:]', '\breturn\s+\[?\s*(None|null|undefined|False)\s*,', '\bpanic!?\(', '\b(throw|raise)\b']
scope: file
check_kind: semantic
severity_default: minor
---

# A routine reports failure through the mechanism its language and codebase use for failures, not through a status code or an ad-hoc error field that brings a second convention in

## Thesis
A routine that cannot do what its name promises reports that execution failure through the one mechanism its codebase uses for failures. Where failures propagate as exceptions, it throws. Where failures are returned as values, it returns the codebase's error or result value, and it reserves a process abort (a panic) for a broken invariant or an unrecoverable state rather than an expected failure such as malformed input or a rate-limit response. The mechanism is the language's idiom unless the codebase departs from it, by a documented rule or throughout its existing code, so the check is consistency with that established convention, not a preference for either side: a status code, an in-band sentinel such as -1, or a returned object, tuple or field that carries an error beside the convention's own mechanism is the defect. A documented non-throwing try-form published beside a throwing member, and a null or default value returned for a common error case, belong to the exception convention.

## Rationale
Callers are written against the codebase's failure mechanism. An in-band status or sentinel works only if every caller remembers to test it; a caller that does not passes the sentinel on as a valid value, which can lead to bugs and can attribute the error to the wrong function. In a codebase whose callers handle failure in catch blocks and let the rest propagate, a returned code needs error-prone bookkeeping at every level between the failure and its handler, bookkeeping those callers were not written to do, so it slips past them unexamined. In a codebase whose callers check a returned error, a thrown exception or a panic unwinds through callers that were not written to be safe against it: adding a throw to one routine obliges a review of all its transitive callers, which is why one large codebase that is not exception-tolerant forbids them. An abort on an expected failure also takes the recovery decision away from the caller, which could have retried, reported, or chosen to abort itself. Keeping one mechanism gives callers one failure path they can see in the signature or the documented contract.

## Example
```go
bad:  func parsePort(s string) int {
          ...
          return -1
      }
good: func parsePort(s string) (int, error) {
          ...
          return 0, fmt.Errorf("parse port %q: %w", s, err)
      }
```

## Limits
The rule is contested in general and holds by convention. The exception-language guidance states "DO NOT return error codes" and "Prefer throwing exceptions over ad-hoc error-handling approaches (such as passing an error container reference type, or returning an object with an error property)"; the error-value languages' own documentation states "returning `Result` is a good default choice when you’re defining a function that might fail" and "Do not use `panic` for normal error handling. Instead, use `error` and multiple return values." The separating condition is the codebase's established mechanism: the language idiom, or the codebase's own rule where it departs from the idiom, documented as a style guide that forbids its language's exceptions does, or followed throughout its existing code, whose callers were written for it. A codebase that has adopted a result type throughout an exception language, recorded in its style guide or in `project_context`, or followed by every other failing routine in the file, is judged by that type; a lone routine that returns a result object in a codebase that throws, or that throws in a codebase that returns error or result values, is the finding. Not a finding: a try-form beside a throwing member that returns a boolean and still throws for any failure other than its one well-defined case, a tester member callers check before the call, or a null or default value returned for a common error case, which the exception convention offers for members that fail in common scenarios, to avoid the performance cost of throwing, since throw rates above 100 per second are likely to noticeably impact the performance of most applications; a second boolean found-result on a lookup where no explanation is needed; an aborting set-up helper published beside an error-returning member and named for its abort, meant for start-up rather than for user input; a panic on a broken invariant, a caller's violation of a precondition the routine documents, an impossible state, a failed start-up that leaves the program unable to set itself up, in tests, examples and prototypes, or one recovered into an error value before it leaves the package; a comparator's -1, a search's not-found index in a family that uses that sentinel, a status code written to a protocol response, and a process exit status, which belong to that interface's contract rather than to the routine's failure path.

## Validator
Read the added line the trigger matched: a returned sentinel or status code, a returned object, tuple or array with an error or ok member, an error-code variable or field, a throw or raise, or a panic. Open the file and establish its failure convention from its other routines — do failing routines throw, or return an error or result value; where none fails, the language's idiom is the convention — and read `project_context` for a documented departure. Where the file calls the routine, note whether each caller tests the returned sentinel or field. Decide whether the flagged value, throw or abort reports an execution failure, the routine unable to do what its name promises, rather than an ordinary result. Check each exemption in Limits before flagging. Validator question: **Does this routine report an execution failure through a status code, sentinel, error-carrying object, throw or abort while its file or codebase reports failures through a different mechanism?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: ERR-03`, severity minor, `file`, `symbol`, `code` = the return, assignment, throw or panic line that carries the failure, quoted verbatim from the diff, `fix` = the routine's signature and failing return, throw or panic rewritten to throw an exception or to return the codebase's error or result value, in the file's language, `rationale` = the file's failure mechanism and the caller that can now miss the failure or blame it on the wrong routine).

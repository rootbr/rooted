---
title: A bug fix corrects the fault that produces the failure rather than stopping the failure where it surfaces or special-casing the input that exposed it
rule_id: PRF-02
domain: performance
step: [implement, review]
applies_to: [universal]
triggers: ['(?i)\b(work-?around|hack|band-?aid|kludge|special[- ]?case)\b', '\b(if|elif|else if|when)\b.*(==|===|[.]equals\()\s*("[^"]*"|''[^'']*''|-?\d{2,})', 'signal:empty_handler']
scope: callers
check_kind: semantic
severity_default: major
---

# A bug fix corrects the fault that produces the failure rather than stopping the failure where it surfaces or special-casing the input that exposed it

## Thesis
A change presented as a bug fix corrects the fault, the code that produces the failure, reached by following the failure back to its root cause. A change that only stops the failure from occurring while the fault stays (an edit to the code where the failure shows, a case for the one input that exposed it, or an error suppressed where it is raised) patches the failure and leaves the fault in place.

## Rationale
The failure and the fault can sit in different code: in one studied debugging task the failure showed when a square figure was rotated, while the fault was an invalid configuration of that figure's number of possible orientations. Ideally, debugging is guided by an understanding of the failure to a root cause; in practice that does not always happen. Through experimentation and manipulation of the program, a developer can stop the failure from occurring without actually fixing the fault: in that task quite a few graduate-student participants did not correct the configuration but modified the rotation calculation code to bypass the failure, one of several occurrences of this phenomenon the study observed. Fixes can themselves be wrong: at least 14.8%–24.4% of sampled fixes for post-release bugs in large operating-system code bases were incorrect and had an impact on end users. Developers and reviewers of those incorrect fixes usually did not have enough knowledge of the involved code, and 27% of the incorrect fixes were made by developers who had never touched the source code files associated with the fix.

## Example
```rust
bad:  const SQUARE: Shape = Shape { name: "square", orientations: 4 };
      fn turn(shape: &Shape, step: u32) -> u32 {
          if shape.name == "square" { return 0; } // workaround
          step % shape.orientations
      }
good: const SQUARE: Shape = Shape { name: "square", orientations: 1 };
      fn turn(shape: &Shape, step: u32) -> u32 { step % shape.orientations }
```

## Limits
When the code where the failure shows is itself the faulty code, the change there is the fix: the rule separates the fault from the failure, not one location from another. When the fault lies in code the change cannot alter, such as a dependency, the platform or an external service, a guard where the failure shows is the available correction; the finder names where the fault lies and stops. Concurrency failures such as data races and deadlocks, whose fixes were incorrect in 39% of cases in the same operating-system code bases, and failures traced across services lie outside this rule; the finder names such a failure and stops.

## Validator
Grep the hunk for a new conditional on one literal value, a new early return or default value, a new empty or swallowing error handler, or a comment naming a workaround, in a change whose message, test or linked issue reports a bug. Open the callers of the changed routine and the failing test or issue the change cites. Trace the wrong value or state the failure reports back to the code that first produces it, and compare that code with the lines the change alters. Validator question: **Does the change leave unchanged the code that first produces the wrong state and only add a guard where the failure shows, a case for the input that exposed it, or a suppression of the error raised there?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PRF-02`, severity major, `file`, `symbol`, `code` = the added guard, literal case or suppressing handler quoted verbatim from the diff, `fix` = the correction made at the code that first produces the wrong state, in the file's language, `rationale` = names the fault the change leaves in place and where it originates).

## Source
- DOI 10.1145/2001420.2001445, §6 Discussion, Observation 1 (fetched): "Ideally, when debugging, programmers are guided based on their understanding of the failure to a root cause. In practice, however, this does not always happen. Sometimes programmers discover that, through experimentation and manipulation of the program, they can stop the failure from occurring without actually fixing the fault. We observed several occurrences of this phenomenon in our study." … "the fault was due to an invalid configuration of the square figure's number of possible orientations. Quite a few participants did not correct this fault, but instead directly modified the rotation calculation code for the figures to bypass the failure." … "We can therefore make the following preliminary observation. Observation 1 -An automated debugging tool may help ensure developers correct faults instead of simply patching failures."; study setup, task description: "The rotation of a square block causes unusual behavior"; study setup, participants: "We selected participants from the set of graduate students".
- DOI 10.1145/2025113.2025121, abstract (fetched): "at least 14.8%–24.4% of sampled fixes for post-release bugs in these large OSes are incorrect and have made impacts to end users" … "39% of concurrency bug fixes are incorrect" … "Developers and reviewers for incorrect fixes usually do not have enough knowledge about the involved code. For example, 27% of the incorrect fixes are made by developers who have never touched the source code files associated with the fix."
- Caveat: the bypass comes from one debugging task given to graduate students, and the paper calls its whole study and its results preliminary ("we perform a preliminary study"; "although the results of our study are still preliminary"); the incorrect-fix rates measure fixes in operating-system code, not how many incorrect fixes patched a failure.

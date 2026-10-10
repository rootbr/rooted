---
title: Code with a release still pending in scope, one that flushes, writes or removes something, does not end the process through an exit that skips releases, so its deferred calls, finally blocks and destructors run before the process stops
rule_id: ERR-29
domain: errors
step: [implement, handle-errors]
applies_to: [universal]
triggers: ['\b(os[.](Exit|_exit|abort)|process[.](exit|abort)|System[.]exit|Runtime[.]getRuntime\(\)[.](exit|halt)|process::(exit|abort))\(', '\b\w*[Ll]og\w*[.](Fatal|Exit)\w*\(', '(^|[\s;{])(abort|exit)\(\s*\w*\s*\)\s*;']
scope: file
check_kind: semantic
severity_default: major
---

# Code with a release still pending in scope, one that flushes, writes or removes something, does not end the process through an exit that skips releases, so its deferred calls, finally blocks and destructors run before the process stops

## Thesis
Code that holds a release still pending in an open scope — a deferred call, a cleanup clause, a scoped-release block or the destructor of an owned value — whose work the end of the process does not do, such as flushing a buffer, completing a pending write, writing a trailer or removing a temporary file, ends the process only after that release has run. It returns an error or an exit status to the one place that exits, reached once the scope has closed; or it exits through an exit that unwinds the stack and so runs the cleanup clauses; or it calls an immediate exit, one that terminates the process without unwinding, only at a point where no such release is left to run. A logging call that reports a fatal error and then calls an immediate exit is itself an immediate exit.

## Rationale
An immediate exit ends the process without unwinding the stack: deferred calls are not run, cleanup clauses are not executed, resources opened in a scoped-release block are not closed, and no destructor on the current stack or on any other thread's stack runs. Every scope still open on the stack is skipped, the scopes of the routines that called the exiting routine among them. What a skipped release would have done is lost: a buffered writer's data is not flushed at program exit; a compressing writer whose close would flush the unwritten data and write the format's footer is left without them; and a temporary file, which is to be removed before the program terminates, is left behind when the cleanup clause that removes it does not execute. Some immediate exits also skip the runtime's own exit-time work: the process's standard I/O stream buffers are not flushed, or writes still pending to the standard output can be truncated and lost. An exit that unwinds, such as one that raises an exception, lets the cleanup clauses run, and a status returned to the program's main routine lets every scope close before the process stops, which is the clean shutdown an immediate exit forgoes. Termination closes every open file descriptor of the process, so a release whose only work is to close a descriptor loses nothing when it is skipped.

## Example
```python
bad:  with open(path, "w") as out:
          out.write(report)
          if not valid:
              os._exit(1)
good: with open(path, "w") as out:
          out.write(report)
          if not valid:
              sys.exit(1)
```

## Limits
An exit that unwinds the stack and a return from the program's main routine are outside the rule, and so is an immediate exit with no release pending in any scope open on its path. An immediate exit whose skipped releases only close descriptors, which termination closes anyway, loses nothing and is outside the rule. The immediate exit is the documented choice in a child process right after a fork, which the rule does not reach. An immediate exit taken on purpose because the program's state is damaged beyond repair, where running the pending releases would corrupt program resources, is outside the rule as well: terminating without running the cleanup clauses and finalizers is the documented choice there, and the rule holds where a clean shutdown is needed. A cleanup registered with the runtime's exit handlers rather than in a scope is outside the rule; whether a given exit runs those handlers depends on the exit, since a halt does not start the shutdown sequence that runs them and an immediate exit of some runtimes calls none of them. Whether a routine other than the entry point may stop the process at all, how it reports a failure to its caller, and the handling around the release itself are judged by their own rules.

## Validator
Grep the added lines for an immediate exit: a process or runtime exit or halt call, an abort, a bare exit call, and a logging call that logs a fatal error and then calls such an exit. For each hit, open the file and name the routine that holds it. List the releases pending on the path to the exit: a deferred call registered earlier in that routine, a cleanup clause or scoped-release block that encloses the exit, and a local value that owns a resource and runs a destructor; then find the routine's callers in the file and list the releases pending at each call. For each pending release, name its work: flushing a buffer or a writer, completing a pending write, writing a trailer, removing a temporary file or directory. Set aside a release whose only work is to close a descriptor; an exit that raises an exception the program can intercept, which unwinds; a return from the main routine; an immediate exit in a child process right after a fork; and an immediate exit that follows a check finding the program's state damaged beyond repair, where running the pending releases would corrupt program resources. Validator question: **Does an added exit that terminates the process without unwinding run while a release that flushes, writes or removes something — a deferred call, a cleanup clause, a scoped-release block or a destructor — is still pending in a scope open on its path?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: ERR-29`, severity major, `file`, `symbol`, `code` = the added exit, abort, halt or fatal-log line quoted verbatim from the diff, `fix` = the routine returning an error or an exit status to the one place that exits once every scope has closed, or exiting through the language's unwinding exit, or releasing explicitly before an exit left at a point with nothing pending, in the file's language, `rationale` = the pending release the exit skips and what it loses: the unflushed buffer, the unwritten trailer or pending write, the temporary file left behind).

---
title: A program whose standard output carries its primary output writes its error, warning and progress messages to standard error, not into standard output
rule_id: ERR-40
domain: errors
step: [implement, handle-errors]
applies_to: [universal]
triggers: ['(?i)(\bprintln!|\bprint!|\bfmt[.]Print(ln|f)?|\bSystem[.]out[.]print(ln|f)?|\bconsole[.](log|info)|^\s*print)\s*(\(\s*f?[`"''][^`"'']*\b(errors?|warn(ing)?|fail(ed|ure)?|could not|cannot|unable to|progress|processing)\b|(\(|\(.*[{,\s(])(err|error|e|ex|exc|exception)(\s*[)}]|[.](message|stack)\b|[.](getMessage|Error|to_string)\(\)))', '(?i)(\bsys[.]stdout[.]write\b|\bprocess[.]stdout[.]write\b|\bfmt[.]Fprint(ln|f)?\(\s*os[.]Stdout\b|\bio::stdout\(\)|\bSystem[.]out\b).*\b(errors?|warn(ing)?|fail(ed|ure)?|could not|cannot|unable to|progress)\b|\b(StreamHandler|SetOutput|basicConfig|ConsoleHandler|Logger|New\w*Handler|with_writer|createLogger|destination)\b.*\b(sys[.]stdout|os[.]Stdout|process[.]stdout|System[.]out|io::stdout|stdout)\b']
scope: file
check_kind: semantic
severity_default: minor
---

# A program whose standard output carries its primary output writes its error, warning and progress messages to standard error, not into standard output

## Thesis
When a program's standard output carries its primary output — the program's actual output, which a user may redirect to a file or pipe to another program — the program writes its error, warning and progress messages to standard error, directly or through a logger whose destination is standard error, and keeps standard output for the primary output alone.

## Rationale
On most operating systems a program can write to two output streams: standard output for its actual output, and standard error, which keeps errors and other messages separate from it. Kept apart, the output can be stored in a file or piped to another program while the errors are still shown to the user. An error message printed to standard output ends up in the file the user redirected the output to: the user does not see it on the screen, and the file holds it where only the data of a successful run belongs. The standard logging facilities of some languages send their console output to standard error by default, and one of them documents printing a library's events of warning severity and above there, when the application configures no logging, as the best default behaviour. Sending error messages to standard error also makes it easier to separate normal status from actual issues.

## Example
```typescript
bad:  for (const [i, path] of paths.entries()) {
          process.stdout.write(`progress: ${i + 1}/${paths.length}\n`);
          if (!fileExists(path)) console.log(`warning: skipping missing ${path}`);
          else console.log(`${path}: ${countLines(path)}`);
      }
good: for (const [i, path] of paths.entries()) {
          process.stderr.write(`progress: ${i + 1}/${paths.length}\n`);
          if (!fileExists(path)) console.error(`warning: skipping missing ${path}`);
          else console.log(`${path}: ${countLines(path)}`);
      }
```

## Limits
The condition that separates the cases is whether standard output carries the program's primary output, the one output standard output is kept for. A program whose standard output carries no primary output, only its stream of log events, is outside the rule; for a containerized application, writing to standard output and standard error is the easiest and most adopted logging method, and the container runtime handles and redirects whatever the application writes to either stream. A message that is itself the output the user ran the program to get is primary output and belongs on standard output. A logging call whose destination is standard error, the default console destination of the standard logger in some languages, already meets the rule; a logger given standard output as its destination, in a program whose standard output carries primary output, does not. Whether an event deserves a message at all, at which level and with what content are judged by their own rules.

## Validator
Grep the added lines for a write to standard output — a print or println call, a console log or info call, a write or formatted print to the standard output stream — whose text or argument reports an error, a failure, a warning or progress, and for a logger or log handler given standard output as its destination. Open the file and establish what the program's standard output carries: the program's actual output — results, data or a report a user may redirect to a file or pipe to another program — or nothing but a stream of log events, as in a service run in a container whose runtime captures both streams. Set aside a hit in a program whose standard output carries no primary output, a message that is itself the output the user ran the program to get, and a write that already goes to standard error; when the file gives no sign of what standard output carries, answer no. Validator question: **Does an added line write an error, warning or progress message to standard output, directly or through a logger whose destination is standard output, or give a logger standard output as its destination, in a program whose standard output carries its primary output?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: ERR-40`, severity minor, `file`, `symbol`, `code` = the added line that writes the error, warning or progress message to standard output, or that gives a logger standard output as its destination, quoted verbatim from the diff, `fix` = the same message written to standard error — through the standard-error print or write call, or a logger whose destination is standard error — with the primary output left on standard output, in the file's language, `rationale` = what the program's standard output carries and where the message ends up when a user redirects that output to a file or pipes it to another program).

## Source
- Rust standard library, `print!`, `println!`, `eprint!`, `eprintln!` (rust-lang/rust `library/std/src/macros.rs`) — "Use `println!` only for the primary output of your program. Use [`eprintln!`] instead to print error and progress messages." (fetched)
- rust-lang/book `src/ch12-06-writing-to-stderr-instead-of-stdout.md` — "Command line programs are expected to send error messages to the standard error stream so that we can still see error messages on the screen even if we redirect the standard output stream to a file."; "It's much more useful for error messages like this to be printed to standard error so that only data from a successful run ends up in the file." (fetched)
- rust-cli/book `src/tutorial/output.md` §Printing errors — "On most operating systems, a program can write to two output streams: `stdout` and `stderr`. `stdout` is for the program's actual output while `stderr` allows errors and other messages to be kept separate from `stdout`. That way, output can be stored to a file or piped to another program while errors are shown to the user." (fetched)
- Google Shell Style Guide §3.1 STDOUT vs STDERR (google/styleguide `shellguide.md`) — "All error messages should go to `STDERR`. This makes it easier to separate normal status from actual issues." (fetched)
- Go package `log` (golang/go `src/log/log.go`), package comment on the standard logger — "That logger writes to standard error" (fetched)
- CPython Logging HOWTO (python/cpython `Doc/howto/logging.rst`) — "they will set a destination of the console (``sys.stderr``)"; §Configuring Logging for a Library — "If the using application does not use logging, and library code makes logging calls, then (as described in the previous section) events of severity ``WARNING`` and greater will be printed to ``sys.stderr``. This is regarded as the best default behaviour." (fetched)
- Kubernetes, Logging Architecture (kubernetes/website `content/en/docs/concepts/cluster-administration/logging.md`) — "The easiest and most adopted logging method for containerized applications is writing to standard output and standard error streams."; "A container runtime handles and redirects any output generated to a containerized application's `stdout` and `stderr` streams." (fetched)
- Node.js `console` (nodejs/node `doc/api/console.md`) — `console.log`: "Prints to `stdout` with newline"; `console.error`: "Prints to `stderr` with newline"; "The `console.warn()` function is an alias for [`console.error()`][]." (fetched)
- Caveat: the Rust, command-line and shell sources state the rule for command-line programs and scripts; the container documentation describes how a containerized application's two streams are captured, not where a command-line program's messages go.

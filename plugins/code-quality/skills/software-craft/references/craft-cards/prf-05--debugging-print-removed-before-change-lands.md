---
title: A print, console or debug-print call added to diagnose a failure is removed before the change lands, while output meant for the program's user and diagnostics routed through the logging facility stay
rule_id: PRF-05
domain: performance
step: [implement, review]
applies_to: [universal]
triggers: ['\bdbg!\s*\(', '^\s*(pprint\s*[.]\s*)?(print|println|pprint)\s*\(', '\bconsole\s*[.]\s*(log|debug|trace|dir|table|info)\s*\(', '\bSystem\s*[.]\s*(out|err)\s*[.]\s*print(ln|f)?\s*\(', '\bfmt\s*[.]\s*(Print(ln|f)?\s*\(|Fprint(ln|f)?\s*\(\s*os\s*[.]\s*Std(out|err)\b)', '(?<![.\w])e?print(ln)?!\s*\(']
scope: file
check_kind: semantic
severity_default: minor
---

# A print, console or debug-print call added to diagnose a failure is removed before the change lands, while output meant for the program's user and diagnostics routed through the logging facility stay

## Thesis
An output call added to observe the program while hunting a failure (a print of a variable, a console write, a print-and-return debug macro, a print to standard output or standard error) is a debugging remnant, and it is removed before the change lands. Output that a command-line program produces as part of its interface to its user is not typically a problem and stays. Debug output meant to stay in production code is better done through the logging facility, where it can be enabled or disabled at will and by priority.

## Rationale
People often print while debugging an application and might forget to remove those prints afterward; such calls are usually intended for debugging and can remain in the codebase even in production code. A leftover print can lead to the accidental inclusion of sensitive information in logs, and clients cannot configure it the way they configure logging statements. In code designed to run in a browser, console messages are considered to be for debugging and therefore not suitable to ship to the client. A logger gives the control the print lacks: through it the same output can be enabled or disabled at will and by priority, and it avoids clogging the standard output log.

## Example
```typescript
bad:  function total(items: Item[]): number {
        console.log("items", items);
        return items.reduce((sum, item) => sum + item.price, 0);
      }
good: function total(items: Item[]): number {
        return items.reduce((sum, item) => sum + item.price, 0);
      }
```

## Limits
Print calls that produce output as part of a command-line program's interface are not typically a problem, and where the console is the channel that informs the program's user, a console call is not strictly debugging output. The documentation of one language's debug-print macro asks that uses of it not stay in version control for long periods, other than in tests and similar code. Diagnostic code kept in the source on purpose is the contested case, and the cases separate by what the output is: output added ad hoc to observe the program while hunting this failure is removed before the change lands, though a test may keep it; output that is the program's own output to its user stays; a diagnostic meant to last stays too, carried by the logging facility, where it can be enabled or disabled at will and by priority. Each side rests on documented text: the print rules say prints used for debugging should be omitted from production code and stripped before being pushed to production, while exempting command-line output and console output that informs the user; the debug-print macro's documentation sends debug output from production code to other facilities such as a logging macro. The rule reaches the output calls a change adds; which events a program logs, and at which level, lies outside it.

## Validator
Grep the hunk's added lines for output calls: a print or print-line call, a console write, a print-and-return debug macro, a formatted print to standard output or standard error. Open the file and decide what each call is: whether the call sits in a test (a test file, or a test function, test-only module or documentation test inside the file), whether the file is a command-line program's entry point or command handler whose printed text is the result or message the user asked for, and whether the file already routes diagnostics through a logging facility. Trace what the call prints: a raw variable, an object dump, a value labelled with its own name or a marker that shows where execution went is observation of internal state; a sentence addressed to the user, or the command's result, is interface output. Validator question: **Does the hunk add, outside a test, a print, console or debug-print call that dumps internal state to observe the program rather than writing a command-line program's output to its user or a diagnostic through the logging facility?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PRF-05`, severity minor, `file`, `symbol`, `code` = the added output call verbatim from the diff, `fix` = the routine with the call removed, or, for a diagnostic meant to stay, the same message through the file's logging facility at a debug level, in the file's language, `rationale` = names the call as a debugging remnant and what it prints, and that a lasting diagnostic goes through the logging facility where it can be enabled or disabled by level).

## Source
- rust-clippy `dbg_macro`, clippy_lints/src/dbg_macro.rs (fetched): "The `dbg!` macro is intended as a debugging tool. It should not be present in released software or committed to a version control system."; suggestion "remove the invocation before committing it to a version control system".
- rust-clippy `print_stdout` / `print_stderr`, clippy_lints/src/write/mod.rs (fetched): "The purpose of this lint is to catch debugging remnants." "People often print on *stdout* while debugging an application and might forget to remove those prints afterward."
- Ruff T201 / T203, crates/ruff_linter/src/rules/flake8_print/rules/print_call.rs (fetched): "`print` statements used for debugging should be omitted from production code. They can lead the accidental inclusion of sensitive information in logs, and are not configurable by clients, unlike `logging` statements." "`print` statements used to produce output as a part of a command-line interface program are not typically a problem."
- ESLint `no-console`, docs/src/rules/no-console.md (fetched): "Such messages are considered to be for debugging purposes and therefore not suitable to ship to the client. In general, calls using `console` should be stripped before being pushed to production." "If you're using Node.js, however, `console` is used to output information to the user and so is not strictly used for debugging purposes."
- Rust standard library, `std::dbg!` documentation, library/std/src/macros.rs (fetched): "you should avoid having uses of it in version control for long periods (other than in tests and similar). Debug output from production code is better done with other facilities such as the [`debug!`] macro from the [`log`] crate."
- PMD `SystemPrintln` (bestpractices), pmd-java/src/main/resources/category/java/bestpractices.xml (fetched): "References to System.(out|err).print are usually intended for debugging purposes and can remain in the codebase even in production code. By using a logger one can enable/disable this behaviour at will (and by priority) and avoid clogging the Standard out log."
- Error Prone `SystemOut`, core/src/main/java/com/google/errorprone/bugpatterns/SystemOut.java (fetched): "Production code should not print to standard out or standard error. Standard out and standard error should only be used for debugging."
- forbidigo, README.md (fetched): "the default pattern of `^(fmt\.Print.*|print|println)$` is used to eliminate debug statements."
- Caveat: these are tool rules and official documentation stating a convention, with no measurement of how often a remnant leaks data; Error Prone's rule has no command-line exemption; that exemption rests on Ruff and ESLint, and ESLint's console rule is written for code that runs in a browser.

---
title: A log message does not spell out the name of its enclosing routine, class or file as literal text, and leaves the source location to the logging facility or a language construct
rule_id: ERR-50
domain: errors
step: [implement, refactor]
applies_to: [universal]
triggers: ['(?:\b_*(?i:log|logger|logging|slog|console)[.]\w+|\b(?:debug|info|warn|error|trace)!)\(\s*f?[`"'']\s*\[?[A-Za-z_]\w*(?:(?:[.#]|::)\w+)?(?:\(\))?\]?\s*[:\]\-]', '(?:\b_*(?i:log|logger|logging|slog|console)[.]\w+|\b(?:debug|info|warn|error|trace)!)\([^`"'']*[`"''][^`"'']*\b[Ii]n\s+\w+(?:(?:[.#]|::)\w+)?\(\)']
scope: file
check_kind: mechanical
severity_default: minor
---

# A log message does not spell out the name of its enclosing routine, class or file as literal text, and leaves the source location to the logging facility or a language construct

## Thesis
A log statement takes the location of its record — the routine, class or file that encloses it — from the logging facility or from a language construct: the logger's name, set through a language construct such as the module's own name; the source file, line and function the facility records with each logging call; or a construct that yields the name of the current routine. Its message text holds no hand-typed copy of the enclosing routine's, class's or file's name, whether as a prefix such as `parseConfig:` or `[UserService]` or as a phrase such as `in load()`.

## Rationale
A location typed into a message has to be recorded and updated by hand, so a rename of the routine that misses the message leaves the record naming the old name. In four open-source server systems (Apache httpd, OpenSSH, PostgreSQL and Squid), 45% of 9,076 changes to logging code made after the fact — not as consistent updates alongside related code changes in the same patch — modified the static text of a message. In a random sample of 200 of these, 39% (±6.6% at 95% confidence) fixed out-of-date text that was inconsistent with the execution information it was meant to record and could mislead and confuse developers or users, and 76% of those fixes were related to function name changes. In one such case a function was renamed without updating the name its log message recorded; the developers were later confused by the out-of-date message while trying to resolve a failure, and a later patch existed only to fix the message. A language construct that holds the name of the function the code is executing in, together with the file and line, supplies the location without the developer recording or updating it, which avoids that inconsistent update in the first place. Logging facilities carry the same information outside the message text: a logger named after its module, from whose name alone it is obvious where an event was logged; a log request's target, which defaults to the module path of the request's location; and the source file, line and function or method a facility records for a logging call.

## Example
```typescript
bad:  class ConfigLoader {
        private readonly log = rootLogger;
        load(path: string): void { this.log.warn("[ConfigLoader] file not found in load()", { path }); }
      }
good: class ConfigLoader {
        private readonly log = rootLogger.child({ name: ConfigLoader.name });
        load(path: string): void { this.log.warn("file not found", { path }); }
      }
```

## Limits
The rule reaches the location written into a message: a name that is the event's subject rather than the statement's location, such as a routine or command that was called and failed or a handler or job being dispatched, follows the rule, and so does a location interpolated from a language construct. Drift in the rest of the text, such as an event and its description falling out of step, calls for natural-language analysis of the message against the code rather than a language construct, and lies outside this check. The message of an error value that is raised or returned lies outside this rule; an error string may identify its origin with a prefix naming the operation or package that generated it. A facility that infers the location from the call stack reports a logging wrapper's own file and line rather than its caller's, and an inferred class or method name may describe an earlier frame, so a project's own logging wrapper obtains its caller's location and passes it to the facility. Whether the output shows the recorded file, line and function is a handler or formatter option and lies outside this rule. A build step that renames functions and classes, as a minifier or obfuscator does, changes the name a construct reads from them at run time, so code built that way keeps those names in the build before it takes its location from such a construct.

## Validator
Grep the added lines for a log or console call whose message literal opens with an identifier-shaped token — a single word or a camelCase, PascalCase or snake_case name, or a `Type.method`, `Type#method` or `Type::method` pair, optionally in square brackets or followed by `()` — and then a colon, a closing bracket or a dash, or whose literal contains `in <name>()`. Open the file and read the routine, the class or type, and the file that enclose the statement. Compare the token with those names, ignoring case and separator style. Skip a token that names the event's subject rather than the statement's location: a routine or command that was called and failed, a handler or job being dispatched, a field or a value. Skip a location interpolated from a language construct, and the message of an error value that is raised or returned rather than logged. Validator question: **Does the literal text of a log message on an added line spell out the name of the routine, class or file that encloses the statement?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: ERR-50`, severity minor, `file`, `symbol`, `code` = the added log statement whose message literal names its enclosing routine, class or file, verbatim from the diff, `fix` = the same statement with the hand-typed location removed and the location supplied by a logger named through a language construct, by the source location the facility records, or by a construct that yields the current routine, in the file's language, `rationale` = which enclosing name the literal repeats, and that a rename which misses the message leaves the record naming the old location).

## Source
- DOI 10.1109/ICSE.2012.6227202 (ICSE 2012), study of logging code in four open-source server systems, §III.C, §IV Table V and §VII Table XI, Figures 7–8, Finding 10 — modifications counted are those "that are not consistent updates with other non-logging code changes"; text changes 4,057 of 9,076 (45%); "In some cases (39%), developers modified the out-of-date log messages that are inconsistent with the actual execution information, which could mislead and confuse the developers or users"; "Majority (76%) of them are related to function name changes"; "Later, they were confused with the out-of-date log message while trying to resolve a failure"; a macro "which holds the function name within which the code is currently executing", with `__FILE__` and `__LINE__` in Figure 8; "This eliminates the need for developers to manually record or update a location information, avoiding the inconsistent update problem at the first place"; "To detect other inconsistent updates (e.g., an event to log and its description), it would be beneficial to use natural language processing together with static source code analysis" (fetched)
- CPython Logging HOWTO §Advanced Logging Tutorial (python/cpython `Doc/howto/logging.rst`) — "logger names track the package/module hierarchy, and it's intuitively obvious where events are logged just from the logger name"; `logging` §LogRecord attributes (`Doc/library/logging.rst`) — `funcName` "Name of function containing the logging call.", `lineno` "Source line number where the logging call was issued (if available)." (fetched)
- Go `log/slog` (golang/go `src/log/slog`) — handler options for "displaying the source file and line of the log call"; `HandlerOptions.AddSource` "causes the handler to compute the source code position of the log statement"; `Source` holds `Function`, `File` and `Line`; §Wrapping output methods "This can produce incorrect source information for functions that wrap slog." and "A correct implementation of Infof will obtain the source location (pc) and pass it to NewRecord." (fetched)
- Rust `log` crate (rust-lang/log `src/lib.rs`) — "A target is a string which defaults to the module path of the location of the log request"; `Record::file` "The source file containing the message."; `Record::line` "The line containing the message." (fetched)
- OpenJDK `java.util.logging.LogRecord#getSourceMethodName` (openjdk/jdk) — "inferred automatically by the logging framework. In the latter case, the information may only be approximate and may in fact describe an earlier call on the stack frame." (fetched)
- Effective Go §Errors (golang/website `_content/doc/effective_go.html`) — "error strings should identify their origin, such as by having a prefix naming the operation or package that generated the error" (fetched)
- MDN `Function: name` §JavaScript compressors and minifiers (mdn/content `files/en-us/web/javascript/reference/global_objects/function/name/index.md`) — "Such transformations often change a function's name at build time."; "make sure your build pipeline doesn't change function names, or don't assume a function has a particular name." (fetched)
- Caveat: the measured drift comes from four server systems written in C and C++, whose authors draw no general conclusion for all software logging, and the location construct it shows is a C one; the card cites no tool rule, and the other languages rest on the mechanism and on their facilities' documentation, not on a measurement.

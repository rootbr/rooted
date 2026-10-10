---
title: A log call passes exactly the arguments its placeholders and key-value pairs require and never formats a lone varying string as its template
rule_id: ERR-47
domain: errors
step: [implement]
applies_to: [universal]
triggers: ['(?i)[.](debug|info|warn|warning|error|exception|critical|fatal|trace|log|printf)\w*\(\s*([\w.]+\s*,\s*)?["''][^"'']*(%[-+ #0]*\d*([.]\d+)?[a-z]|%\(\w+\)|\{\})', '\b(trace|debug|info|warn|error|log)!\(\s*([^"\s)]|"[^"]*\{)', '(?i)[.](debug|info|warn|warning|error|exception|critical|fatal|trace|log)(f|w|context|attrs)?\(\s*[a-z_][\w.]*\s*,', '(?i)\b\w*(printf|fatalf|panicf|debugf|infof|warnf|warningf|errorf|tracef|logf)\(\s*[a-z_][\w.]*\s*\)', '[.](Debug|Info|Warn|Error|Log)(Context|Attrs|w|S)?\(\s*([\w.]+\s*,\s*){0,2}"']
scope: hunk
check_kind: mechanical
severity_default: minor
---

# A log call passes exactly the arguments its placeholders and key-value pairs require and never formats a lone varying string as its template

## Thesis
A logging call that formats a template, whether its placeholders are printf-style verbs, %-placeholders or {} slots, receives arguments that match those placeholders in number and, where a placeholder names a type, in type. A logging call that takes alternating keys and values holds a string key or a ready-made key-value attribute in every key position and follows every key with its value. A string whose content varies and has no arguments after it reaches the record as an argument filling a placeholder of a constant template, not as the template of a call that formats it even then. A trailing exception that the facility shows separately from the message is not counted among the placeholder arguments.

## Rationale
Where a template is interpreted when the statement runs rather than validated by the compiler, it can carry errors that create the wrong string, and what the error does depends on the formatter. One formatter writes a description of the problem into the generated string: a wrong-typed, an extra and a missing argument each print as a marker such as `%!d(MISSING)`. Another ignores extra arguments and throws an exception when an argument is missing or incompatible with its placeholder. One key-value facility files an argument in a key position that is neither a string nor an attribute, and a final key left without a value, as a value under the key `!BADKEY`. One facility formats the record while emitting it and passes an exception raised there to its error handler, which in the setting its documentation advises for production swallows the exception. A template whose content varies is a variable rather than a literal, and one compiler requires the literal precisely so that it can check the arguments against the template; when a varying template, passed with no other arguments to a call that formats it even then, happens to contain a %, misformatting occurs. Checkers report too many and too few arguments, an argument of the wrong type, a key position holding neither a string nor an attribute, a final key without a value and a non-constant template passed with no other arguments, and one toolchain runs the format check, as one of a high-confidence subset of checks, by default while building a test binary and does not run the tests when the check finds a problem.

## Example
```rust
bad:  warn!("retry {} of {} for job {}", attempt, max);
      error!(reason);
good: warn!("retry {} of {} for job {}", attempt, max, job_id);
      error!("{}", reason);
```

## Limits
A facility that performs no formatting when no arguments are supplied takes a varying message passed alone without reading placeholders in it. A wrapper that receives a template and its arguments as parameters and forwards both to a formatting call is checked as a formatting function where it is called, so its forwarding call is not a varying template. Where the compiler requires the template to be a literal and checks the arguments against it, a mismatch or a varying template fails the build, so a finding there reports what the build also rejects. Whether the record is warranted, its level, its content, and whether a message is built before the level is checked are judged by their own rules, and so is a varying template that untrusted input controls.

## Validator
Grep the added lines for a logging call: a method or macro named for a level, a printf-like call whose name ends in f and that writes a log record or diagnostic output, and a call that takes alternating keys and values. For a literal template, count its placeholders by the template's own syntax, leaving out an escaped one such as a doubled %, and count the arguments after it, leaving out a trailing exception the facility shows separately from the message; where a placeholder names a type, compare it with the argument's type as the hunk declares it. For a key-value call, check that each key position holds a string key or a key-value attribute and that the last key has a value after it. For a template that is not a literal (a variable, a parameter, a concatenation or a call result) and has no arguments after it, check whether the call formats it even then: a printf-like call does, and a facility that skips formatting when no arguments follow does not. Validator question: **Does an added logging call pass more or fewer arguments than its template has placeholders, an argument of a type its placeholder rejects, a key position holding neither a string key nor an attribute, a final key without a value, or a varying string, with no arguments after it, as a template the call formats?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: ERR-47`, severity minor, `file`, `symbol`, `code` = the logging call quoted verbatim from the diff, `fix` = the same call with one argument per placeholder, each key followed by its value, or the varying string moved into a placeholder of a constant template, in the file's language, `rationale` = which placeholder lacks an argument, which argument has no placeholder or key, or which varying string is formatted as a template, and what the record shows instead).

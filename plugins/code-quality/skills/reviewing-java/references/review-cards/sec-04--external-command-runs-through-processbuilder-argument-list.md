---
title: An external command runs through ProcessBuilder or exec(String[]) with each argument as its own element, never through Runtime.exec(String) or a shell -c string
rule_id: SEC-04
domain: security
triggers: ['[.]exec\(', 'ProcessBuilder', 'Runtime[.]getRuntime\(', '"(/bin/)?(sh|bash|zsh)"', '"cmd([.]exe)?"|"powershell"', '"-c"']
scope: file
check_kind: semantic
severity_default: critical
---

# An external command runs through ProcessBuilder or exec(String[]) with each argument as its own element, never through Runtime.exec(String) or a shell -c string

## Thesis
A process started from Java names the program and each argument as separate array or list elements — `new ProcessBuilder("convert", input, "out.pdf")` — and no element that originates outside the code is part of a shell invocation's command string (`"sh", "-c", "convert " + input`). `Runtime.exec(String)` is not used: it splits the string on whitespace only, so it cannot carry an argument with a space, and a string assembled with untrusted data assembles the wrong command.

## Rationale
`ProcessBuilder` passes its list to the operating system as an argument vector; no shell parses it, so `;`, `|`, `&&`, backticks and redirections in an argument are just characters of that argument. `Runtime.exec(String)` breaks the string into tokens with a `StringTokenizer` on whitespace and runs the first token with the rest as arguments — no shell either, but an untrusted value with a space becomes extra arguments (`--output /etc/passwd`), and an attacker who controls the leading token controls the program. Invoking `sh -c` or `cmd /c` with an interpolated string hands the whole string to a shell, whose metacharacters chain arbitrary commands. Where an argument may begin with `-`, a `--` end-of-options marker before it stops option injection; a value that names the program to run comes from an allowlist in the code.

## Example
```java
bad:  Runtime.getRuntime().exec("sh -c 'convert " + userFile + " out.pdf'");
good: Process p = new ProcessBuilder("convert", "--", userFile, "out.pdf").start();
```

## Limits
Applies to a command line that contains a value from outside the code: a request, a message, a filename a user chose, a database field. A constant command with constant arguments is not flagged. A program name selected from a fixed map in the code is correct; a value validated against an allowlist regex with no metacharacters (`^[a-z0-9]{3,10}$`) before use as one argument is the correct second layer. Passing an untrusted value as a single argument to a program that itself interprets it (a `find -exec`, a `git` alias) is a defect of the invoked program's grammar and is out of this card's scope.

## Validator
On the triggered hunk find each `exec(String)`, each `ProcessBuilder` or `exec(String[])` whose elements include `sh`, `bash`, `cmd` or `powershell` with `-c` or `/c`, and each element built by concatenation. Open the file and trace each concatenated or non-constant element to its origin. Validator question: **does a value from outside the code reach a command as part of a string that a shell or a whitespace tokenizer will split, or as the program name?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: SEC-04`, severity critical, `file`, `symbol`, `code` = the `exec` or `ProcessBuilder` call quoted verbatim from the diff, `fix` = the argument-list form with the untrusted value as one element after `--`, `rationale` naming the shell or tokenizer split that lets the value become commands or options).

## Source
`java.lang.Runtime#exec(String)` Javadoc, Java SE 21 — "@deprecated This method is error-prone and should not be used, the corresponding method exec(String[]) or ProcessBuilder should be used instead. The command string is broken into tokens using only whitespace characters"; `#exec(String, String[], File)` — tokens from "a StringTokenizer created by the call new StringTokenizer(command)". OWASP OS Command Injection Defense Cheat Sheet — "In Java, use ProcessBuilder and the command must be separated from its arguments"; `Runtime.exec` "does NOT try to invoke the shell at any point"; the `--` end-of-options guideline. OWASP ASVS 5.0 requirement 1.2.5. SEI CERT IDS07-J; CWE-78.

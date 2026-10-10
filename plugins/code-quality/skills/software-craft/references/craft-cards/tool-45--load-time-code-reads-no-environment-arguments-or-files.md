---
title: Code that runs while a module loads reads no environment variable, argument or file
rule_id: TOOL-45
domain: tooling
step: [design, implement]
applies_to: [universal]
triggers: ['\bfunc\s+init\s*\(\s*\)|^\s*static\s*\{', '\b(?:os[.]Args|sys[.]argv|process[.]argv)\b', '\bprocess[.]env\b', '\bos[.](?:Getenv|LookupEnv|getenv|environ)\b', '\bSystem[.](?:getenv|getProperty)\s*\(', '\b(?:std::)?env::(?:vars?(?:_os)?\s*\(|args(?:_os)?\b)']
scope: file
check_kind: semantic
severity_default: minor
---

# Code that runs while a module loads reads no environment variable, argument or file

## Thesis
Code that runs while a module or package loads, other than the entry point's own startup code, leaves reading environment variables, the working directory, program arguments and files to a helper the entry point calls.

## Rationale
Load-time code is meant to be completely deterministic, regardless of program environment or invocation; a read of the environment, the working directory, program arguments or a file there likely belongs in a helper called as part of the entry point or elsewhere in the program's lifecycle, and a library intended for other programs takes special care to stay deterministic and to perform no load-time magic. The rule keeps a module that behaves the same whichever program loads it and whenever it is loaded.

## Example
```go
bad:  var dsn string
      func init() { dsn = os.Getenv("DB_URL") }
good: func main() {
          dsn := os.Getenv("DB_URL")
          run(dsn)
      }
```

## Limits
Load-time code that is unavoidable or desirable, such as a complex expression that cannot be a single assignment, a pluggable hook registration or a deterministic precomputation, stays when it reads no environment, arguments or files. The entry point's own startup code is its main routine or, for a script run as the program, the top-level code that runs it; an initialiser or static block in the entry point's own module is load-time code like any other. A read of a flag's value before the command line is parsed is a defect of its own, outside this rule. Where a routine outside load-time code may read the environment, and which values belong in configuration, lie outside this rule.

## Validator
Grep the hunk for a load-time initialiser, a static block, a top-level statement outside the entry point's startup code and an environment, argument or file read. For load-time code other than the entry point's own startup code (an initialiser, a static block, a top-level statement, a default argument value), trace whether it reads the environment, the working directory, program arguments or a file. Validator question: **Does the hunk add a read of the environment, working directory, program arguments or a file in load-time code other than the entry point's own startup code?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: TOOL-45`, severity minor, `file`, `symbol`, `code` = the load-time line that reads the environment, an argument or a file, `fix` = the read moved into a helper the entry point calls, with the value passed on as an argument or field, in the file's language, `rationale` = the load-time side effect the line creates).

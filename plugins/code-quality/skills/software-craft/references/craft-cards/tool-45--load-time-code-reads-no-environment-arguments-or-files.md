---
title: Code that runs while a module loads reads no environment variable, argument or file, and no value is computed from a flag before the command line is parsed
rule_id: TOOL-45
domain: tooling
step: [design, implement]
applies_to: [universal]
triggers: ['\bfunc\s+init\s*\(\s*\)|^\s*static\s*\{', '^\s*def\s+\w+\s*\([^)]*=\s*(?:FLAGS|flags|_?[A-Z_]+)[.]\w+', '\b(?:os[.]Args|sys[.]argv|process[.]argv)\b', '\bprocess[.]env\b', '\bos[.](?:Getenv|LookupEnv|getenv|environ)\b', '\bSystem[.](?:getenv|getProperty)\s*\(', '\b(?:std::)?env::(?:vars?(?:_os)?\s*\(|args(?:_os)?\b)']
scope: file
check_kind: semantic
severity_default: minor
---

# Code that runs while a module loads reads no environment variable, argument or file, and no value is computed from a flag before the command line is parsed

## Thesis
Code that runs while a module or package loads, other than the entry point's own startup code, leaves reading environment variables, the working directory, program arguments and files to a helper the entry point calls, and no code computes a value from a flag before the command line has been parsed.

## Rationale
Load-time code is meant to be completely deterministic, regardless of program environment or invocation; a read of the environment, the working directory, program arguments or a file there likely belongs in a helper called as part of the entry point or elsewhere in the program's lifecycle, and a library intended for other programs takes special care to stay deterministic and to perform no load-time magic. A default computed from a flag while a routine is being defined is computed before the command line has been parsed, so it carries the flag's unparsed default rather than the value the user set. The rule keeps a module that behaves the same whichever program loads it and whenever it is loaded.

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
Load-time code that is unavoidable or desirable, such as a complex expression that cannot be a single assignment, a pluggable hook registration or a deterministic precomputation, stays when it reads no environment, arguments or files. The entry point's own startup code is its main routine or, for a script run as the program, the top-level code that runs it; an initialiser or static block in the entry point's own module is load-time code like any other. A value read from a flag after the command line is parsed, inside a routine's body, is outside the rule. Where a routine outside load-time code may read the environment, and which values belong in configuration, lie outside this rule.

## Validator
Grep the hunk for a load-time initialiser, a static block, a top-level statement outside the entry point's startup code, a default argument value and an environment, argument or file read. For load-time code other than the entry point's own startup code (an initialiser, a static block, a top-level statement, a default argument value), trace whether it reads the environment, the working directory, program arguments or a file, or a flag's value before parsing. Validator question: **Does the hunk add a read of the environment, working directory, program arguments or a file in load-time code other than the entry point's own startup code, or a read of a flag's value before the command line is parsed?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: TOOL-45`, severity minor, `file`, `symbol`, `code` = the load-time line that reads the environment, an argument or a file, or the default computed from the flag, `fix` = the read moved into a helper the entry point calls after parsing, with the value passed on as an argument or field, in the file's language, `rationale` = the load-time side effect or the pre-parse read the line creates).

## Source
- uber-go/guide style.md, Avoid `init()` (fetched): "When `init()` is unavoidable or desirable, code should attempt to: 1. Be completely deterministic, regardless of program environment or invocation." "3. Avoid accessing or manipulating global or environment state, such as machine information, environment variables, working directory, program arguments/inputs, etc. 4. Avoid I/O, including both filesystem, network, and system calls. Code that cannot satisfy these requirements likely belongs as a helper to be called as part of `main()` (or elsewhere in a program's lifecycle), or be written as part of `main()` itself. In particular, libraries that are intended to be used by other programs should take special care to be completely deterministic and not perform 'init magic'." "some situations in which `init()` may be preferable or necessary might include: Complex expressions that cannot be represented as single assignments. Pluggable hooks, such as `database/sql` dialects, encoding type registries, etc. Optimizations to Google Cloud Functions and other forms of deterministic precomputation."
- google/styleguide gh-pages pyguide.md §2.12.4 Default Argument Values (fetched): "No:  def foo(a, b=_FOO.value):  # sys.argv has not yet been parsed..."
- Caveat: the load-time evidence is stated for one language's package initialiser and one language's default arguments, and the card applies it to code that runs when any module loads; no cited study measures the defect rate of load-time reads.

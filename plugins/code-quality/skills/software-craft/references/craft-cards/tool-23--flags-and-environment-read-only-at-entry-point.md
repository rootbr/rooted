---
title: Flags and environment variables are read only at the entry point or in one configuration module, and general-purpose code receives the values as explicit arguments
rule_id: TOOL-23
domain: tooling
step: [design, implement, refactor]
applies_to: [universal]
triggers: ['\bprocess[.]env\b', '\bos[.](?:Getenv|LookupEnv|getenv|environ)\b', '\bSystem[.](?:getenv|getProperty)\s*\(', '\b(?:std::)?env::(?:vars?(?:_os)?\s*\(|args(?:_os)?\b)', '\bflag[.](?:String|Int|Int64|Uint|Bool|Duration|Float64|Var|Func)\w*\s*\(', '\b(?:os[.]Args|sys[.]argv|process[.]argv)\b']
scope: callers
check_kind: semantic
severity_default: minor
---

# Flags and environment variables are read only at the entry point or in one configuration module, and general-purpose code receives the values as explicit arguments

## Thesis
A program defines its flags only in its entry point, and reads environment variables only there, in a helper in the entry point's own module that only the entry point calls, or in one configuration module the rest of the code reads from. General-purpose code is configured through explicit function arguments or structure fields rather than by reaching through to the command line or the environment, so importing it defines no flag.

## Rationale
An environment read littered through a project is another kind of global dependency, and it could lead to merge conflicts in a multi-user setup and to deployment issues in a multi-server setup. A flag defined inside a general-purpose module punches through to the command-line interface, so importing that module exports new flags as a side effect. The rule restores a module that is configured through its own interface, its arguments and fields, whichever program uses it.

## Example
```rust
bad:  pub fn connect() -> Conn {
          Conn::open(&std::env::var("DB_URL").unwrap())
      }
good: pub fn connect(url: &str) -> Conn { Conn::open(url) }
      fn main() {
          let url = std::env::var("DB_URL").expect("DB_URL is set");
          let conn = connect(&url);
      }
```

## Limits
The entry point, a helper in its own module that only it calls, and the one configuration module are where these reads belong, and flags kept as global variables in their own group at the top of the entry point are the documented form. In the extremely rare case that a general-purpose module must define a flag, the flag's name clearly indicates the module it configures; an exported global variable is a much less frequent alternative to arguments and fields, taken only under the strictest scrutiny. A project may exclude specific environment variables from the check through an allow-list, and a project that prefers reading the environment throughout its code may disable the check. The entry point's own startup code is its main routine or, for a script run as the program, the top-level code that runs it; whether code that runs while a module loads may read the environment at all is a separate rule's matter. Which values belong in configuration, how each is validated and which default it takes lie outside this rule.

## Validator
Grep the hunk for an environment read, a program-argument read, a system-property read and a flag definition. Open the file and decide whether the read sits in the program's entry point, in a helper in the entry point's own module that only the entry point calls, or in the project's one configuration module; a read inside a routine there, or in the entry point's own startup code, passes, and a flag defined at the entry point's top level passes. Elsewhere, trace whether the routine could take the value as an argument or field instead. Skip a variable on the project's documented allow-list. Validator question: **Does the hunk add a flag definition outside the entry point; an environment or program-argument read outside the entry point, a helper in its own module that only it calls, and the one configuration module?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: TOOL-23`, severity minor, `file`, `symbol`, `code` = the added line that defines the flag or reads the environment, a program argument or a file, `fix` = the routine taking the value as a parameter or configuration field and the entry point or configuration module reading it once and passing it on, in the file's language, `rationale` = the hidden global dependency the read creates).

## Source
- google/styleguide gh-pages go/decisions.md, Common libraries > Flags (fetched): "Flags must only be defined in `package main` or equivalent." "General-purpose packages should be configured using Go APIs, not by punching through to the command-line interface; don't let importing a library export new flags as a side effect. That is, prefer explicit function arguments or struct field assignment or much less frequently and under the strictest of scrutiny exported global variables. In the extremely rare case that it is necessary to break this rule, the flag name must clearly indicate the package that it configures." "If your flags are global variables, place them in their own `var` group, following the imports section."
- eslint/eslint docs/src/rules/no-process-env.md, and eslint-community/eslint-plugin-n docs/rules/no-process-env.md (fetched): "Littering it through out a project could lead to maintenance issues as it's another kind of global dependency. As such, it could lead to merge conflicts in a multi-user setup and deployment issues in a multi-server setup. Instead, one of the best practices is to define all those parameters in a single configuration/settings file which could be accessed throughout the project." Option allowedVariables: "this option allows you to exclude specific variables from triggering a linting error." When Not To Use It: "If you prefer to use `process.env` throughout your project to retrieve values from environment variables, then you can safely disable this rule."
- Caveat: the flag evidence is stated for one language's packages and the scattered-read evidence for one runtime's environment object, and the card applies both to every language; the core lint rule is deprecated since 7.0.0 in favour of the plugin rule, whose document carries the same opening paragraph and the allowedVariables option, while the When Not To Use It sentence is in the core document only.

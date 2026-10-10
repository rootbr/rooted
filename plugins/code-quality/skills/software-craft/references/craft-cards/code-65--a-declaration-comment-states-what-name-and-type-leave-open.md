---
title: A field, constant or parameter whose meaning or special values its name and type do not convey carries a comment that states them
rule_id: CODE-65
domain: code
step: [design, implement, document]
applies_to: [universal]
triggers: ['(?i)\b\w*(timeout|delay|interval|duration|ttl|deadline|period|size|length|limit|max|level|width|offset|rate|threshold|capacity|retries)\w*\??\s*(:|=[^=]|\s+\*?(\[\])?(u?int\d*|i\d+|u\d+|f\d+|float\d*|double|long|number|Duration|time[.](Duration|Time))\b)|\b(u?int\d*|i\d+|u\d+|f\d+|long|double|float|Duration|number)\s+\w*(timeout|delay|interval|duration|ttl|deadline|period|size|length|limit|max|level|width|offset|rate|threshold|capacity|retries)\w*\s*[;=,)]', '(?i)=\s*-1\b|\b(math[.]MaxInt\d*|Integer[.]MAX_VALUE|Long[.]MAX_VALUE|i(32|64)::MAX|u(32|64)::MAX|Number[.]MAX_SAFE_INTEGER|sys[.]maxsize)\b|\b\w+\??\s*:\s*(Option<|Optional\[|[\w.<>\[\]]+\s*\|\s*(null|undefined|None)\b)|@Nullable\b|\bOptional<[\w<>, ]+>\s+\w+\s*[;=,)]|\b\w+\?:\s*\w']
scope: file
check_kind: semantic
severity_default: suggestion
---

# A field, constant or parameter whose meaning or special values its name and type do not convey carries a comment that states them

## Thesis
A field, a constant or a parameter whose name and type leave its meaning open carries a comment that states what they leave open: what the value stands for; what a zero value, a null or another sentinel such as -1 signifies where that meaning is not obvious; or, for an error-prone or non-obvious field, parameter or option, why it is interesting. The comment sits above the declaration or at the end of its line, or in the doc comment of the type, the constant group or the routine that declares it. The rule reaches public and private declarations alike and flags only those whose meaning or purpose is not obvious from the name and type: a declaration whose name and type suffice passes without a comment, and a comment that merely restates the name does not state the meaning.

## Rationale
A routine's documentation is meant to give enough information to write a call without reading the routine's code, and editors display the description of a constructor parameter that also declares a field on constructor calls and on accesses of that field. Where the type and name suffice, no comment is needed, and commentary that restates the parameter names adds little useful information to the reader. Special values are among what the type and name may not clearly express; documented examples are -1 meaning that the number of table entries is not yet known, zero meaning the default heading level 3, and the zero value of a type when its meaning is not obvious. An error-prone parameter is documented by saying why it is interesting, for example that data not matching the format verbs of another argument makes the routine inline warnings into its output. Not every parameter must be enumerated in the documentation; the commentary asked for states something non-obvious or materially helpful to the reader.

## Example
```rust
bad:  pub struct Conn {
          pub read_timeout_ms: u64,
          pub max_idle: Option<usize>,
      }
good: pub struct Conn {
          /// Zero disables the timeout and waits for data indefinitely.
          pub read_timeout_ms: u64,
          /// None keeps every idle connection; Some(0) keeps none.
          pub max_idle: Option<usize>,
      }
```

## Limits
A meaning carried by the name or the type passes: where the type and name suffice no comment is needed, and a parameter description may be omitted when it is obvious from the routine's name and type signature. A zero value whose meaning is obvious needs no comment. An override or implementation needs no comment for a parameter whose meaning the overridden declaration documents; its documentation covers the specifics of the override, and in many cases the override needs no additional documentation. Conventions that comment every global variable, explain every exported field or document every public attribute, and a lint that requires documentation on every public item, are stricter than this rule and outside it: one such lint is allow by default because it can be noisy and not all projects may want to enforce everything to be documented, and the finding reaches only declarations whose meaning is open. A documented project convention that exempts a kind of declaration from documentation, such as private fields, rejects the finding for that kind. Outside the rule: local variables declared inside a routine body, the choice of a longer name or a more specific type instead of a comment, stating a valid range as a checked contract, and documents outside the source such as a configuration reference.

## Validator
Grep the added lines of the hunk for the declaration of a field, a constant or a parameter, in particular one named as a timeout, delay, interval, size, length, limit, maximum, level, width, offset, rate, threshold, capacity or retry count, one initialized to -1 or to an integer maximum, and one whose type admits null or absence; skip local variables declared inside a routine body. Open the file and collect what documents the declaration: a comment above it or at the end of its line, the doc comment of its type, its constant group or its routine, and, for an override or implementation, the documentation of the overridden declaration where the file holds it; an override or implementation whose overridden declaration lies outside the file passes. Say what the value stands for from the name and type alone; where you cannot, the meaning is open. Trace where the file reads the value: a comparison or branch that gives a zero, null, -1 or maximum value a behaviour of its own (no deadline, a default, no limit, not yet known) is a special value; a constraint the routine places on the argument that its type does not express, such as having to match another argument, makes the parameter error-prone. A meaning the name or the type already carries, or one the collected documentation states beyond restating the name, passes. Validator question: **Does an added field, constant or parameter have a meaning, a special value or an error-prone use that neither its name, its type nor any comment documenting it states?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: CODE-65`, severity suggestion, `file`, `symbol`, `code` = the added declaration line, verbatim from the diff, `fix` = the declaration with a comment in the language's documented doc-comment convention, at the declaration or in the doc comment of its type or routine, that states the missing meaning as the file's use of the value shows it, or names what the comment must state where the file does not read the value, in the file's language, `rationale` = what the name and type leave open and, where the file reads the value, the line that gives the value that meaning).

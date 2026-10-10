---
title: A routine that would take two or more boolean parameters takes an enum or a named options type instead, except a constructor whose booleans only initialise two-state properties
rule_id: CODE-35
domain: code
step: [design, implement, refactor]
applies_to: [universal]
triggers: ['\b(bool|boolean|Boolean)\s+\w+\s*,[^)]*\b(bool|boolean|Boolean)\s+\w+', ':\s*(bool|boolean|Boolean)\b[^)]*,[^)]*:\s*(bool|boolean|Boolean)\b', '\b\w+\s+bool\s*,[^)]*\b\w+\s+bool\b|(^|[(,])\s*\w+\s*,\s*\w+\s+bool\b', '\b(true|false|True|False)\b[^();]*,[^();]*\b(true|false|True|False)\b|^\s*(true|false|True|False)\s*,\s*$', '^\s*(mut\s+)?\w+\??\s*:\s*(bool|boolean|Boolean)\b[^,;]*,\s*$', '^\s*(final\s+)?((bool|boolean|Boolean)\s+\w+|\w+\s+bool)\s*,\s*$', '\w+\s*=\s*(true|false|True|False)\s*,\s*$|^\s*\w+\s*=\s*(true|false|True|False)\s*[,)]']
scope: hunk
check_kind: mechanical
severity_default: minor
---

# A routine that would take two or more boolean parameters takes an enum or a named options type instead, except a constructor whose booleans only initialise two-state properties

## Thesis
A routine that would otherwise take two or more boolean parameters takes instead an enum for each choice, whose values name what the choice means, or one options type that groups the flags that travel together, so that each argument at the call site says what it means. A constructor may keep boolean parameters that are truly two-state values and that it uses only to initialise boolean properties. A call that passes two or more boolean literals to a routine that keeps its boolean parameters names each parameter beside its literal, by a named argument or by a comment carrying the parameter name.

## Rationale
A bare true or false at a call site does not say what it conveys: the reader has to look up the parameter names in the declaration, or remember what each literal means and which position each flag belongs in, with no help from the type system. The calling code is what future readers meet more often than the declaration, so the rule optimises the call. A core type such as a boolean has many possible interpretations, and a deliberate type conveys the one intended: enum values named for their meaning make each argument self-describing. An options type lets the call site reference each option by name, reduces the argument count, which makes calls easier to read and write, and takes another option later without a change to the call sites. An enum lets a routine request exactly one choice from among many; where its input is instead the presence or absence of a set of flags, a flag set or an options type carries it. A boolean allows two states, and it is documented as the parameter type only where there will never be a need for more than two values, while an enum leaves room to add values later. A comment naming the parameter beside a literal spares the reader a look at the declaration, and a checker can match it against the declared parameter name; it is documented as the last resort, after an enum or an options type.

## Example
```rust
bad:  fn render(report: &Report, show_hidden: bool, draft: bool) { ... }
      render(&report, true, false);
      fn save(path: &Path,
          overwrite: bool,
          follow: bool) { ... }
good: enum Hidden { Show, Skip }
      enum Stage { Draft, Final }
      fn render(report: &Report, hidden: Hidden, stage: Stage) { ... }
      render(&report, Hidden::Show, Stage::Final);
```

## Limits
A constructor is outside the finding when each of its boolean parameters is truly a two-state value that it uses only to initialise a boolean property; a constructor that uses a boolean for anything else, or whose boolean could need a third value, is not. The rule counts two or more boolean parameters in one signature, so a routine with a single boolean parameter is outside it. An options type whose fields are booleans passes, since its flags travel together in one argument and each is set by name at the call site. A routine that implements or overrides a method declared elsewhere is judged at that declaration, not at each implementation: the tool checks of this rule inspect the declared method and exempt interface implementations and override definitions, and one of them also skips a routine declared with a foreign calling convention. A call is outside the finding when each of its boolean literals is named by a named argument or by a comment carrying the parameter name, or when it calls an equality assertion or a collection method such as append, insert, get or pop, which the tool check of boolean arguments in calls allows by default. One tool check of boolean parameters, which a project enables by choice, fires at its default bound only on a routine with more than three of them and lets the project set the bound; a bound of two or more that the project context documents is the tolerance that rejects a finding within it.

## Validator
Grep the hunk's added lines for a routine signature that declares two or more boolean parameters, counting a parameter list that spans several lines, its unchanged lines read from the hunk context, and for a call that passes two or more boolean literals as arguments, counting an argument list that spans several lines, its unchanged lines read from the hunk context. For a signature, count its boolean parameters, a parameter counting as boolean when its declared type is boolean or, with no declared type, its default value is a boolean literal, and read the routine in the hunk; set aside a constructor whose boolean parameters are each a truly two-state value only assigned to a boolean property, a routine the hunk marks as implementing or overriding a method declared elsewhere, a routine declared with a foreign calling convention, and a count within a bound the project context documents. For a call, count its boolean literal arguments, leaving out a literal that is an element of a collection or tuple, and set aside a call to an equality assertion or a collection method such as append, insert, get or pop; when two or more remain, check whether a named argument or a parameter-name comment names each of them; when the hunk also adds the called routine's signature and that signature is itself flagged, report the signature only. Validator question: **Does a signature that the hunk adds or changes, outside the set-aside cases, declare two or more boolean parameters, or does a call that the hunk adds or changes, outside the set-aside cases, pass two or more boolean literals of which at least one is named by no named argument or parameter-name comment?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: CODE-35`, severity minor, `file`, `symbol`, `code` = the added signature line or lines declaring the boolean parameters, or the added call passing the bare boolean literals, verbatim from the diff, `fix` = the signature taking an enum per choice with values named for their meaning, or one options type grouping the flags that travel together, with the call passing those named values, or, where the routine keeps its booleans, the call naming each literal by a named argument or a parameter-name comment, in the file's language, `rationale` = the number of boolean parameters or bare literals, that the call site shows only their values and positions, and the meaning, and the room for another value or option, that the named type gives).

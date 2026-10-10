---
title: A routine does not take a boolean parameter whose role is to choose which of two code paths it runs, while a boolean it stores or forwards as a value is allowed
rule_id: CODE-34
domain: code
step: [design, implement, refactor]
applies_to: [universal]
triggers: ['signal:boolean_argument', '\b(?:(?:bool|boolean|Boolean)\s+[a-z_]\w*\s*[,)]|[a-z_]\w*\??\s*:?\s*(?:bool|boolean)\s*[,)=])', '\bfunc\b[^{]*\b[a-z_]\w*\s+bool\s*[,)]']
scope: file
check_kind: semantic
severity_default: minor
---

# A routine does not take a boolean parameter whose role is to choose which of two code paths it runs, while a boolean it stores or forwards as a value is allowed

## Thesis
A choice between two paths through a routine is made by calling a separate routine for each path where the paths are distinct actions, or by passing a two-valued enumeration where the choice is a mode, rather than by a selector: a boolean parameter that the routine tests in a branch condition (an if, a conditional expression, a match on its value), so that the argument decides which of two paths the body takes. A boolean parameter that carries a two-state value is not a selector and stays: one the routine stores, as a binary option setting or a constructor parameter that only initialises a two-state property does, one it returns, one whose own value it turns into the text or number that represents it, as a routine that formats or converts the boolean does, and one it only passes on to another routine, which is judged at the routine that tests it. Outside the rule is a boolean parameter that an inherited or implemented declaration fixes.

## Rationale
A selector is a boolean used to decide which of two paths to take through the routine. However well the parameter is named, the code calling the routine shows only its value, true or false, so the maintainer of that code has to guess at the meaning or take extra time to look the routine up, and the calling code is encountered more often than the declaration. A caller that passes the flag controls the flow of the routine it calls, which makes the two control-coupled, and coupling among routines must be minimized for better maintainability. The boolean also limits the routine to two behaviours, which makes it difficult to extend. A separate routine per path states the action at the call site and suits choices that are distinct actions; a two-valued enumeration suits one parameter that selects a mode, is more suggestive at the call site than true or false, and makes it easier to add a third value later. A boolean that carries a value is documented as acceptable: a binary option setting takes a boolean argument rather than signalling its value by which option is called, because a caller that chooses options programmatically would otherwise have to change which calls it composes instead of an argument, and booleans are documented as worth considering for a constructor parameter that is truly a two-state value and simply initialises a boolean property.

## Example
```go
bad:  func render(o Order, compact bool) string {
          if compact { ... }
          ...
      }
      s := render(o, true)
good: func renderCompact(o Order) string { ... }
      func renderFull(o Order) string { ... }
      s := renderCompact(o)
```

## Limits
The rule is contested in general. One documented position replaces every bare boolean argument with a deliberate type, because a boolean has many possible interpretations and a custom type makes the options easier to expand later; the other accepts a boolean that carries a two-state value. What the routine does with the boolean, the role it plays, separates the cases. A boolean the routine tests to choose which path runs is the finding: one rule reports a public method whose boolean parameter's only use is the condition of an if statement or a conditional expression and asks for multiple methods instead, and another reports a boolean parameter used in an if condition as a control flag. A boolean the routine stores is accepted: binary option settings are documented as taking a boolean, and booleans are documented as worth considering for constructor parameters that are truly two-state values simply used to initialise boolean properties. A routine that turns a boolean into the text or number that represents it, as the standard formatting of a boolean as true or false does, branches on it in the shape both checks report, yet its callers pass a value computed at run time, so neither a split nor an enumeration applies, and it is not flagged. The position that replaces every boolean, a constructor's included, preferring a constructor called with two named variants to one called with two literals, reaches past this rule and is the project's choice. A comment naming the parameter beside a boolean literal at the call site is documented as improving readability, with a more self-documenting interface to be considered first; it changes no routine, so it leaves a selector in place. An override or implementation of an inherited declaration keeps the boolean that declaration fixes, and most checks that report boolean parameters skip it; the setter of a boolean property that only stores its value treats it as a value, and one check exempts every property setter. The number of boolean parameters is outside this rule: flags that travel together are documented as grouped into an options type, one guideline asks for enumerations where a member would otherwise take two or more booleans, and one linter's default reports a routine only above three boolean parameters.

## Validator
Read the added line the trigger matched: a routine signature that declares a boolean parameter, or a call that passes a boolean literal. For a call, find the definition of the called routine in the file; when the file does not define it, there is nothing to trace, so stop. Keep only a routine whose signature, or whose test of the boolean, is among the added lines. Skip a routine that overrides or implements an inherited declaration. For each remaining boolean parameter, trace its uses through the routine's body: a use as the condition of an if, a conditional expression or a match on its value, choosing which code runs, makes it a selector, unless the branches only produce the text or number that represents the boolean's own value, as formatting or converting a boolean does; a body that only assigns it to a field or property, returns it, or passes it as an argument to another routine treats it as a value. Validator question: **Does an added or changed routine take a boolean parameter that its body tests in a branch condition to choose which code runs?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: CODE-34`, severity minor, `file`, `symbol`, `code` = the added line that declares the boolean parameter or tests it, quoted verbatim from the diff, `fix` = the routine split into one routine per path, each named for its action, or the boolean replaced by a two-valued enumeration where the choice is a mode, with the call updated, in the file's language, `rationale` = the two paths the boolean selects between and that the call site shows only true or false).

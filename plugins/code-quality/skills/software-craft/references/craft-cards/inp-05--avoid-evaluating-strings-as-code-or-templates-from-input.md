---
title: Code avoids evaluating a string as code or building a template from untrusted input, and where there is no alternative the untrusted input it includes is sanitized, or for a template strictly validated, before use
rule_id: INP-05
domain: input
step: [implement]
applies_to: [universal]
triggers: ['(?<![.\w])eval(?:[?][.])?\(|[.]eval\(\s*[^)\s]|\(\s*0\s*,\s*eval\s*\)\s*\(', '(?<![.\w])exec\(', '\bnew\s+Function\(|(?<![.\w])Function\(\s*[\"''`a-zA-Z]|\bset(Timeout|Interval|Immediate)\(\s*[\"''`]', '\bSpelExpressionParser\b|[.]parseExpression\(|\bScriptEngineManager\b|\bGroovyShell\b|\bvm[.]runIn\w*Context\(', '\brender_template_string\(|[.]from_string\(|\btemplate[.]New\([^)]*\)[.]Parse\(|\bHandlebars[.]compile\(|\b_[.]template\(|\bVelocity[.]evaluate\(|\bnew\s+Template\(|[.]render_str\(']
scope: callers
check_kind: semantic
severity_default: major
---

# Code avoids evaluating a string as code or building a template from untrusted input, and where there is no alternative the untrusted input it includes is sanitized, or for a template strictly validated, before use

## Thesis
Code avoids the general evaluator and the other dynamic code execution features: a function built from a string, a string of code passed as a timer's callback, an expression-language evaluator and an embedded script engine. Code known when the program is written stays ordinary code, and a timer or callback receives a function value rather than a string. Templates are built from text their authors wrote, and an untrusted value reaches a template as the data it executes with. Behaviour selected at runtime goes through a fixed table from a validated key to a handler, and a string that holds data rather than code is a case for switching to a data format such as JSON and its parser. A literal-only evaluator does not take that parser's place for untrusted data: one runtime's documentation of its literal-only evaluator does not recommend calling it on untrusted data. Where there is no alternative, any user input included in evaluated code is sanitized before it runs, and any untrusted input included while a template is built is sanitized or strictly validated.

## Rationale
Some interfaces execute code provided as strings at runtime; when user-controlled data is included in the code string, an attacker can inject and execute arbitrary instructions within the application. The general evaluator executes the code it is passed with the privileges of the caller, so a string a malicious party can affect may end up running malicious code. A function built from a string and a string passed to a timer are implied evaluations, because a string of code is passed in to be interpreted. The documented practice is to avoid the function constructor and always pass a function to a timer. The security model of a contextually escaping template engine, as one standard library documents it, assumes that template authors are trusted and that the data passed at execution is not, and seeks to preserve its safety properties in the face of that untrusted data. The handler table is keyed by a validated value; a property lookup with unconstrained input is not safe either and may lead to object injection attacks. The documented literal-only evaluator is designed not to execute code, yet a relatively small input can lead to memory or stack exhaustion, crashing the process, and some inputs may cause excessive CPU consumption. The verification standard places avoiding dynamic code execution at its first level and template injection at its second.

## Example
```go
bad:  t := template.Must(template.New("greet").Parse("Hello, " + name))
      t.Execute(w, nil)
good: t := template.Must(template.New("greet").Parse("Hello, {{.}}"))
      t.Execute(w, name)
```

## Limits
Dynamic code execution might be useful in specific meta-programming use cases, and a project that is a rare one needing a function built from a string or a string passed to a timer keeps that use; the fallback of the Thesis then holds for every untrusted input the code includes. Evaluating a constant string admits no injected input, yet the evaluator is still replaced, because in most contexts it can be substituted for a better alternative approach. A template compiled from text its authors wrote, with untrusted values passed as data at execution, is the pattern the rule asks for. Deserializers that construct objects, the choice of parser for structured input and the escaping of output for its context lie outside this rule.

## Validator
Grep the hunk for a call to the general evaluator, a function constructor or timer given a string, an expression-language parser or script engine, and a template compiled from a string. For each hit, open the call and trace the string or template source back to where it is built: a literal, a concatenation, a format call, a parameter. Decide whether the string is code known when the program is written, where ordinary code or a function value would serve; holds data, where a data-format parser would serve; selects behaviour, where a fixed table keyed by a validated value would serve; or splices a value into a template, where a constant template given the value as data would serve. Where none would serve, trace whether input from outside the trust boundary reaches the call and whether it is sanitized first, or for a template sanitized or strictly validated. Validator question: **Does the hunk evaluate a string as code or build a template from untrusted input where ordinary code or a function value, a fixed handler table, a data-format parser or a constant template would do the job, or let untrusted input reach an evaluation call unsanitized or a template build neither sanitized nor strictly validated?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: INP-05`, severity major, `file`, `symbol`, `code` = the evaluation call or template construction and the line that builds its string, `fix` = the same behaviour through ordinary code or a function value, a fixed handler table keyed by a validated value, a data-format parser, or a constant template given the value as data, in the file's language, `rationale` = that the string runs as code with the caller's privileges, and which untrusted input can reach it).

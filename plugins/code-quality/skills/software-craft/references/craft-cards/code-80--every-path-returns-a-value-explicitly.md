---
title: If any return in a routine states a value, every path out of the routine states its value explicitly, including the path that reaches its end
rule_id: CODE-80
domain: code
step: [implement]
applies_to: [universal]
triggers: ['^\s*return(?:\s+(?:None|undefined))?\s*;?\s*(?://.*|#.*)?$', '^\s*(?:(?:export\s+)?(?:default\s+)?(?:async\s+)?function\b|(?:async\s+)?def\s+\w+|func\b|(?:(?:public|private|protected|static|async|override|get|set)\s+)*(?!(?:if|for|while|switch|catch|with|return|function)\b)[A-Za-z_$][\w$]*\s*(?:<[^>]*>)?\s*\([^()]*\)\s*(?::\s*[^={};]+)?\{\s*$)|=>\s*\{\s*$']
scope: file
check_kind: semantic
severity_default: minor
---

# If any return in a routine states a value, every path out of the routine states its value explicitly, including the path that reaches its end

## Thesis
When any return in a routine states a value, every return in it states one explicitly: a path with no other value to give returns the empty value by name, and the routine closes with an explicit return whenever its end is reachable. A routine that returns no value keeps every return bare.

## Rationale
A path that executes a bare return or runs off the routine's end still hands its caller a value that no return on that path states, such as the implicit empty value. The lack of an explicit return at the end of a routine that can return a non-empty value can cause confusion, and an explicit return of the empty value can make the code more readable by clarifying intent. When some paths of a routine return a value explicitly and others do not, the difference might be a typing mistake, especially in a large routine.

## Example
```go
bad:  func parse(s string) (n int, err error) {
          if s == "" { return 0, errEmpty }
          // ... thirty lines that set n and err ...
          return
      }
good: func parse(s string) (n int, err error) {
          if s == "" { return 0, errEmpty }
          // ... thirty lines that set n and err ...
          return n, err
      }
```

## Limits
A routine whose end cannot be reached needs no closing return. A routine whose only stated value is the empty value may instead keep every return bare, with no closing return. A constructor, which returns the instance it builds implicitly unless it returns another object explicitly, is outside the rule. Where a routine names its results in its signature, so that a bare return yields exactly those named values, the bare return is accepted in a routine of a handful of lines; once the routine is longer than that, the rule flags it beside a return that lists its values. Where the compiler rejects a value-returning routine whose end is reachable without a return, or the type checker does so under a declared return type that excludes the empty value, the end-of-routine half of the rule is already enforced.

## Validator
Grep the hunk for a bare return line, a return of the empty value and a routine header. Open the file at each routine the hunk adds or changes, skipping constructors; list its returns, marking each one that states a value; where the routine names its results in its signature and is a handful of lines long, treat its bare returns as stating those values; and trace whether control can reach the routine's end without a return. Validator question: **Does a routine with a return that states a value also have a path that leaves it without stating its value, either a bare return or a reachable end?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: CODE-80`, severity minor, `file`, `symbol`, `code` = the bare return or the routine's last statement, quoted verbatim from the diff, beside one return in the same routine that states a value, `fix` = the same path ending in a return that states its value, the empty value by name where the path has no other, or every return bare where the routine's only stated value is the empty value, in the file's language, `rationale` = names the implicit value that path yields and the return that states a value elsewhere in the routine).

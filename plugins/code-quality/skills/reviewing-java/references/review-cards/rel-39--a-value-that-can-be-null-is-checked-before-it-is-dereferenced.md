---
title: A value that can be null — a Map.get result, a request accessor, a nullable return — is checked or defaulted before it is dereferenced
rule_id: REL-39
domain: reliability
triggers: ['[.]get\([^)]*\)[.]', '[.]equals\(', 'getOrDefault\(', '@Nullable', 'Optional[.]ofNullable\(', 'findById\(', 'getHeader\(', 'getParameter\(', 'getAttribute\(']
scope: file
check_kind: semantic
severity_default: major
---

# A value that can be null — a Map.get result, a request accessor, a nullable return — is checked or defaulted before it is dereferenced

## Thesis
An expression that may evaluate to `null` — `map.get(key)`, a request header, parameter or attribute, a lookup that documents `null` for a miss — is null-checked or replaced by `getOrDefault`/`computeIfAbsent`/`Optional` before a method is invoked on it; `equals` is invoked on the operand known to be non-null.

## Rationale
`Map.get` "returns the value to which the specified key is mapped, or null if this map contains no mapping for the key"; a header or attribute that a client did not send is `null`; a repository miss is `null` or empty. A chained call on such a value throws `NullPointerException` on the first input that lacks the key, which is the input the tests did not include, and the exception names a line, not the missing datum. `variable.equals("constant")` is the same defect in another shape: the literal cannot be null, the variable can.

## Example
```java
bad:  String region = config.get(tenant).region();
      if (request.getHeader("X-Trace").equals("on")) trace();
good: String region = config.getOrDefault(tenant, Config.DEFAULT).region();
      if ("on".equals(request.getHeader("X-Trace"))) trace();
```

## Limits
A `get` on a map populated in the same method or class with the key in question, a lookup inside a `containsKey` guard, a key drawn from the map's own `keySet()`, and a value annotated or documented non-null are out of scope. A dereference whose `NullPointerException` is the intended fail-fast at a boundary, with a message (`requireNonNull(x, "x")`), is correct.

## Validator
On the triggered hunk find each dereference or `equals` receiver whose value comes from `Map.get`, a header/parameter/attribute accessor, or a lookup documented nullable. Open the file to check for a guard, a default, or a construction that guarantees presence. Validator question: **can this expression be null on some input, with the dereference throwing instead of a defined outcome?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: REL-39`, severity major, `file`, `symbol`, `code` = the dereference quoted verbatim from the diff, `fix` = a guard, `getOrDefault`, `Optional`, or the literal on the receiver side of `equals`, `rationale` naming the input on which the value is null).

## Source
`java.util.Map#get(Object)` Javadoc, Java SE 21 — "Returns the value to which the specified key is mapped, or null if this map contains no mapping for the key"; `#getOrDefault`, `#computeIfAbsent`. SpotBugs `NP_NULL_ON_SOME_PATH_FROM_RETURN_VALUE` — "The return value from a method is dereferenced without a null check, and the return value of that method is one that should generally be checked for null".

---
title: An operation returns its results as its return value rather than writing them into an argument, unless it exists to fill or change data the caller already owns
rule_id: API-18
domain: interface
step: [design, implement, refactor]
applies_to: [universal]
triggers: ['\b(out|output|outs|result|results|dest|dst)\w*\s*:\s*&mut\s', '\b(out|output|result|results|dest|dst)\w*\s+\*[A-Za-z_][\w.\[\]]*\s*[,)]', '\b[\w<>]+(\[\]|<.*>)\s+(out|output|result|results|holder)\w*\s*[,)]', '\bdef\s+\w+\(.*\b(out|output|result|results|acc|accumulator)\s*:\s*(list|dict|set|List|Dict|Set)\b', '\b(out|output|result|results)\s*:\s*(\w+\[\]|Array<|Map<|Set<|Record<)|\b(out|output)\w*\s*:\s*\{']
scope: file
check_kind: semantic
severity_default: minor
---

# An operation returns its results as its return value rather than writing them into an argument, unless it exists to fill or change data the caller already owns

## Thesis
An operation that produces one or more results hands them back as its return value: the result itself, or several results together in a tuple, a struct or a record written for that return. It does not deliver a result by writing it into a parameter whose role is output, such as a pointer, a mutable reference, an array or a holder object that the caller creates in advance only so that the operation can fill it. An operation meant to modify data the caller already owns keeps that data as a parameter: a buffer the caller re-uses across calls, or a value the operation reads and then changes in place.

## Rationale
An output parameter raises questions that the signature alone does not answer, for the caller and the implementer alike: whether the parameter is only written or also read, what happens to data already in it, whether that data is appended to or overwritten, whether the parameter may be absent where its type admits a null, and what it holds when the operation fails. Each call site also has to create the receiving object before the call. A returned result settles all of these: the operation creates it from scratch, a caller cannot read it after a failure that returns none, and the call fits inside a wider expression. That form is much harder to misuse, which reduces the likelihood of bugs and the developer's cognitive load, and return values improve readability over output parameters while often giving the same or better performance. An operation that can return several values at once has no need for a pointer to a result to simulate a reference parameter.

## Example
```typescript
bad:  function nextInt(text: string, pos: number, out: number[]): number { ... }
      const value: number[] = [];
      const next = nextInt(text, pos, value);
good: function nextInt(text: string, pos: number): { value: number; next: number } { ... }
      const { value, next } = nextInt(text, pos);
```

## Limits
Reading into a buffer the caller re-uses is one case of an operation meant to modify data the caller already owns, and it keeps the buffer as a parameter. Returning a value does not work for an in-out parameter, one whose data the operation reads and then changes; taking such a value as an input, changing it and returning it is a variant whose fit depends on how the operation is used and on whether the value moves cheaply. Returning a value takes from the caller the easy choice of how the result is created, such as the memory arena it is allocated in; the return form then needs that choice as an additional parameter, or the operation has to know it already. Returning a value can be less efficient where it leads to repeated allocation in a loop, and often it is as efficient or more, so an output parameter is kept for performance only where there is evidence that the difference matters. The rule judges the signature of an operation the change declares or changes; a call to an existing operation whose signature takes an output parameter is outside it. How many parameters an operation takes, and how it reports a failure, are outside the rule. The project context can reject the finding by stating a framework contract, or a measured cost of returning, that requires the output parameter.

## Validator
Grep the added lines for a parameter that looks like an output: a mutable reference or a pointer, an array, a collection or a holder object named out, output, result, dest or the like. Open the file and read each operation whose signature the hunk adds or changes and that takes such a parameter, whatever its name. Trace what the body does with the parameter: whether it only writes a result into it, or also reads the data already there. Read the call sites in the file: whether they create the argument empty, or as a zero value, just before the call and read the result from it afterwards. Skip a parameter the operation reads and then changes, a buffer the caller re-uses across calls, a parameter that carries the caller's choice of how the result is created, and an output parameter whose declaration comment or the project context cites a measured cost of returning. Validator question: **Does an operation the change declares or changes deliver a result by writing it into a parameter that the caller passes in only to receive it, where the operation could return that result as its value or as part of a compound value?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: API-18`, severity minor, `file`, `symbol`, `code` = the signature line that declares the output parameter, quoted verbatim from the diff, `fix` = the signature returning the result, or a tuple, struct or record of the results, in place of the output parameter, with one call site rewritten to use the returned value, in the file's language, `rationale` = the questions the output parameter leaves to every caller (whether it is read, what happens to data already in it, what it holds after a failure) and the receiving object each call site has to create in advance).

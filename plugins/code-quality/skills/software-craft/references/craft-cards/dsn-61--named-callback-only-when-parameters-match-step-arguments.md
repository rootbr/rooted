---
title: A named function is passed directly as a pipeline callback exactly when the step supplies no argument beyond those the function means to take
rule_id: DSN-61
domain: design
step: [implement]
applies_to: [functional]
triggers: ['[.](map|filter|forEach|some|every|find|findIndex|findLast|findLastIndex|flatMap|reduce|reduceRight)\(\s*[A-Za-z_$][\w$]*([.][A-Za-z_$][\w$]*)*\s*[,)]', '\blambda\s+(\w+(?:\s*,\s*\w+)*)\s*:\s*[\w.]+\(\s*\1\s*\)', '\|\s*(\w+)\s*\|\s*[\w:.]+\(\s*\1\s*\)', '\b(\w+)\s*->\s*[\w.]+\(\s*\1\s*\)']
scope: callers
check_kind: semantic
severity_default: major
---

# A named function is passed directly as a pipeline callback exactly when the step supplies no argument beyond those the function means to take

## Thesis
A function is passed by name to a pipeline step (a map, a filter, a for-each, a search or a fold) only when every argument the step supplies is one the function means to take, of the exact type the step passes; an optional parameter that the step never fills keeps its default and calls for no lambda. When the step supplies more than the function means to take, such as the element's index and the collection beside the element, the step receives a lambda that forwards only the intended arguments, the element and, for a fold, the accumulator with it. When every argument the step supplies is one the function means to take, the step receives the function itself rather than a lambda whose body only calls it with the lambda's own parameters.

## Rationale
A step that calls its callback with the element, the element's index and the collection passes all three to a function given by name, and a function whose optional second parameter is meant for something else receives the index there. A string-to-integer parser whose optional second parameter is the radix, mapped by reference over ['1', '2', '3'], returns [1, NaN, NaN] where [1, 2, 3] was expected. The mismatch can pass a type check and still produce a logical error, when the function's parameter accepts the same type the step passes. It can also arrive later: when a function mapped by reference over [1, 2, 3] gains a second, optional parameter in a minor version, the result changes from [2, 3, 4] to [2, 3, 5] with the call site untouched, because the index that the step passes as each call's second argument lands in the new parameter. A lambda that forwards only the element calls the function with the expected number of arguments, and the result stays [2, 3, 4]. Where the step passes exactly the arguments the function takes, with their exact types, a lambda whose body only calls that function with its own parameters adds code and a level of indirection for no benefit.

## Example
```python
bad:  def describe(item): ...
      labels = list(map(lambda item: describe(item), items))
good: def describe(item): ...
      labels = list(map(describe, items))
```

## Limits
The two directions split on what the step supplies. A step that passes the element together with its index and the collection is given a forwarding lambda, with three exceptions passed by name: a built-in function that takes only one argument and needs no receiver, such as a number conversion or a truthiness test; a type-predicate callback that takes only the element, passed to a filter, every, find or find-last step, where wrapping can fail to preserve the narrowing of the result's type; and a function declared beside the call to be that step's callback, when the stability of both call signatures is assured. One lint rule reports that locally declared callback too, so a tolerance stated in the project's context settles that case. A step that passes only arguments the function means to take, leaving any optional parameter at its default, makes the forwarding lambda replaceable in all but a few cases, and three cases keep the lambda: a body that computes the callee, such as one that calls the result of a call, since the replacement would evaluate that expression eagerly where the lambda was defined rather than each time the lambda is called; a lambda that callers invoke with arguments by name, since the function's parameter names may differ from the lambda's; and a call where the argument's type gets adjusted on its way to the function, which the redundancy check ignores.

## Validator
Grep the hunk for a pipeline step whose callback argument is a bare or dotted function name, and for a lambda or closure whose body is a single call of a function on exactly the lambda's own parameters. For a bare name, open the file at the step's receiver and establish the arguments the step passes to its callback, the element alone, the accumulator with the element for a fold, or either of these with the index and the collection; then open the named function's definition, local or imported, and check whether the step passes any argument beyond those the function means to take, one that lands in a parameter, optional ones included, meant for something else, or one the function drops and a parameter added later would receive. An optional parameter that the step never fills keeps its default and is no mismatch. Treat as matching a built-in function that takes only one argument and needs no receiver, a type-predicate callback that takes only the element, passed to a filter, every, find or find-last step, and a function declared beside the call as that step's callback where the project's context admits it. For a forwarding lambda, confirm that every argument the step passes is one the function means to take, with its type unadjusted, that the body computes nothing per call beyond the forwarded call, and that no caller passes the lambda's arguments by name. Validator question: **Does the hunk pass a function by name to a step that supplies an argument beyond those the function means to take, or wrap in a pure forwarding lambda a function to which the step supplies only arguments it means to take?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: DSN-61`, severity major, `file`, `symbol`, `code` = the step call with its callback argument, quoted verbatim from the diff, `fix` = the step call with a lambda that forwards only the intended arguments, the element and, for a fold, the accumulator with it, or with the function passed by name in place of the forwarding lambda, in the file's language, `rationale` = the arguments the step supplies set against the function's parameter list, naming the parameter that receives the index or collection, or the lambda that only forwards).

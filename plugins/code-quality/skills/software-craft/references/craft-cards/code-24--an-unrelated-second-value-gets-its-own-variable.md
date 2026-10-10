---
title: A name in a routine holds one quantity, and a second, unrelated value gets its own variable rather than being assigned or re-declared under the earlier name
rule_id: CODE-24
domain: code
step: [implement, refactor]
applies_to: [universal]
triggers: ['(?<![\w.])(?:(?i:temp|tmp|aux|scratch)\w*|result|res|value|val|data|ret|buf|out)\s*(:\s*[^=]+)?:?=(?!=)', 'signal:long_routine']
scope: file
check_kind: semantic
severity_default: minor
---

# A name in a routine holds one quantity, and a second, unrelated value gets its own variable rather than being assigned or re-declared under the earlier name

## Thesis
Within a routine, each variable serves one purpose. When the routine needs a second value unrelated to the one a variable already holds, it declares a new variable with its own name for that value, and the earlier variable is neither assigned the second value nor re-declared to hold it. A rebinding that holds the earlier value transformed or converted, even into another type, or a value derived from the earlier one that replaces it once the original value is no longer needed, serves the same purpose and may keep the name.

## Rationale
The cost of a recycled variable is to readability and safety. Re-declaring a name can hurt readability, especially in large code bases, because it is easy to lose track of the active binding at any place in the code, and re-declaring a name by accident to hold an unrelated value may indicate a mistake. A buffer recycled for a second use can carry data left from the first, and leftover data in a recycled buffer is a common source of security bugs. A new variable for the second value gives each name one meaning at every line where it is read. Keeping the name for a transformed or converted form of the same quantity spares the author from coming up with a second name for one thing, such as one name for a string of spaces and another for their count; once a derived value replaces the original, the code after it no longer has access to the original, which is good style when no later operation should legitimately use it.

## Example
```python
bad:  temp = read_lines(path)
      temp = [s.strip() for s in temp]
      save(temp)
      temp = count_errors(log)
      alert(temp)
good: lines = read_lines(path)
      lines = [s.strip() for s in lines]
      save(lines)
      error_count = count_errors(log)
      alert(error_count)
```

## Limits
The rule is contested on the related rebinding, a change of type included. One position flags a change of a variable's type inside a routine, whether or not the new value is related to the old one, and opt-in lints flag even a re-declaration that reuses the original value, because a name may then be bound to different things depending on position in the code; the other holds rebinding a name to a transformed value of the same quantity idiomatic even when the type changes, as when a string of spaces is rebound as the number of those spaces. A type change alone does not separate the cases: a related rebinding may change type, and an unrelated one may keep it, as an integer loop index reused for a second loop does. The separating condition is whether the new value is closely related to the old one: the earlier value transformed or converted, or a value derived from it that replaces it once the original value is no longer needed, is idiomatic, and a rebinding to an unrelated value is the one that may indicate a mistake. Reusing one error variable for the result of each call in a long chain of conditional checks is a common, pragmatic idiom, and the rule leaves it alone. A buffer may be reused as scratch space as an optimization, to avoid reallocating it on every iteration; its scope is then preferably kept as narrow as possible, and care is taken that no later use reads data left by an earlier one. Keeping the name for a related value is a permission, not a duty: a new name remains available wherever it reads more clearly. A scratch-buffer reuse the project documents as a performance measure rejects the finding. A reassigned parameter, a loop-control variable changed inside its loop, a declaration in a nested block that hides a name of an enclosing scope, and the choice of the new variable's name are outside this rule.

## Validator
Grep the hunk for an added assignment or declaration to a name the routine may already hold: a generic temporary or result name (`temp`, `tmp`, `result`, `value`, `data`, `buf`) assigned again, a name re-declared in the same scope, or a declaration that re-assigns an existing variable alongside a new one. Open the file and, for each candidate, find the routine's earlier binding of the same name; read both values and the uses of the name after each. Drop the candidate when the new value is the earlier value transformed or converted (into any type), a value derived from the earlier one that replaces it once the original is no longer needed, an error result re-assigned by the next call in a chain of checks, or a scratch buffer reused within a narrow scope with no leftover data read; drop a reassigned parameter, a loop-control variable changed inside its loop, and a nested-block declaration that hides an outer name. Validator question: **Is a variable in the routine, after holding one value, assigned or re-declared to hold a value unrelated to it, neither derived from the earlier value nor the next error result in a chain of checks, so that one name stands for two unrelated quantities at different lines?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: CODE-24`, severity minor, `file`, `symbol`, `code` = the added assignment or declaration that rebinds the name to the unrelated value, verbatim from the diff, `fix` = the second value bound to a new variable with its own name and the later uses of that value renamed with it, in the file's language, `rationale` = the two unrelated quantities the one name holds and the lines where each is bound).

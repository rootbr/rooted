---
title: A routine performs one cohesive job and does not bundle operations whose results and effects share no data
rule_id: CODE-33
domain: code
step: [design, implement, refactor]
applies_to: [universal]
triggers: ['signal:long_routine', '\b(def|fn|func|function)\s+(\([^)]*\)\s*)?\w*(_and_|[a-z]And[A-Z])\w*\s*[(<\[]', '^\s*((\w+|<[^>]*>)(<[^>]*>)?(\[\])?\s+)+[a-z]\w*And[A-Z]\w*\s*[(<]|^\s*[a-z]\w*And[A-Z]\w*\s*\([^)]*\)\s*(:\s*[^={;]+)?\{|\b(const|let|var)\s+[a-z]\w*And[A-Z]\w*\s*(:[^=]*)?=\s*(async\b\s*)?(\(|function\b|\w+\s*=>)']
scope: file
check_kind: semantic
severity_default: minor
---

# A routine performs one cohesive job and does not bundle operations whose results and effects share no data

## Thesis
Each routine is responsible for one task, and the operations in its body share the data that binds them into that task. Operations whose results and effects share no data, such as computing a total and clearing a cache, sit in separate routines, each responsible for its own task.

## Rationale
As a routine gains responsibilities, it becomes more difficult to reason about, harder to test and harder to change without breaking one of its parts, and the documented remedy is to separate the work so that each routine is responsible for one task. In a program's entry point, the number of separate tasks handled increases as the program grows, and the documented practice is to split out its separate concerns when it starts getting large. Cohesion is the strength of association of the elements within a module, and the usual goal of decomposition is to place different functionalities and responsibilities in different components. The functional cohesion of a procedure is measured on its data slices: data tokens that lie on more than one slice are the glue that binds separate components together, and super-glue tokens lie on every slice, so a procedure whose slices share no token has nothing binding its parts. In a large-scale study of the refactorings in 156 open-source projects, scored with eight program comprehension metrics, re-organizing code with the goal of creating more cohesive components, methods among them, had a positive impact on readability, especially on the coherence between identifiers and documentation comments. Length and doing too much are two definitions that practice treats as one: in a study of the 125 bugs that developers traced to code smells in 11 web application projects, 45 bugs were caused by long methods, in 31 methods, and the study found many factors besides length affecting code quality.

## Example
```typescript
bad:  function totalAndClear(items: Item[], cache: Map<string, number>): number {
        cache.clear();
        return items.reduce((sum, item) => sum + item.price, 0);
      }
good: function total(items: Item[]): number {
        return items.reduce((sum, item) => sum + item.price, 0);
      }
      // the code that invalidates the cache calls cache.clear() itself
```

## Limits
A routine whose body only calls other routines in sequence toward one purpose and handles their errors is outside the finding; the documented shape is a program's entry point whose responsibilities are limited to calling the argument parsing, setting up any other configuration, calling the routine that runs the program's logic and handling the error that routine returns, so that it handles running the program while the called routines hold the logic. Parsing a program's arguments may stay in its entry point while that logic is small, and moves to other routines or types when it starts getting complicated. Length alone is not the finding: a conceptually simple routine that is one long but simple case analysis, doing small things for many cases, may be longer, and a long routine whose operations all share data passes. Operations that share data with the rest of the routine are outside the finding; whether they form one task or several, and how far to decompose them into smaller routines, the rule does not settle. A routine the project context documents as deliberately combining tasks is the tolerance that rejects the finding.

## Validator
Where a hunk carries the long_routine signal, start from the routine it measures, and grep the added lines for a routine signature, especially a name that joins two verbs or nouns with and. Open the file and take each routine whose signature the hunk adds or renames, or whose body the hunk changes. List its results and effects: each value it returns, and each object, store or external peer it changes, counting writes to several fields of one object as one effect on that object. For each result or effect, trace back through the body the statements and the data that produce it, counting a statement that guards, orders, sets up or records an operation (acquiring and releasing a lock, opening and closing a resource, checking a precondition, logging the operation) as part of that operation's trace. Group the results and effects whose traces share a variable, a parameter, a field or an intermediate value. Count the object a method runs on, and an object that both traces reach through one parameter or variable and use only by reading or writing its fields, as shared only through a field that both traces read or write, directly or through a routine they call, whether the code names that object or leaves it implicit. Set aside a routine whose body only calls other routines in sequence toward one purpose and handles their errors, argument parsing that stays small in a program's entry point, and a combined routine the project context documents; a name joined with and is a prompt, not the finding, since a routine that loads a value and saves it shares that value. Validator question: **Does the routine hold two or more groups of operations whose results and effects share no variable, parameter, field or intermediate value?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: CODE-33`, severity minor, `file`, `symbol`, `code` = the first added line of each group of operations that the diff adds to and that shares no data with the others, with the routine's signature line when the diff adds it, quoted verbatim from the diff, `fix` = the groups separated, in the file's language: a group of several statements moved to its own routine named for its result or effect, and a group that is a single call left to the callers that need it, `rationale` = the result or effect each group produces, the absence of any data the groups share, and the reasoning, testing or change that bundling them makes harder).

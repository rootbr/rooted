---
title: A change that alters a routine leaves no comment on or inside the routine stating what it no longer does, returns, raises or requires
rule_id: CODE-71
domain: code
step: [implement, refactor, document, review]
applies_to: [universal]
triggers: ['\b(def|fn|func|function)\s+(\([^)]*\)\s*)?\w+\s*[(<\[]|^\s*(public|protected|private|internal|static|export)\b[^=;]*\(|^\s*(@\w+\s+)*((public|protected|private|default|abstract|final|synchronized|native|static)\s+)*(<[^>]*>\s+)?(?!(if|for|while|switch|select|elif|return|throw|raise|new|else|yield|await|case|assert|goto|go|defer|match|typeof|delete|and|or|not|in|is|lambda)\b)[A-Za-z_$][\w$.]*(<[^;=()]*>)?(\[\])*\s+[A-Za-z_$][\w$]*\s*\([^;=]*(\)\s*(throws\s+[\w$., ]+)?(\{.*|;)?|[,(])\s*$|^\s*((public|private|protected|static|async|override|readonly|abstract|get|set)\s+)*(?!(if|for|while|switch|catch|with|return|function|typeof|await|new|delete|void|yield|case|else|super|this|synchronized|match)\b)[A-Za-z_$][\w$]*\??\s*(<[^>]*>)?\s*\([^()]*\)\s*(:\s*[^=;{]+?\s*(\{.*|;)|\{.*)\s*$|\b(const|let|var)\s+[A-Za-z_$][\w$]*\s*(:[^=]+)?=\s*(async\s*)?(\([^()]*\)|[A-Za-z_$][\w$]*)\s*(:\s*[^=]+)?=>|^\s+(?!(Some|Ok|Err|None|Box|Vec|Rc|Arc|String|Self)\b)[A-Z]\w*\s*\([^()]*\)\s*(\([^()]*\)|[\w.*\[\]]+)?\s*$', '\b(return|raise|throw|yield)\b|\bpanic!?\s*\(', '@(param|returns?|throws)\b|^\s*:(param|returns?|raises)\b']
scope: base-compare
check_kind: semantic
severity_default: minor
---

# A change that alters a routine leaves no comment on or inside the routine stating what it no longer does, returns, raises or requires

## Thesis
When a change alters what a routine does, returns, raises or requires (its behaviour, its parameters or return type, the errors it reports, the preconditions it states), or finishes the work a TODO or FIXME describes, the same change updates or removes the comments that describe the old code: the routine's doc comment and its tags, the examples in that doc comment, the implementation comments inside the routine, and the TODO or FIXME. After the change, no comment on or inside a changed routine names a parameter, a return value, an error, a precondition, a behaviour or a pending task that the code no longer has.

## Rationale
Keeping comments up to date when the code changes is a priority. A documented parameter that is not in the signature can mislead the routine's users and may mark an omission when refactoring, and nothing is worse than a doc example that does not work because the code changed after the documentation was written. Class and method comments change with a minority of code changes: across 1.3 billion AST-level changes in the complete histories of 1,500 systems, 13% to 20% of code changes triggered a change to a class or method comment. The other changes are not thereby inconsistent, but each is a place where an inconsistency can enter. Tools check the structural part of this drift: they match each documented parameter against the signature and each documented checked exception against what the routine throws, and where the language runs doc examples as tests, an example that no longer works fails. These checks compare names and run examples; a sentence of prose that the change made false is outside what they compare, and is left to the reader of the change, for whom the comments that were there before the change are worth reading: a TODO that can now be removed, a comment advising against the change. The rule rests on what a false comment costs its reader, not on a defect rate: inconsistent updates of a function and its comment are not necessarily correlated with more bugs, and the change found risky was one that suddenly updated a function and its comment inconsistently where they are usually updated consistently, or the reverse.

## Example
```java
bad:  /**
       * Returns the order with this id, or null when none has it.
       * @param timeout seconds to wait for the store
       */
      public Optional<Order> find(String id) { return lookup(id); }
good: /** Returns the order with this id, or an empty Optional when none has it. */
      public Optional<Order> find(String id) { return lookup(id); }
```

## Limits
A change that leaves true everything a comment states needs no comment edit: renaming a local, or restructuring a body whose documented behaviour holds. A documented error that the routine's body does not raise itself is not stale when a callee raises it or when the routine is abstract and its implementations may raise it, and a documented parameter is not stale when the routine receives it through a variadic or keyword-collecting parameter. A still-true comment that could be worded better, a TODO or FIXME the change adds, and documents outside the source (a README, a design document, a generated reference site) are outside the rule. The rule covers the comments on and inside each routine the change alters; a comment elsewhere that describes that routine, such as the doc comment of its enclosing type, a comment at a call site or a comment in another file, is beyond what the check reads. Whether the fix rewrites a stale comment or deletes it is the author's choice; either meets the rule once no comment states what the code no longer does.

## Validator
Read the hunk's added and removed lines and list each routine whose behaviour the change alters: a parameter added, removed, renamed or retyped; a changed return type or returned value; an error raised, thrown, returned or panicked on that was not before, or one no longer raised; a changed check on the routine's inputs; code that does the work a TODO or FIXME in the routine describes. For each, open the base version of the file with `git show <base_sha>:<path>` and read the routine's doc comment with its tags and examples, the implementation comments inside the routine and every TODO or FIXME in it; then read the same comments at HEAD. Compare each statement those comments make at HEAD (a parameter name, what is returned and when, which error and when, a precondition, a described behaviour, a pending task) with the code at HEAD. Skip a documented error that a callee raises or that an abstract routine's implementations may raise, a documented parameter that a variadic or keyword-collecting parameter receives, and a comment whose statement the change leaves true. Validator question: **Does a comment on or inside a routine this diff changes state, at HEAD, a parameter, return, error, precondition, behaviour or pending task that the changed code no longer has?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: CODE-71`, severity minor, `file`, `symbol`, `code` = the changed code line quoted verbatim from the diff, followed by the comment line or tag it contradicts as it stands at HEAD, `fix` = that comment rewritten, in the file's language and its documented doc-comment convention, to state what the code now does, or removed when the change leaves it nothing true to state, `rationale` = what the comment states, what the changed code does instead, and the reader or caller it can mislead).

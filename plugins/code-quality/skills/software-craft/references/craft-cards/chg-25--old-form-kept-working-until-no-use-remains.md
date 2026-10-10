---
title: A change that renames, moves, re-signs or removes an element without updating every use of it keeps the old form working beside the new one until no use of the old form remains
rule_id: CHG-25
domain: change
step: [design, implement, refactor, review]
applies_to: [universal]
triggers: ['signal:added_file', '(?i)\b(?:moved|renamed)\s+(?:to|from)\b', '\b(def|fn|function|class|struct|interface|trait|enum|type)\s+\w+|\bfunc\s+(\([^)]*\)\s*)?\w+\s*[(\[]|\b(public|protected|private|internal|static)\s+[\w<>\[\],.? ]+\s+\w+\s*\(']
scope: callers
check_kind: semantic
severity_default: major
---

# A change that renames, moves, re-signs or removes an element without updating every use of it keeps the old form working beside the new one until no use of the old form remains

## Thesis
When a change renames, moves, re-signs or removes an element and leaves some of its uses to later changes, the old form stays declared and working beside the new one, as an alias, as a re-export that keeps the element available from its old location, or as a forwarding definition, a wrapper that keeps one form's signature and calls the other, so that the whole system keeps working after each change and the remaining uses move in separate changes. The old form is removed only once no use of it remains, counting the uses in code that an automated rewrite did not process, such as code built only under another build configuration or platform, macro bodies, documentation examples and code generated at build time.

## Rationale
In a large codebase it may be impractical or infeasible to move a declaration and update all its clients in a single change; the change then happens incrementally, the declaration added at its new place without deleting the original, and the clients updated over time. Keeping the element available from both the old and the new location gives a transition period in which references to the old and the new form can be mixed and interoperate. Changes that depend on each other need a way to keep the whole system working after each one is submitted; otherwise the build can break for every other developer between the submissions, for a few minutes, or longer when a later submission goes wrong. The same holds when a codebase moves to the next language edition: code made compatible with both the current and the next edition at once is easier to migrate incrementally, and when the automated migration does not completely succeed or requires manual help, the work can iterate on the current edition before the switch. An automated rewrite does not reach every use: one compiler-driven migration tool works with a single build configuration at a time, cannot fix procedural macros at all, cannot update documentation tests and cannot apply to code that a build script generates. Tool-driven cleanup is not complete either: no analysis is known that ensures complete automation, because determining reachability in a sound and complete manner is infeasible, so some manual intervention by the developer follows the tool's cleanup. Removing the old form therefore rests on an impact analysis that identifies all the systems and software products the change affects.

## Example
```java
bad:  class Store { void saveAll(List<Item> items) { ... } }  // renamed from save
      store.save(items);  // a use left for a later change: the build breaks
good: class Store {
          void saveAll(List<Item> items) { ... }
          void save(List<Item> items) { saveAll(items); }
      }
      store.save(items);
```

## Limits
A change that moves or renames the declaration and updates every use in the same change meets the rule, since no use of the old form remains after it. An old form that must be retained indefinitely for backward compatibility, as for an element whose callers lie outside the codebase, falls outside the rule; how long it stays and how its removal is announced is deprecation policy, which the rule does not reach. Where a language offers no alias for some kind of element, there may be no way to make code that refers to the old name interoperate with code that refers to the new one; a change that deletes such an element's old form while a use remains still breaks that use and is flagged like any other, and a change that moves it together with every use meets the rule. The rule does not set the size of each change in the sequence.

## Validator
Grep the hunk for a deleted or renamed declaration, a changed parameter list, a deleted alias, re-export or forwarding definition, and a note that something moved or was renamed. For each old name or old signature, open the callers: search the whole codebase for it, including files compiled only under another build configuration, platform condition or feature switch, macro bodies, the templates and inputs of code generators, and documentation examples. Trace whether this change updates each use found, and whether the element's callers lie outside the codebase. Validator question: **Does the change delete or alter the old form of an element while a use that only the old form accepts remains in the codebase outside the change?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: CHG-25`, severity major, `file`, `symbol`, `code` = the deleted, renamed or re-signed declaration quoted verbatim from the diff, `fix` = the old form restored beside the new one as an alias, a re-export or a forwarding definition with the old signature that calls the new form, in the file's language, or, for an element the language cannot alias, the remaining uses updated in the same change, `rationale` = names one remaining use of the old form by file and line and the build configuration, macro, generator or documentation example that holds it).

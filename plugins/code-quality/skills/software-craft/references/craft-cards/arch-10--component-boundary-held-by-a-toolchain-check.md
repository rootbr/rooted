---
title: A boundary a change declares between components, such as a part kept for one component's own use or a dependency one component may not take on another, is held by a check the toolchain or the project's dependency checker runs, not by a directory name, a naming convention or a sentence in a document alone
rule_id: ARCH-10
domain: architecture
step: [design, implement, review]
applies_to: [universal]
triggers: ['(?i)^\s*(package|namespace|import|from|use|using)\b.*?[./:\\](_?internals?|impl|private|_[a-z]\w*)\b', '(?i)["''][^"'']*/(_?internals?|impl|private)/[^"'']*["'']', '(?i)\b(must|may|should|shall)\s+not\s+(import|depend\s+on|reference|call\s+into)\b']
scope: callers
check_kind: semantic
severity_default: minor
---

# A boundary a change declares between components, such as a part kept for one component's own use or a dependency one component may not take on another, is held by a check the toolchain or the project's dependency checker runs, not by a directory name, a naming convention or a sentence in a document alone

## Thesis
Where a change declares a boundary between components (a package, directory or module kept for one component's own use, or a rule that one component may not depend on another) and the project's toolchain or dependency checker offers a checked form at that scope, the change declares the boundary in that checked form. The checked forms are component-scoped visibility, a module system's export list, build-target visibility, a package export map, and a contract in the dependency checker the project runs whose violation fails the build or a test. A directory name or naming mark the toolchain ignores, such as an internal sub-package whose types are public or a leading-underscore module, leaves every reference across the boundary legal, and an invariant stated only in prose leaves it legal too. A check at compile time and a check at test time both hold the boundary.

## Rationale
Where visibility has two levels, local to one package and global, a type that a neighbouring package of the same component uses has to be global, and as soon as a symbol is exported it can be imported from anywhere else. A directory by itself only arranges files: there is no relationship among the packages in it, and it restricts no import. A boundary held by convention relies on a rigorous and consistent process of code review, a discipline that often breaks down as projects grow, use cases become more complex and developers come and go. In a longitudinal case study of a commercial system, detecting where the code departed from its intended architecture was insufficient to prompt the small, informal team to remove the departures. In a longitudinal study of 19 bi-weekly versions of each of four open-source systems, the number of architectural violations kept growing in the long term despite all effort, and some violations appeared to recur after being eliminated. A checked form turns a crossing into a failure of the build or of a test: the build tool rejects the use of an internal package as not allowed, a target fails to build when it violates the visibility of one of its dependencies, language access control prevents use of a public member outside its module unless its package is exported, and an architecture verification throws an exception on any detected violation.

## Example
```typescript
bad:  // billing/internal/tariffs.ts; "shipping must not import this"; CI runs the import lint, which ignores folder names
      export function tariff(zone: string): number { ... }
      import { tariff } from "../billing/internal/tariffs";  // shipping/quote.ts
good: // billing/tariffs.ts; a lint rule set to error in CI admits importers under billing/ only
      /** @package */
      export function tariff(zone: string): number { ... }
      import { quote } from "../billing";  // shipping/quote.ts, the component's public entry
```

## Limits
The condition that separates the cases is whether the project's toolchain offers a checked form at the component scope or the project already runs a dependency checker. Where the language's own documentation states that nothing in it makes it possible to enforce data hiding, that it is all based upon convention, and that documentation, a public-names list and a single leading underscore mark the internal interfaces, and neither the build toolchain nor a dependency checker the project runs offers a checked form at the component scope, the naming convention is the declaration and the rule does not apply. A checked form counts without being airtight: a package export map is not a strong encapsulation, since a require of an absolute sub-path still loads the file, and a static checker for a very dynamic language is bound to have limitations: one such checker avoids false positives at any cost by accepting a small number of false negatives. Where a compile-time module system works well, it keeps its place, since it checks at compile time where an architecture test checks at test time; the test-time check serves where the compiler is not of much use to prevent the illegal references. The rule governs references across a boundary between components, whether units of build, release or deployment or modules a project declares inside one such unit, and leaves the visibility of one member inside a component to the class and routine level.

## Validator
Grep the hunk for a package or namespace segment named internal, impl or private, an import of an underscore-prefixed module, an import path running through such a directory, and prose stating that one component must not import, depend on, reference or call into another. For each hit, open the component's build file, module descriptor, package manifest and the configuration of any dependency checker the build or CI runs, and open the callers that reference the component across the declared boundary. Trace whether the boundary appears in a form the toolchain or the checker enforces: component-scoped visibility, a module export list, build-target visibility, a package export map, or a checker contract whose violation fails the build or a test. Skip the hit where neither the language nor the build toolchain offers a checked form at the component scope and the project runs no dependency checker. Validator question: **Does the change declare a boundary between components that the project's toolchain or dependency checker could check, while holding it only by a directory name, a naming mark or prose?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: ARCH-10`, severity minor, `file`, `symbol`, `code` = the boundary's declaration or the import that crosses it, verbatim from the diff, `fix` = the same boundary in the toolchain's checked form, such as a visibility modifier, an export-list entry, a build visibility attribute, an export map entry or a checker contract, in the file's language, `rationale` = names the reference the naming mark leaves legal and the check that would reject it).

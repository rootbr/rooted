---
title: Once no use of a migration's old alias, forwarder or replaced implementation remains in code its author can change, the old path is deleted, unless it belongs to a published interface that a compatibility promise keeps
rule_id: CHG-30
domain: change
step: [refactor, review]
applies_to: [universal]
triggers: ['@[Dd]eprecated\b|#\[deprecated\b|//\s*Deprecated:|@warnings[.]deprecated\(|//\s*go:fix\s+inline|@InlineMe\b|^\s*(?:export\s+)?type\s+\w+\s*=\s*[\w.]+\s*;?\s*$|^\s*pub\s+use\s+[\w:]+(?:\s+as\s+\w+)?\s*;', '(?i)\b(?:legacy|compat|shim)']
scope: callers
check_kind: semantic
severity_default: minor
---

# Once no use of a migration's old alias, forwarder or replaced implementation remains in code its author can change, the old path is deleted, unless it belongs to a published interface that a compatibility promise keeps

## Thesis
Once no use of a migration's old path (an alias, a forwarding routine, or a replaced implementation, such as the one a flag used to select) remains in code the migrating author can change, the old path is deleted rather than left in place, provided it belongs to no published interface whose outside callers a compatibility promise protects.

## Rationale
A move that is impractical or infeasible to make atomically in a large codebase adds the new declaration without deleting the original, so that clients can be updated incrementally, over time. Once all callers refer to the new declaration, the original may be safely deleted; source-level inlining tools have eliminated millions of calls to deprecated routines in one monorepo, and when a batch of rewrites goes well the old code is no longer in use and can be safely deleted. Deprecated code should eventually be removed. In practice the cleanup is not always performed: often developers do not clean up code related to obsolete flags, causing technical debt to accumulate. Code kept for such flags can affect development across multiple dimensions: unnecessary control-flow paths can adversely affect reliability, effort must be spent to maintain test coverage of the unnecessary paths, the dead code and its tests affect build and testing time, and coding complexity can become quite high as programmers reason about control paths related to the obsolete flags. Removing all code artifacts of a flag whose goal is accomplished improves code hygiene and avoids that debt. The deletion can be generated from the program's syntax trees: one cleanup tool generated cleanup changes for 1381 flags (17% of all flags), 65% of which landed without any changes and over 85% of which compiled and passed tests.

## Example
```java
bad:  static int total(Order order) { return order.amount(); }
      @Deprecated  // forwarder kept after its last caller moved to total
      static int legacyTotal(Order order) { return total(order); }
      static int due(Order order) { return total(order); }
good: static int total(Order order) { return order.amount(); }
      static int due(Order order) { return total(order); }
```

## Limits
The cases separate on whether the old path belongs to a published interface whose callers outside the codebase a compatibility promise protects. Such a path may have to be retained indefinitely for backward compatibility: a standard library's compatibility promise prevents ever removing an old name, which stays as a deprecated forwarder that simply calls its replacement, and any removal of it is a matter for the project's deprecation policy, which this rule does not reach. An old path whose every caller is in code the migrating author can change is deleted once no use of it remains: helpers left unused by a rewrite may be safely deleted unless they are part of a stable published API, and deprecated code should eventually be removed. While callers remain, the old and new paths coexist by design, because clients are updated incrementally; the rule applies only once the last use is gone. A few calls may remain where an automated rewrite would be unsafe, such as where a local declaration shadows a name; while they remain, the old path still has a use and the rule does not apply.

The finder reaches the card through an added line that declares, marks or names the old path: a deprecation marker, an alias or re-export declaration, or a legacy, compat or shim name; a change that only migrates the last caller and adds none of those is not dispatched by the diff alone.

## Validator
Grep the hunk for deprecation markers, alias and re-export declarations, inline-forwarding directives, names containing legacy, compat or shim, and deleted lines that called an old name the diff replaces with a new one. For each old path the diff adds, touches or leaves behind after migrating its callers, open its callers at scope: search the repository for uses of its name outside its own declaration and its own tests. Trace whether the old path is part of a published interface: exported from a package or library that consumers outside the repository depend on under a stated compatibility or versioning promise. Validator question: **Does an old alias, forwarder or replaced implementation that the diff adds, touches or leaves behind after migrating its callers have no remaining use in the repository outside its own declaration and tests, and belong to no published interface under a compatibility promise?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: CHG-30`, severity minor, `file`, `symbol`, `code` = the old path's declaration line quoted verbatim from the diff, or the diff's last migrated call when the declaration lies outside the hunk, `fix` = the old declaration and its tests deleted with the replacement left as the only path, in the file's language, `rationale` = names the old path and its replacement, states that no use of the old path remains in the repository and that no published interface under a compatibility promise keeps it).

## Source
- golang/website `_content/blog/alias-names.md`, gradual code repair (fetched): "In large codebases it may be unpractical or infeasible to make such a change atomically [...] we add its declaration in a new package without deleting the original declaration in the old package. This way, clients can be updated incrementally, over time. Once all callers refer to `F` in the new package, the original declaration of `F` may be safely deleted (unless it must be retained indefinitely, for backward compatibility)."
- golang/website `_content/blog/gofix.md`, newexpr fixer (fetched): "all of your `newInt`-like helper functions will have become unused and may be safely deleted (assuming they aren’t part of a stable published API). A few calls may remain where it would be unsafe to suggest a fix, such as when the name `new` is locally shadowed by another declaration."
- golang/website `_content/blog/inliner.md`, renaming ioutil.ReadFile (fetched): "Go’s compatibility promise prevents us from ever removing the old name"; "Deprecated: As of Go 1.16, this function simply calls [os.ReadFile]"; "To date, these tools have eliminated millions of calls to deprecated functions in Google’s code base. [...] robots quietly prepare, test, and submit batches of code changes across a monorepo of billions of lines of code. If all goes well, by the morning the old code is no longer in use and can be safely deleted."
- SonarSource rule S1133 'Deprecated code should be removed' (fetched): "Deprecated code should eventually be removed."
- DOI 10.1145/3377813.3381350, abstract and §2 (fetched, uber/piranha report.pdf): "It analyzes the ASTs of the program to generate appropriate refactorings which are packaged into a diff"; "When the goal of a feature flag is accomplished [...] all code artifacts related to the flag need to be removed from the source code. This ensures improved code hygiene and avoids technical debt"; "In practice, this simple post cleanup process is not always performed. Oftentimes, developers do not cleanup code related to obsolete flags, causing accumulation of technical debt"; "The presence of code related to these unnecessary flags can affect software development across multiple dimensions"; "the overall reliability of the application can be adversely affected in the presence of unnecessary control flow paths"; "effort must be spent to maintain test coverage of these unnecessary paths. Third, the presence of dead code and tests impacts the overall build and testing time"; "coding complexity can become quite high as the programmer has to reason about the control paths related to these obsolete flags"; "generated code cleanup diffs for 1381 flags (17% of total flags), (b) 65% of the diffs landed without any changes, (c) over 85% of the generated diffs compile and pass tests successfully".
- Caveat: the cost and cleanup figures concern code kept for stale feature flags; the deletion condition and its compatibility exception come from moved, renamed or deprecated declarations.

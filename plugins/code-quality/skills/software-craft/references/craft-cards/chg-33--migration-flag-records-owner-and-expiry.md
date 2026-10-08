---
title: A flag added to switch between an old and a new path records its owner and its expiry where it is declared or registered
rule_id: CHG-33
domain: change
step: [design, implement, review]
applies_to: [universal]
triggers: ['(?i)\bfeature[_-]?(?:flag|gate|toggle|switch)', '(?i)\btoggle', '(?i)\b(?:define|register|new|add)_?(?:flag|toggle|feature|gate)\w*\s*\(', '(?i)\b(?:use|enable)_?new[A-Z_]\w*', '(?i)\bflags?[.](?:bool|string|int|define)\w*\(']
scope: hunk
check_kind: mechanical
severity_default: suggestion
---

# A flag added to switch between an old and a new path records its owner and its expiry where it is declared or registered

## Thesis
A flag that a change adds to switch between an old and a new path records, where it is declared or registered, who owns it and when it expires — as a date or a release — so that cleanup can find the flag and its owner once it is stale. A flag meant to stay as a permanent setting is outside the rule.

## Rationale
When the goal of a flag is accomplished, the flag needs to be disabled and all code artifacts related to it need to be removed from the source code, yet developers often do not clean up the code of obsolete flags, and technical debt accumulates. Feature gates are not intended as long-term APIs: individual gates are expected to be deprecated and removed after their feature becomes generally available or is dropped. The code of an unnecessary flag can adversely affect the application's reliability through unnecessary control-flow paths, requires effort to maintain test coverage of those paths, and, as dead code and tests, impacts build and testing time. Once flags go uncleaned for a long period, determining ownership of the stale flags can become problematic, and an orphaned flag is one whose owner has left the organization and whose final roll-out status is unclear. An expiry date that the owner defines when the flag is created makes its intent clear, which enables automated cleanup tools to generate diffs without confusing developers, and the owner of each flag is to be tracked precisely. A comment in the code that declares the flag, naming the release in which it is to be removed, signals when removal is planned. In one deployment of automated flag cleanup, a developer introduces a flag by creating an entry in a flag management system and entering the flag's attributes there, and a pipeline queries that system for the list of stale flags and invokes the cleanup tool with each stale flag's name, its owner and its intended behaviour. The tool assigns the diff it generates to the flag's author, and over 18 months it generated cleanup diffs for 1381 flags (17% of total flags), 65% of which landed without any changes.

## Example
```go
bad:  flags := flag.NewFlagSet("feature-flags", flag.ExitOnError)
      useNewParser := flags.Bool("use-new-parser", false,
          "toggle the new parser")
good: flags := flag.NewFlagSet("feature-flags", flag.ExitOnError)
      // Owner: parser-team. Remove in v2.4, once every caller uses the new parser.
      useNewParser := flags.Bool("use-new-parser", false,
          "toggle the new parser")
```

## Limits
A kill switch whose value can be modified for emergency purposes, or a flag used for monitoring debug information, may not be stale even once it is completely rolled out, and such a flag is outside the rule. A truly optional capability that users are permanently intended to enable or disable should include its own mechanism for doing so, such as a command-line flag or configuration-file option, in addition to the temporary switch, and that mechanism is outside the rule too. Where a project enters each flag in a flag management system when the flag is introduced, the owner and expiry recorded in that entry meet the rule, and the declaration in the change need not repeat them.

## Validator
Grep the hunk for an added flag, gate or toggle: a feature-flag registration, a command-line or configuration flag definition, or a constant added to a list of flags, whose name or help text selects a new or an old path (new, old, legacy, use, enable, migrate). Open the declaration and the lines around it in the hunk: the comment or documentation above it, the metadata fields of its registration, and any registry entry the hunk adds with it. Look for an owner (a person, team or alias) and an expiry (a date or a release; a removal condition with neither is not an expiry). Skip a flag whose declaration states it is a permanent setting, a kill switch or a debug switch, and a flag in a project whose documented convention keeps owner and expiry in a flag management system. Validator question: **Does the hunk add a flag that switches between an old and a new path whose declaration, and the registry entry the hunk adds with it, record no owner or no expiry date or release?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: CHG-33`, severity suggestion, `file`, `symbol`, `code` = the added flag declaration line, `fix` = the same declaration with its owner and its expiry date or release recorded beside it, in the file's language, `rationale` = that a switch between an old and a new path is meant to be removed and that without a recorded owner and expiry its cleanup can be neither scheduled nor assigned).

## Source
- DOI 10.1145/3377813.3381350, ICSE-SEIP 2020, author copy `report.pdf` in the uber/piranha repository (fetched) — §6 Recommendations: "When a feature flag is created initially, the owner of the flag should also define an expiry date for the flag. This clear intent enables automated cleanup tools to generate diffs without confusing developers. Further, the owner for each flag should be tracked precisely." §2 Background and Motivation: "When the goal of a feature flag is accomplished [...], the flag needs to be disabled in the feature flag management system and all code artifacts related to the flag need to be removed from the source code."; "Oftentimes, developers do not cleanup code related to obsolete flags, causing accumulation of technical debt."; "Orphaned flags: Flags whose owners have left the organization and the final status of the flag roll out is unclear."; "the overall reliability of the application can be adversely affected in the presence of unnecessary control flow paths"; "effort must be spent to maintain test coverage of these unnecessary paths"; "the presence of dead code and tests impacts the overall build and testing time"; "In order to introduce a flag in the codebase, a developer creates an entry in the flag management system, and inputs attributes related to the name of the flag, type of the flag, roll-out percentages, targeted platforms, geographical locations where the flag is operational, etc." §3 Challenges: "certain flags are used as kill switches whose values can be modified for emergency purposes, flags that are used for monitoring debug information, etc. Therefore, even when flags are completely rolled out, they may not necessarily be stale."; "Since flags were not cleaned up for a long period of time, determining ownership information for stale flags became problematic." §4.4 Piranha pipeline: "The Piranha pipeline queries the flag management system for a list of stale flags, and invokes Piranha, providing as input the name of the stale flag, its owner, and the intended output behavior". Abstract: "Piranha takes as input the name of the flag, expected treatment behavior, and the name of the flag’s author."; "The diff is assigned to the author of the flag for further processing"; "deployment of Piranha from Dec 2017 to May 2019"; "generated code cleanup diffs for 1381 flags (17% of total flags), (b) 65% of the diffs landed without any changes". §1.1: "our findings on the usage of Piranha over 18 months".
- kubernetes/community, `contributors/devel/sig-architecture/feature-gates.md` (fetched): "Feature gates are _not_ intended to be long-term APIs. Individual gates are expected to be deprecated and removed after a feature becomes GA (or is dropped)."; "Typically, we add a comment in the code such as: `// remove in 1.23` to signal when we plan to remove the feature gate."; "Truly optional capabilities which are permanently intended to be enabled or disabled by users (even once the feature is GA) should include a mechanism for enabling or disabling the feature (like a command-line flag or config file option) in addition to the associated feature gate."
- Caveat: both sources report practice with feature flags and gates (one company's Objective-C, Java and Swift mobile apps; one open-source project); neither measures the effect of recording an owner and expiry, so the rule rests on their stated recommendation and practice.

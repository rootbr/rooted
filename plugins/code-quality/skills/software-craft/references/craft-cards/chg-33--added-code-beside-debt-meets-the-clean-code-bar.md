---
title: Code a change adds to code that already carries debt meets the same bar as code added to clean code, reusing functionality the code already provides and repeating none of the surrounding duplication, poor names or other smells
rule_id: CHG-33
domain: change
step: [implement]
applies_to: [universal]
triggers: ['signal:duplicate_block', 'signal:long_routine', 'signal:deep_nesting', 'signal:magic_number']
scope: file
check_kind: semantic
severity_default: minor
---

# Code a change adds to code that already carries debt meets the same bar as code added to clean code, reusing functionality the code already provides and repeating none of the surrounding duplication, poor names or other smells

## Thesis
When a change extends code that already carries technical debt, such as duplicated logic, non-descriptive names or other code smells, the code the change adds meets the bar the project sets for any new code. It reuses the functionality the surrounding code already provides instead of re-implementing it, gives what it introduces descriptive names, and repeats none of the smells around it.

## Rationale
Existing debt causes new debt: in a controlled experiment in which developers extended systems with high or low debt density, a causal analysis attributed the effects to the pre-existing debt. Existing debt increased the likelihood that developers introduced new debt when extending a system, and existing debt of a given type increased the likelihood of new debt of that type, even in cases where it was not necessary to do so. Against the low-debt systems, the high-debt systems made developers 102% more likely to duplicate existing logic, 458% more likely to give a variable a non-descriptive name, and led them to introduce 117% more issues reported by a static analyser, all established with 95% credible intervals and estimated for a developer with ten years of professional experience. Codebases often degrade through small decreases in code health over time, especially when a team under significant time constraints feels it has to take shortcuts; most systems become complex through many small changes that add up, so preventing even small complexities in new changes is important.

## Example
```typescript
bad:  // module has orderTotal, withTax and fmt1(o), which inlines withTax's 1.0825
      function fmt2(o: Order): string {
        return o.id + " (backorder): " + (orderTotal(o) * 1.0825).toFixed(2);
      }
good: function formatBackorder(order: Order): string {
        return `${order.id} (backorder): ${withTax(orderTotal(order)).toFixed(2)}`;
      }
```

## Limits
The rule judges the code the change adds, not the debt already present: reviewers favor approving a change that definitely improves the overall code health even if it is not perfect, and surrounding problems the change exposes but cannot address now are filed for cleanup and assigned to the change's author, optionally with the project's debt marker in the code referencing the filed issue. A different but better name for something already existing in adjacent code could be more confusing than a bad but consistent naming scheme; for new variables, mimicking the bad naming scheme has no practical advantage. Where the surrounding code departs from the project's style guide, the added code follows the guide where it requires a form; where the guide only recommends one, the choice between the recommendation and the surrounding code is a judgment call biased toward the guide unless the local inconsistency would be too confusing; where no style rule applies, the added code keeps the surrounding code's style conventions, a consistency that never extends to re-implementing functionality the code already provides, a non-descriptive name for a new identifier or a repeated smell. Checking in a change that definitely worsens the overall code health is reserved for an emergency.

## Validator
Read the hunk's added routines, blocks and identifiers. Open the file and note the debt around the change: duplicated blocks, long routines, deep nesting, magic numbers, short or non-descriptive names. For each added block, search the file and its imports for an existing routine that already computes the same result. For each identifier the hunk introduces, compare its name with what it holds, and set aside a name that only refers to an entity already named that way in adjacent code. Check whether the added code reproduces a smell of the surrounding code that a clean form would avoid. Validator question: **Where the surrounding code already carries debt, does the added code re-implement functionality the file or its imports already provide, give a newly introduced identifier a non-descriptive name, or reproduce a smell of that code where a clean form was available?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: CHG-33`, severity minor, `file`, `symbol`, `code` = the added lines that re-implement existing functionality, misname a new identifier or repeat the surrounding smell, quoted verbatim from the diff, `fix` = the added code rewritten in the file's language to call the existing routine, name the new identifier for what it holds or drop the repeated smell, `rationale` = the debt pattern in the surrounding code that the change repeats and the existing routine or descriptive name the added code should use).

## Source
- arXiv:2209.01549; DOI 10.1007/s10664-024-10456-6, Abstract and Sect. 7 'Discussion' (fetched, arXiv v1 text) — "a controlled experiment [...] completing a system extension tasks in an already existing systems with high or low TD density"; "pre-existing TD is the cause of the effects"; "Finding 1 (RQ1): Existing TD increases the likelihood of developers introducing new TD when extending a system, even in cases where it is not necessary to do so."; "Finding 2 (RQ1.1): Existing TD of a certain type increases the likelihood of developers introducing new TD of that type when extending a system, even in cases where it is not necessary to do so."; "Developers are 102% more likely to duplicate existing logic in our systems with high levels of TD"; "Developers are 458% more likely to assign a variable a non-descriptive name in systems with high levels of TD"; "Developers introduce 117% more SonarQube issues in our systems with high levels of TD"; "All of these were established by investigating 95% credible intervals."; "Effect estimated for a developer with 10 years of professional programming experience"; "using a different (but better) variable name to describe something already existing in adjacent classes could be more confusing than a bad (but consistent) naming scheme"; "there is no practical advantage to mimicking the bad naming scheme for new variables"
- google/eng-practices review/reviewer/looking-for.md, Context and Consistency (fetched) — "Don't accept CLs that degrade the code health of the system. Most systems become complex through many small changes that add up, so it's important to prevent even small complexities in new changes."; "What if the existing code is inconsistent with the style guide?"; "if something is required by the style guide, the CL should follow the guidelines"; "it's a judgment call whether the new code should be consistent with the recommendations or the surrounding code. Bias towards following the style guide unless the local inconsistency would be too confusing."; "If no other rule applies, the author should maintain consistency with the existing code."
- google/eng-practices review/reviewer/standard.md (fetched) — "often, codebases degrade through small decreases in code health over time, especially when a team is under significant time constraints and they feel that they have to take shortcuts"; "reviewers should favor approving a CL once it is in a state where it definitely improves the overall code health of the system being worked on, even if the CL isn't perfect."; "Nothing in this document justifies checking in CLs that definitely worsen the overall code health of the system. The only time you would do that would be in an emergency."
- google/eng-practices review/reviewer/pushback.md, Cleaning It Up Later (fetched) — "If the CL exposes surrounding problems and they can't be addressed right now, the developer should file a bug for the cleanup and assign it to themselves so that it doesn't get lost. They can optionally also write a TODO comment in the code that references the filed bug."
- Caveat: the experimental evidence is one controlled experiment in Java with 29 developers from a convenience sample; the effect sizes are estimated for a developer with ten years of professional experience on the study's tasks and systems.

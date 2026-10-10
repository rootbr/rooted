---
title: Code that changes together for one reason sits in one release or deployment component, so one requirement does not repeatedly need coordinated edits in several separately released or deployed components
rule_id: ARCH-04
domain: architecture
step: [design, implement, review]
applies_to: [universal]
triggers: ['signal:duplicate_block', 'signal:added_file', '^\s*(module\s+[\w.~-]+(/[\w.~-]+)+\s*$|\[(package|project|workspace)\]\s*$|<module>[^<]+</module>|include\s*\(?\s*["'']:)']
scope: callers
check_kind: semantic
severity_default: major
---

# Code that changes together for one reason sits in one release or deployment component, so one requirement does not repeatedly need coordinated edits in several separately released or deployed components

## Thesis
When the version history shows two or more separately released or deployed components changing together repeatedly for one shared reason — the same requirement's knowledge or decision — the code that changes for that reason is gathered into one component, and the boundary is judged on the change history and the dependency structure together.

## Rationale
The property at stake is modularity, the capability of a product to limit changes to one component from affecting other components. Co-change mined from version history shows coupling that program analysis does not detect, and following it can prevent errors due to incomplete changes; in the history of eight open-source projects, after an initial change, the top three mined suggestions contained a correct location with a likelihood of more than 70 percent. Regression models found that co-changes including files from different subsystems result in more bugs than co-changes including files from one subsystem only. Inside each of two systems, discrepancies between how its parts should change together under the modular structure and how they actually change together in version history were, in hundreds of cases across 15 releases of one system and 10 releases of the other, recognized as design problems or refactored by the developers in later versions. Across 19 large projects, files involved in architecture anti-patterns detected from structural relationships and revision history were more error-prone and change-prone, and the more such anti-patterns a file was involved in, the more error-prone and change-prone it was. Dependencies alone misrepresent co-change: approximately half of all dependencies are never involved in a co-change, and the vast majority of co-changes pertain to a small percentage of dependencies, so both the change history and the dependency structure enter the judgment of a boundary. Logical coupling found in release history marks potential structural shortcomings to be examined further, pointing to restructuring opportunities, so a finding is a candidate for examination rather than a verdict.

## Example
```go
bad:  module example.com/pricing
      func Gross(net float64) float64 { return net * 1.19 }
      module example.com/invoicing
      func VATLine(net float64) float64 { return net * 0.19 }
good: package tax // module example.com/tax releases every VAT rule
      const Rate = 0.19
      func VAT(net float64) float64 { return net * Rate }
      func Gross(net float64) float64 { return net + VAT(net) }
```

## Limits
Co-change alone does not decide membership. In a class-level case, methods that clean up a data connection for two different protocols tended to change together and were still correctly placed in different classes that split the system's responsibilities well; merging them only to isolate the change could create a class managing heterogeneous responsibilities. Tangled commits make all changes to all modules appear related: in five open-source projects up to 15% of bug fixes consisted of multiple tangled changes, and on average at least 16.6% of source files were incorrectly associated with bug reports; a coupling-analysis tool by default leaves change sets of more than 30 files out of its coupling analysis. In two large industrial systems the correlation between evolutionary coupling and defects was generally positive but varied in strength, and was less likely to hold for parts with fewer files and fewer contributing developers. Coupling and cohesion need to be balanced against developers' intuition of which entities conceptually belong together. The separating condition: the rule holds where the co-changing code changes for one shared reason, the same requirement's knowledge or decision, counted over change sets made for that reason; it does not hold for variants of one role for different cases, or for files related only through tangled or oversized change sets. The rule reaches separately released or deployed components; change locality among classes and routines inside one component sits outside it.

## Validator
List the files the hunk changes and map each to its release or deployment component — the module, package, workspace member or deployable service a build manifest declares. Where the change touches two or more such components, or adds a component or a duplicated block, read the changed code in each component and trace whether the edits carry the same requirement's knowledge or decision — one rule, one constant, one schema field, one message format — or implement one role for different cases, or are unrelated edits bundled into one change. Search the repository for usages of the changed symbols, and check whether a dependency between the components explains the shared edit. Validator question: **Does this change edit one requirement's knowledge or decision in two or more separately released or deployed components, so that each later change for that reason needs coordinated edits in all of them, rather than variants of one role for different cases?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: ARCH-04`, severity major, `file`, `symbol`, `code` = the line in each component that carries the shared reason's code, quoted verbatim from the diff, `fix` = that code gathered into one component the others depend on, in the file's language, `rationale` = the shared reason, the components that carry its code and the usages or copies in each that a later change for that reason must also edit).

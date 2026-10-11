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

## Source
- doi:10.1109/ICSE.2013.6606741, abstract (fetched): "Using statistical regression models we show that co-changes that include files from different subsystems result in more bugs than co-changes that include files only from the same subsystem".
- doi:10.1145/1985793.1985850, abstract (fetched): "the discrepancies between how components should change together based on the modular structure, and how components actually change together as revealed in version history"; "We evaluated Clio using 15 releases of Hadoop Common and 10 releases of Eclipse JDT"; "hundreds of violations identified using Clio were indeed recognized as design problems or refactored by the developers in later versions".
- doi:10.1109/TSE.2019.2910856, abstract (fetched): "by analyzing a project's structural relationships and revision history"; "Through our analyses of 19 large-scale software projects"; "files involved in these architecture anti-patterns are more error-prone and change-prone"; "the more anti-patterns a file is involved in, the more error-prone and change-prone it is".
- doi:10.1109/TSE.2005.72, abstract (fetched): "show up item coupling that is undetectable by program analysis, and 3) can prevent errors due to incomplete changes"; "After an initial change, our ROSE prototype can correctly predict further locations to be changed"; "In our evaluation based on the history of eight popular open source projects, ROSE's topmost three suggestions contained a correct location with a likelihood of more than 70 percent".
- doi:10.1109/TSE.2011.91, abstract (fetched): "approximately half of all dependencies are never involved in cochanges and that the vast majority of cochanges pertain to only a small percentage of dependencies"; "inferring the cochange characteristics of a software architecture solely from its dependency structure results in a severely distorted approximation"; "always take both the change characteristics and the dependency structure into account".
- doi:10.1109/ICSM.1998.738508, abstract (fetched): "potential structural shortcomings can be identified and further examined, pointing to restructuring or reengineering opportunities".
- ISO/IEC 25010:2023, modularity (relayed through a fetched transcription): "Capability of a product to limit changes to one component from affecting other components."
- code-maat README, § Mining logical coupling and options table (fetched): "Logical coupling refers to modules that tend to change together"; "the first column (`entity`) gives us the name of the module"; "consider the `InfoUtils.java` module in the example output above"; "--max-changeset-size MAX-CHANGESET-SIZE 30 Maximum number of modules in a change set if it shall be included in a coupling analysis".
- doi:10.1109/TSE.2014.2372760, § 3.2.2 (fetched): "even if the four involved methods tend to change together, they are correctly placed into different classes splitting well the system's responsibilities"; "both in charge of cleaning up a data connection, the two protocols they manage are different"; "no apparent reason for placing them in the same class with the only goal of isolating the change"; "this refactoring operation could create a class managing heterogeneous responsibilities".
- doi:10.1109/MSR.2013.6624018, abstract (fetched): "such tangled changes will make all changes to all modules appear related"; "In an investigation of five open-source [...] projects, we found up to 15% of all bug fixes to consist of multiple tangled changes"; "on average at least 16.6% of all source files are incorrectly associated with bug reports".
- doi:10.1002/smr.1842, abstract (fetched): "We analysed 2 large industrial systems"; "there is generally a positive correlation between EC and defects, but the correlation strength varies"; "less likely to have a relationship to software defects for parts of the software with fewer files and where fewer developers contributed".
- doi:10.1109/TSE.2017.2786222, abstract (fetched): "sound design principles (e.g., coupling and cohesion) need to be balanced against developer intuition of which entities conceptually belong together".
- Caveat: the studies measure files, classes and subsystems inside one codebase; the rule carries their cross-subsystem finding to release and deployment units.

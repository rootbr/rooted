---
title: A change presented as a refactoring alters no observable behaviour of the code it restructures, including the values it returns, the errors it raises and the order of its side effects
rule_id: CHG-01
domain: change
step: [refactor, review]
applies_to: [universal]
triggers: ['\b(def|fn|function)\s+\w+\s*[(<\[]|\bfunc\s+(\([^)]*\)\s*)?\w+\s*[(\[]|\b(public|protected|private|internal|static)\s+[\w<>\[\],.? ]+\s+\w+\s*\(', '^\s*(import\s|from\s+[\w.]+\s+import\s|use\s+[\w:{]+|package\s+\w+)', 'signal:added_file']
scope: base-compare
check_kind: semantic
severity_default: major
---

# A change presented as a refactoring alters no observable behaviour of the code it restructures, including the values it returns, the errors it raises and the order of its side effects

## Thesis
A change presented as a refactoring, or made up only of restructuring edits such as renames, moves, extractions and inlinings, preserves the external behaviour of the code it restructures: for the same input, every caller the change leaves unedited and every public or exported routine it edits gets the same returned values and raised errors, sees argument expressions and calls that have side effects or can raise run in the same order, and observes the same writes, output and mutations as in the base version; a non-public routine whose parameters, return value or raised errors the change alters together with all of its callers is judged through those callers. Any defect fix or feature the change carries is declared as a behaviour change of its own. The check applies whether the edits were made by hand, by a refactoring engine, by an automatic lint fix or by a language model, and a passing regression suite leaves it open.

## Rationale
A refactoring is a transformation that preserves the external behaviour of a program and improves its internal quality; comparing each edit with the base version is what confirms the first half of that definition. Manual refactoring is commonly supported by regression testing as its safety net, and that net misses anomalies inspection finds: a static inspection of manual refactoring edits detected 22 times more anomalies than the existing regression suites, with 94 percent precision on average, and 24 percent of the seeded anomalies it identified were not detected by generated test suites. In a study with 15 professional developers, participants located 13 percent of the seeded anomalies with testing only, against 90 percent with inspection support. Even mainstream refactoring engines contain bugs: testing 29 refactorings in three refactoring engines over 153,444 transformations identified 63 bugs related to behavioural changes and 57 related to compilation errors. Of the refactoring solutions two language models suggested, 13 of 176 and 9 of 137 were unsafe, either changing the functionality of the code or introducing syntax errors. An automatic lint fix documented as unsafe changes the exception raised on an empty collection to a different type, which could break error handling upstream, and an inliner takes care to avoid even subtle behaviour changes, such as changes to the order in which argument expressions are evaluated. Developers proceed with an automated refactoring even when it may change the behaviour of the program, and rarely preview automated refactorings. In three large open source projects totalling 26,523 revisions, bug fixes increased after API-level refactorings, and a large number of refactoring revisions included bug fixes at the same time or were related to later bug-fix revisions. In practice the word refactoring is not confined to semantics-preserving transformations, and developers perceive refactoring as involving substantial cost and risk, so the label alone does not show that a change's edits preserve behaviour.

## Example
```typescript
bad:  // inlined from: return charge(readAmount(), readFee()); where charge(a, f) returns a + f
      import { readAmount, readFee } from "./meter";
      function total(): number {
        return readFee() + readAmount();
      }
good: function total(): number {
        const amount = readAmount();
        const fee = readFee();
        return amount + fee;
      }
```

## Limits
A large number of refactoring revisions include bug fixes at the same time, and tool support is called for to apply refactoring and behaviour-modifying edits together; a behaviour change the change declares, as a fix or a feature, is judged as that change, and this rule reaches only a difference the change presents as absent. Running time is outside the check: a documented lint fix that speeds a first-element lookup from 1.69 seconds to 70.8 nanoseconds per loop is classed as unsafe because the type of the exception it raises changes, which could break error handling upstream. Putting untested code under tests before restructuring it, splitting a change into commits, and migrating external callers of a renamed public interface lie outside this rule.

## Validator
Read the change's title, description and commit messages, and grep the hunks for renamed, moved, extracted or inlined declarations: routine signatures, imports and added files. When the change is presented as a refactoring or its edits are all restructurings, open every edited routine and every call site of a moved, renamed, extracted or inlined routine at the base version and at the head; where the change alters a non-public routine's parameters, return value or raised errors and updates all of its callers with it, make the comparison at those callers rather than inside the routine. Trace the same inputs, including empty, absent and boundary values, through both versions and compare the returned values, the errors raised and their types, the order in which argument expressions and calls that have side effects or can raise run, and the writes, output and mutations performed. Apply the same comparison to edits a refactoring engine, a lint fix or a language model produced, and treat passing tests as no answer either way. Validator question: **Does a change presented as a refactoring, or made up only of restructuring edits, give some caller it leaves unedited, or some public or exported routine it edits, a different returned value or raised error, a different order of argument expressions or calls that have side effects or can raise, or a different write, output or mutation than in the base version for some input, without the change declaring that behaviour change?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: CHG-01`, severity major, `file`, `symbol`, `code` = the edited head line and the base line it replaces, quoted verbatim, `fix` = the restructured code rewritten to keep the base version's returned value, raised error, side effects and their order, or the behaviour change split out and declared, in the file's language, `rationale` = the input on which the two versions differ and the behaviour that differs).

## Source
- DOI 10.1109/TSE.2012.19, "Automated Behavioral Testing of Refactoring Engines", abstract (fetched): "Refactoring is a transformation that preserves the external behavior of a program and improves its internal quality." "even mainstream refactoring engines contain critical bugs." "We have evaluated this technique by testing 29 refactorings in Eclipse JDT, NetBeans, and the JastAdd Refactoring Tools. We analyzed 153,444 transformations, and identified 57 bugs related to compilation errors, and 63 bugs related to behavioral changes."
- RefactoringMiner README, §Supported Refactoring Types (fetched): "15. Change Return Type" "32. Add Parameter" "33. Remove Parameter" "34. Reorder Parameter" "35. Add Thrown Exception Type" "36. Remove Thrown Exception Type" "37. Change Thrown Exception Type"
- DOI 10.1109/TSE.2017.2679742, "Refactoring Inspection Support for Manual Refactoring Edits", abstract (fetched): "Refactoring is commonly performed manually, supported by regression testing, which serves as a safety net" "of which 24 percent are not detected by generated test suites. Compared to running existing regression test suites, it detects 22 times more anomalies, with 94 percent precision on average." "With RefDistiller, participants located 90 percent of the seeded anomalies, while they located only 13 percent with testing."
- arXiv:2411.04444, "An Empirical Study on the Potential of LLMs in Automated Software Refactoring", abstract (fetched): "13 out of the 176 solutions suggested by ChatGPT and 9 out of the 137 solutions suggested by Gemini were unsafe in that they either changed the functionality of the source code or introduced syntax errors"
- DOI 10.1109/ICSE.2012.6227190, "Use, Disuse, and Misuse of Automated Refactorings", abstract (fetched): "proceed with an automated refactoring even when it may change the behavior of the program, and rarely preview the automated refactorings"
- DOI 10.1145/1985793.1985815, "An empirical investigation into the role of API-level refactorings during software evolution", abstract (fetched): "three large open source projects, totaling 26523 revisions" "there is an increase in the number of bug fixes after API-level refactorings" "a large number of refactoring revisions include bug fixes at the same time or are related to later bug fix revisions" "tools to support safe application of refactoring and behavior modifying edits together"
- DOI 10.1145/2393596.2393655, "A field study of refactoring challenges and benefits", abstract (fetched): "the refactoring definition in practice is not confined to a rigorous definition of semantics-preserving code transformations and that developers perceive that refactoring involves substantial cost and risks"
- golang.org/x/tools go/analysis/passes/inline, package documentation (fetched): "The inliner takes care to avoid behavior changes, even subtle ones, such as changes to the order in which argument expressions are evaluated."
- Ruff linter documentation, §Fix safety, RUF015 (fetched): "an unsafe fix could lead to a change in runtime behavior" "when the collection is empty, this raised exception changes from an `IndexError` to `StopIteration`" "Since the change in exception type could break error handling upstream, this fix is categorized as unsafe."
- Caveat: the engine and model studies examined Java code, and the inspection figures count seeded anomalies.

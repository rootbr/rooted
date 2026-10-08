---
title: A routine longer than about 40 lines is split where a part can be broken out without harming the program's structure, and length alone is not the finding
rule_id: CODE-36
domain: code
step: [implement, refactor, review]
applies_to: [universal]
triggers: ['signal:long_routine']
scope: file
check_kind: semantic
severity_default: minor
---

# A routine longer than about 40 lines is split where a part can be broken out without harming the program's structure, and length alone is not the finding

## Thesis
A routine longer than about 40 lines is read for a part that can be broken out into a routine of its own without harming the program's structure: a block that does a well-defined task and can carry a descriptive name. Where such a part exists, the routine is split. Length alone is not the finding: a routine whose length comes from a conceptually simple body, such as one long but simple case statement doing small things for many different cases, may stay whole.

## Rationale
A routine that grows too large tends to aggregate too many responsibilities, and becomes harder to understand and therefore harder to maintain. Even when a long routine works now, someone modifying it later may add new behaviour, which could result in bugs that are hard to find. In a study of the evolution of about 785,000 methods from 49 open-source projects, a method's length in source lines of code correlated with its change- and bug-proneness, more weakly with bug-proneness than with change-proneness; methods of 24 source lines or fewer were less change- and bug-prone, and a group of small methods whose lengths sum to x was generally collectively less change- and bug-prone than one method of length x. In a controlled experiment with 61 novice programmers, the program carrying a long method mainly decreased system understanding. At the class level, a study of class size in three systems, with four size measures, found no threshold effect, and its findings suggest a simple continuous relationship between class size and faults. The length a routine can carry shrinks as its complexity and indentation level grow, so a complex routine keeps closer to the bound and moves its pieces into helper routines with descriptive names. The 40 lines mark where to start looking for such a piece, not a hard limit. The property restored is a routine whose parts each do a well-defined task under a name of their own.

## Example
```java
bad:  void importOrders(Path file) {
          // 20 lines: read each row into an Order
          // 25 lines: check each Order, collect the errors
          // 15 lines: insert the valid Orders
      }
good: void importOrders(Path file) {
          List<Order> orders = parseRows(file);
          List<Order> valid = validate(orders);
          insertAll(valid);
      }
```

## Limits
Long routines are sometimes appropriate, so the length is a prompt and not a hard limit. A routine whose length comes from a conceptually simple body, one long but simple case statement doing lots of small things for a lot of different cases, may be longer than the bound and may stay whole. A routine-length bound set in the project's documented linter configuration or style guide replaces the 40 lines for the routines it covers; the routine-length rules of five static-analysis tools default to bounds between 50 and 150 lines, and each lets a project configure its own. How far to decompose is contested. One position refactors a routine above a fixed threshold into smaller routines that focus on well-defined tasks, and a method-size study recommends keeping methods within 24 source lines; the other places no hard limit on routine length, because long routines are sometimes appropriate. The condition that separates the cases is whether the routine holds a part that can be broken out without harming the program's structure. Where it does, the routine is split, because a group of small methods was generally collectively less change- and bug-prone than one large method of the same total size. Where the length comes from a conceptually simple body, the routine may stay whole, because the maximum length shrinks with complexity and indentation level rather than following one count. Nesting depth, branch complexity, a duplicated block, the parameter list and the split of a class or module are outside this rule.

## Validator
Read the `long_routine` value the hunk carries, open the file and read the enclosing routine through. Drop the routine when a routine-length bound in the project's documented configuration admits its length. Mark each block that does a well-defined task of its own, such as a phase of the work, a loop body, or a block that computes one value later lines use, and check that it could take a descriptive name and be read on its own once moved, with its inputs passed in and its result returned. Drop the routine when its length comes from one conceptually simple body, such as one long but simple case statement doing small things for many cases. Validator question: **Is the routine longer than about 40 lines, or the project's configured bound, and does it hold a block that does a well-defined task and could move into its own descriptively named routine without harming the program's structure?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: CODE-36`, severity minor, `file`, `symbol`, `code` = one added line inside the routine, verbatim from the diff, preferring the first line of the block that can be broken out or the routine's signature line when the diff adds it, `fix` = the routine with that block moved into a new routine whose name states its task and a call in its place, in the file's language, `rationale` = the routine's line count, the first line of the block that can be broken out and the well-defined task the block performs).

## Source
- Google Python Style Guide §3.18 Function length (google/styleguide, pyguide.md; the same paragraph in the Google C++ Style Guide, Write Short Functions) (fetched): "Prefer small and focused functions."; "We recognize that long functions are sometimes appropriate, so no hard limit is placed on function length. If a function exceeds about 40 lines, think about whether it can be broken up without harming the structure of the program."; "Even if your long function works perfectly now, someone modifying it in a few months may add new behavior. This could result in bugs that are hard to find."
- Linux kernel coding style §6 Functions (torvalds/linux, Documentation/process/coding-style.rst) (fetched): "The maximum length of a function is inversely proportional to the complexity and indentation level of that function."; "if you have a conceptually simple function that is just one long (but simple) case-statement, where you have to do lots of small things for a lot of different cases, it's OK to have a longer function."; "if you have a complex function [...] you should adhere to the maximum limits all the more closely. Use helper functions with descriptive names".
- SonarSource S138 (sonar-python S138.html; default 100 lines in python-checks TooManyLinesInFunctionCheck, 75 in sonar-java MethodTooBigCheck) (fetched): "A function that grows too large tends to aggregate too many responsibilities. Such functions inevitably become harder to understand and therefore harder to maintain. Above a specific threshold, it is strongly advised to refactor into smaller functions which focus on well-defined tasks."
- ESLint `max-lines-per-function`, Checkstyle `MethodLength`, clippy `too_many_lines`, funlen (fetched): "`"max"` (default `50`) enforces a maximum number of lines in a function."; `max` "Specify the maximum number of lines allowed." default 150; `too-many-lines-threshold` "Default Value: `100`"; "The default limits are 60 lines and 40 statements. You can configure these."
- arXiv:2205.01842, DOI 10.1145/3524842.3527975 (fetched): "we examine the evolution of ∼785K Java methods"; "from 49 open-source software projects"; "SLOC correlates with change- and bug-proneness at the method-level granularity. SLOC’s correlation with bug-proneness is generally lower than change-proneness."; "Methods of 24 SLOC or fewer exhibit less change- and bug-proneness. Therefore, developers should strive to keep their methods within 24 SLOC."; "A group of small methods, with sum SLOC x, are generally collectively less change- and bug-prone than an individual large method with SLOC x."
- DOI 10.1109/icpc.2016.7503706 (fetched): "We conduct a controlled experiment with 61 novice Scratch programmers"; "we find that Long Method mainly decreases system understanding".
- DOI 10.1109/TSE.2002.1000452 (fetched): "Our results provide unambiguous evidence that there is no threshold effect of class size. We obtained the same result for three systems using four different size measures. These findings suggest that there is a simple continuous relationship between class size and faults"
- Caveat: the method-size study measured correlation in open-source Java projects; the comprehension experiment used novices on block-based programs; the threshold study measured class size, not routine size; the 40 lines and the tool defaults are guidance and configuration, not measured thresholds.

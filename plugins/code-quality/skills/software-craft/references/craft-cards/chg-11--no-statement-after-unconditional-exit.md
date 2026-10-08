---
title: No statement follows a return, throw, raise, break, continue, never-returning call or exitless loop in the same block, because such a statement can never run and is usually a mistake
rule_id: CHG-11
domain: change
step: [implement, review]
applies_to: [universal]
triggers: ['^\s*(?:return\b|throw\b|raise\b|break\b|continue\b)|\b(?:panic!?|unreachable!|todo!|unimplemented!)\s*\(|^\s*(?:for\s*\{|for\s*\(\s*;\s*;\s*\)|loop\s*\{)']
scope: hunk
check_kind: mechanical
severity_default: major
---

# No statement follows a return, throw, raise, break, continue, never-returning call or exitless loop in the same block, because such a statement can never run and is usually a mistake

## Thesis
Every statement in a block is reachable under the language's control-flow rules: a return, a throw or raise, a break, a continue, a call the language counts as never returning such as a panic, a branching statement with an else whose every branch exits, or a loop with no condition, no range or collection to run out of and no break that refers to it is the last statement of its block, save a statement after it that carries a label control can jump to, such as the target of a goto or a case or default label. The claim covers what the control-flow rules alone make unreachable, not code that only the values of data rule out.

## Rationale
A return, throw, continue or break unconditionally exits its block, so any statement after it in that block cannot be executed; the same holds after a call to panic and after a loop with no exit. Unreachable statements are usually a mistake, and they may also signal unfinished code. When the statements are meant to run, the mistake lies in the exit, which then belongs after them or under a condition; when the code is no longer in use, it is a candidate for removal. Several toolchains accept such code by default and report it only as an editor suggestion or a warning, or leave it to a separate analyzer, so a passing build does not rule it out.

## Example
```go
bad:  if err != nil {
          return err
          log.Printf("write failed: %v", err)
      }
good: if err != nil {
          log.Printf("write failed: %v", err)
          return err
      }
```

## Limits
A function declaration, or a variable declaration without an initializer, that the language hoists to the top of its scope may follow an exit; an initializer after an exit never runs and stays in the rule. A statement whose presence alone changes what the enclosing function is, such as a yield after a return that makes the function an empty generator, may follow an exit. A statement that carries a label control can jump to, such as the target of a goto or a case or default label, is reachable after an exit, and so are the statements after it. A call that the language does not list as terminating leaves the next statement reachable under the control-flow rules, whatever the callee does at run time; where a function that declares results must end in a terminating statement, the statement after such a call is required and stays. Code that appears unreachable only through type analysis or the values of data is outside the rule; an analysis of infeasible paths that compares the control-flow graph with a more precise abstract interpretation reaches it.

## Validator
Grep the hunk's added and context lines for an exit: a return, throw, raise, break or continue, a call the language counts as never returning, or a loop header with neither a condition nor a range or collection to iterate. For each match, open the enclosing block and read the statements that follow the exit at the same nesting level up to the block's close, and, where every branch of a branching statement with an else ends in an exit, the statements that follow that branching statement in its own block, keeping those the hunk adds and those that follow an exit the hunk adds. Skip a hoisted function declaration, a hoisted variable declaration without an initializer, a yield that makes the enclosing function a generator, a statement the compiler demands after a call it does not count as terminating, and a statement that carries a label control can jump to, together with the statements after it. Validator question: **Does a statement the hunk adds, or one that follows an exit the hunk adds, sit in the same block after a return, throw or raise, break, continue, a call the language counts as never returning, a branching statement whose every branch exits, or a loop with no condition, no range or collection to run out of and no break?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: CHG-11`, severity major, `file`, `symbol`, `code` = the exiting statement and the first statement after it, quoted verbatim from the diff, `fix` = the block with the exit moved after the statements meant to run, or with the unreachable statements removed, in the file's language, `rationale` = names the exit and states that the statements after it in the same block can never execute).

## Source
- ESLint core rule no-unreachable (type problem, recommended: true), eslint/eslint main docs/src/rules/no-unreachable.md and lib/rules/no-unreachable.js: "Because the `return`, `throw`, `continue`, and `break` statements unconditionally exit a block of code, any statements after them cannot be executed. Unreachable statements are usually a mistake."; correct examples "because of JavaScript function and variable hoisting", and lib/rules/no-unreachable.js reports a variable declaration when `node.kind !== "var" || node.declarations.some(isInitialized)` (fetched)
- rustc lint UNREACHABLE_CODE (default level Warn), rust-lang/rust master compiler/rustc_lint_defs/src/builtin.rs: "Unreachable code may signal a mistake or unfinished code. If the code is no longer in use, consider removing it." (fetched)
- go vet analyzer unreachable, golang/tools master go/analysis/passes/unreachable/doc.go: "finds statements that execution can never reach because they are preceded by a return statement, a call to panic, an infinite loop, or similar constructs" (fetched)
- go vet analyzer unreachable, golang/tools master go/analysis/passes/unreachable/unreachable.go, findDead: "Is this a labeled goto target? If so, assume it is reachable due to the goto.", and each case clause of a switch starts with `d.reachable = true` (fetched)
- Go language specification, golang/go master doc/go_spec.html, Terminating statements: "A call to the built-in function panic."; "An \"if\" statement in which: the \"else\" branch is present, and both branches are terminating statements."; "A \"for\" statement in which: there are no \"break\" statements referring to the \"for\" statement, and the loop condition is absent, and the \"for\" statement does not use a range clause."; "All other statements are not terminating."; Function declarations: "If the function's signature declares result parameters, the function body's statement list must end in a terminating statement." (fetched)
- Pylint W0101 unreachable, pylint-dev/pylint main pylint/checkers/base/basic_checker.py: "Used when there is some code behind a \"return\" or \"raise\" statement, which will never be accessed."; _check_unreachable: "Don't add 'unreachable' for empty generators." (fetched)
- TypeScript tsconfig option allowUnreachableCode, microsoft/TypeScript-Website v2 packages/tsconfig-reference/copy/en/options/allowUnreachableCode.md: "`undefined` (default) provide suggestions as warnings to editors"; "These warnings are only about code which is provably unreachable due to the use of JavaScript syntax"; "This does not affect errors on the basis of code which _appears_ to be unreachable due to type analysis." (fetched)
- DOI 10.1145/2786805.2786865 (ESEC/FSE 2015), abstract via neverworkintheory/neverworkintheory.github.io main _posts/2016/2016-06-09-hidden-truths.html: "detection of infeasible paths in code that can discover a wide range of code smells ranging from useless code that hinders comprehension to real bugs"; "calculating the difference between the control-flow graph that contains all technically possible edges and the corresponding graph recorded while performing a more precise analysis using abstract interpretation"; "the Java Development Kit as well as the Qualitas Corpus (a curated collection of over 100 Java Applications) and were able to find thousands of issues across a wide range of categories" (fetched). Caveat: the evaluated corpora are compiled Java, where a statement after an unconditional exit is a compile-time error (javac compiler.err.unreachable.stmt, openjdk/jdk master src/jdk.compiler/share/classes/com/sun/tools/javac/resources/compiler.properties), so every counted issue is a path that the values of data rule out, outside this rule; the source anchors only the Limits' pointer to infeasible-path analysis.

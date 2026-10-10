---
title: A routine takes at most five parameters unless an inherited declaration fixes its signature or a framework invokes it
rule_id: CODE-39
domain: code
step: [design, implement, refactor]
applies_to: [universal]
triggers: ['signal:many_parameters', '\b(def|func|fn|function|fun|public|private|protected|internal|static|override|abstract|async|export|pub)\b[^;=]*\((?:[^,()]*,){5,}[^()]*\)|^\s*\w+\s*\((?:[^,()]*,){5,}[^()]*\)\s*(:\s*[^;={]+)?\{|\((?:[^,()]*,){5,}[^()]*\)\s*(:\s*[^;={]+)?=>', '\b[\w<>\[\]?.]+\s+\w+\s*\((?:[^,()]*,){5,}[^()]*\)\s*(\{|throws\b)']
scope: hunk
check_kind: mechanical
severity_default: major
---

# A routine takes at most five parameters unless an inherited declaration fixes its signature or a framework invokes it

## Thesis
A routine declares at most five parameters, not counting the receiver of a method. Where a routine would need more than five, the remedy can be to split it into smaller routines with fewer parameters, each doing a part of what the original did, or to group some of its parameters into a new type that holds data belonging together in the application's domain. A routine whose signature an inherited declaration fixes, or that a framework or test runner invokes, is exempt: a method that overrides or implements an inherited declaration takes the count that declaration fixes and is judged at that declaration, and a routine that a framework or test runner invokes, such as a web request handler, a constructor or provider whose parameters a dependency-injection container supplies, or a test method, may have more.

## Rationale
An argument selection defect is a call that passes the wrong argument, such as two arguments in each other's place. A name-based detector run over 200 million lines of internal code and 10 million lines of predominantly open-source external code found such defects even in large, mature projects, and the analysis of the defects found shows that the probability of one increases markedly when a method has more than five arguments. Five is the bound that analysis gives: methods should have five or fewer parameters, and interfaces with more often lead to parameter mismatch bugs. As parameters are added, the role of individual parameters also becomes less clear and adjacent parameters of the same type become easier to confuse; a routine with many arguments is less memorable and harder to read at the call site, and its maintainers must figure out the role of each parameter and keep track of their position. Both remedies leave each routine fewer arguments: smaller routines that each do a part of what the original did, which lowers the confusion risk, or objects that group related arguments. The receiver of a method is passed implicitly and is not counted. Tools that check the count ship different configurable defaults, 3, 5, 7, 8 and 13; the one that defaults to eight documents it as a very conservative starting number, chosen although the analysis argues for five or fewer, with hopes to decrease it.

## Example
```go
bad:  func Draw(x1, y1, z1, x2, y2, z2 int) { ... }
      Draw(ax, ay, az, bx, by, bz)
good: type Point struct{ X, Y, Z int }
      func Draw(from, to Point) { ... }
      Draw(Point{ax, ay, az}, Point{bx, by, bz})
```

## Limits
A routine whose signature an inherited declaration fixes, or that a framework or test runner invokes, is outside the rule, and several tools that run the check skip it. A method that overrides or implements an inherited declaration takes the count that declaration fixes: changing the signature of an overriding method may make it incompatibly override the method it replaces, which type checkers report, and an author overriding a method from a third-party library has no control over the number of parameters. The count is judged at the inherited declaration, and an override of a declaration already over the bound is not reported a second time. Routines that a framework or test runner invokes are skipped: a web request handler, a constructor or provider method whose parameters a dependency-injection container supplies, a deserialization constructor, and a test method, which is never directly invoked. A declaration of a foreign function, whose parameters are not its author's choice, and the component list of a record type are skipped as well. A project tolerance rejects the finding: a parameter limit set in the project's linter configuration, which each tool that runs the check exposes as an option.

## Validator
Find each routine signature among the hunk's added lines, from the many_parameters signal's count or from a definition whose parameter list holds five or more commas, and read the whole parameter list in the hunk, including a list that wraps over several lines. Count one parameter per declared parameter: names that share one type declaration count separately, a destructuring pattern that binds several names from one argument counts as one parameter, and the receiver of a method (an explicit or implicit self, this or receiver) is left out. Skip the signature when the hunk shows it overriding or implementing an inherited declaration (an override keyword, annotation or decorator, or an implementation block of an interface or trait), carrying an annotation or decorator by which a framework or test runner invokes it or supplies its parameters, declaring a foreign function, or declaring a record's components. Skip it when the hunk's removed lines hold the same routine's previous signature with as many parameters or more. Validator question: **Does an added routine signature declare more than five parameters, not counting a method receiver, when no inherited declaration fixes its signature, no framework or test runner invokes it, and it declares neither a foreign function nor a record's components?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: CODE-39`, severity major, `file`, `symbol`, `code` = the added signature line or lines declaring the parameters, verbatim from the diff, `fix` = the routine split into smaller routines that each take a subset of the parameters, or the signature with the parameters that belong together grouped into one new type, in the file's language, `rationale` = the parameter count against the bound of five and that the probability of passing a wrong argument increases markedly above five).

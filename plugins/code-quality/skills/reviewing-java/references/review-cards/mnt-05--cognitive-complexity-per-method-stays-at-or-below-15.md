---
title: A method's cognitive complexity stays at or below 15, counting one per break in linear flow plus one per level of nesting
rule_id: MNT-05
domain: maintainability
triggers: ['\bif\s*\(', '\bfor\s*\(', '\bwhile\s*\(', '\bswitch\s*\(', '\bcatch\s*\(', '&&|\|\|', '\?\s*[^:]+\s*:']
scope: file
check_kind: semantic
severity_default: minor
---

# A method's cognitive complexity stays at or below 15, counting one per break in linear flow plus one per level of nesting

## Thesis
Every method the diff adds or extends has a cognitive complexity of at most 15, where each `if`, `else if`, `else`, ternary, `switch`, loop, `catch`, labelled `break` or `continue`, run of one boolean operator and recursive call adds one, and an `if`, ternary, `switch`, loop or `catch` nested inside another control structure adds one more per level of nesting, while `else`, `else if`, an operator run, a labelled jump and a recursive call take the flat increment alone; a method above 15 is split into helpers, flattened with guard clauses, or has its type-switching replaced by polymorphism.

## Rationale
The metric measures how hard the control flow of a method is to follow, not how many paths it has: a flat `switch` with ten cases costs little, a condition inside a loop inside a condition costs its own increment plus two for nesting. A meta-analysis of about 24,000 understandability evaluations over 427 code snippets found the metric positively correlated with comprehension time and with subjective understandability ratings — the first validated, solely code-based metric with that property. Above the threshold, each change to the method means re-reading branches that have nothing to do with the change.

## Example
```java
bad:  for (Order o : orders) {                            // +1
          if (o.isOpen()) {                               // +1, +1 nesting
              if (o.total() > limit && o.isRush()) { ... } // +1, +2 nesting, +1 for &&
good: for (Order o : orders) { if (needsReview(o)) { review(o); } }   // +1, +2
      private boolean needsReview(Order o) {
          return o.isOpen() && o.total() > limit && o.isRush();          // +1
      }
```

## Limits
A flat `switch` or `if`/`else if` ladder over a closed set of cases with no nesting scores low and is not flagged for its length. Generated code, an `equals`/`hashCode` implementation, and a method the project context exempts ("parser state machines accepted up to 40") are out of scope. A threshold declared in the project context replaces 15.

## Validator
On the triggered hunk locate each method the added lines belong to and open the file to read the whole method. Count +1 for each `if`, `else if`, `else`, `?:`, `switch`, `for`, `while`, `do`, `catch`, labelled `break`/`continue`, recursive call, and each run of `&&` or `||` (a change of operator starts a new run); then add the nesting depth of each `if`, `?:`, `switch`, `for`, `while`, `do` and `catch` that sits inside other control structures — `else`, `else if`, operator runs, labelled jumps and recursive calls take no nesting increment. Validator question: **does the count for this method exceed 15?** Yes → flag with the count.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: MNT-05`, severity minor, `file`, `symbol`, `code` = the method signature and its deepest nested block quoted verbatim from the diff, `fix` = the extracted helper or guard clause that brings the count under 15, `rationale` naming the count and the nesting that drives it).

## Source
SonarSource `java:S3776` "Cognitive Complexity of methods should not be too high" — "Cognitive Complexity is a measure of how hard the control flow of a method is to understand. Methods with high Cognitive Complexity will be difficult to maintain" (rule text from the `sonar-java` 6.15.1 plugin resources; the default threshold of 15 is `CognitiveComplexityMethodCheck.DEFAULT_MAX` in the `sonar-java` check source). Muñoz Barón, Wyrich, Wagner, "An Empirical Validation of Cognitive Complexity as a Measure of Source Code Understandability", ESEM 2020, arXiv:2007.12520, DOI 10.1145/3382494.3410636 — the three counting rules (no increment for shorthand structures; an increment per break in linear flow; an increment per level of nesting) and the meta-analysis result. Campbell, "Cognitive Complexity — A new way of measuring understandability", SonarSource white paper 2018 — the counting specification.

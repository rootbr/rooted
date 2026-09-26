---
title: A method's cyclomatic complexity stays at or below 10, counting decision points plus one
rule_id: MNT-06
domain: maintainability
triggers: ['\bif\s*\(', '\bfor\s*\(', '\bwhile\s*\(', '\bswitch\s*\(', '\bcase [^:]+[:-]', '\bcatch\s*\(', '&&|\|\|']
scope: file
check_kind: semantic
severity_default: minor
---

# A method's cyclomatic complexity stays at or below 10, counting decision points plus one

## Thesis
Every method the diff adds or extends has a cyclomatic complexity of at most 10: one for the method entry plus one for each decision point — `if`, `else if`, `?:`, `switch`, each `case`, `for`, `while`, `do`, `catch`, and each `&&` or `||` — so that the method's independent paths can be enumerated and tested.

## Rationale
The count equals the number of linearly independent paths through the method, which is the number of test cases needed to cover its branches; the measure's original paper proposes ten as a reasonable, though not magical, upper limit, and the Java analyzers ship that default (Checkstyle `CyclomaticComplexity` max 10, PMD `CyclomaticComplexity` method report level 10, SonarSource S1541 threshold 10). Above it, the decision logic concentrated in one method is hard to read and change, and the tests that would cover every path are rarely written.

## Example
```java
bad:  int fee(Order o) {
          if (o.isRush()) { ... } else if (o.isBulk() && o.total() > 100) { ... }
          switch (o.region()) { case EU: ... case US: ... case APAC: ... default: ... }
          for (Item i : o.items()) { if (i.fragile()) { ... } }
          return o.isGift() ? gift : base; }                                        // 11
good: int fee(Order o) { return baseFee(o) + regionFee(o.region()) + handlingFee(o.items()); }
```

## Limits
`equals` and `hashCode` implementations, generated code, and a flat `switch` over an enum whose cases each delegate are not worth a finding. A threshold declared in the project context replaces 10.

## Validator
On the triggered hunk locate each method containing added lines and open the file to read it whole. Count 1 + the number of `if`, `else if`, `?:`, `switch`, `case`, `for`, `while`, `do`, `catch`, `&&` and `||`. Validator question: **does the count exceed 10?** Yes → flag with the count.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: MNT-06`, severity minor, `file`, `symbol`, `code` = the method signature and its densest decision block quoted verbatim from the diff, `fix` = the extracted methods that split the decision logic, `rationale` naming the count and the paths that go untested).

## Source
McCabe, "A Complexity Measure", IEEE Transactions on Software Engineering SE-2(4), 1976, DOI 10.1109/TSE.1976.233837 — the measure and the upper bound of 10. Checkstyle `CyclomaticComplexity` — "The complexity is equal to the number of decision points + 1", `DEFAULT_COMPLEXITY_VALUE = 10`. PMD `CyclomaticComplexity` — "Concentrating too much decisional logic in a single method makes its behaviour hard to read and change", `methodReportLevel` default 10. SonarSource `java:S1541` "Methods should not be too complex" — "Complex code … will in any case be difficult to understand and therefore to maintain", `equals`/`hashCode` exempt (rule text from the `sonar-java` 6.15.1 plugin resources).

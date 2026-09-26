---
title: An invariant names its forbidden state as a construct an added line can show, not as a consequence
rule_id: META-02
domain: meta
triggers: ['^\s*\d+[.]\s+\*\*', 'Violation\s*:', '[Ii]nvariant', '\bmust not\b|\bnever\b']
scope: file
check_kind: mechanical
severity_default: minor
---

# An invariant names its forbidden state as a construct an added line can show, not as a consequence

## Thesis
The `Violation:` clause of an invariant — or, where the clause is absent, its rule — names the state the reviewer scans for as something a line of Java can exhibit: a call, an expression, an import, a dependency, an annotation, a value out of range. A clause that names only the consequence (`latency regressions`, `inconsistency`, `heap churn`), or that is missing, gives the reviewer a goal and no test.

## Rationale
A run violates an invariant when the program's behaviour fails the stated property, and whether it fails is decidable only against a property concrete enough to check. The invariants that guide a repair come in two sets — the good patterns a correct run keeps and the bad patterns that produce the defect — and a finder works from the second: it recognises the bad pattern in the change and names it. An architecture rule reaches the same shape when it is written as the forbidden dependency itself — no class in one package depends on a class in another — and evaluated against the imported classes. A consequence describes what happens after the violation, at runtime, in production; a reviewer holding a diff cannot see it, so the clause must name the construct that precedes it.

## Example
```java
bad:  7. **onEvent is allocation-free**: Keep the dispatcher lean.
         Violation: latency regressions.
good: 7. **onEvent is allocation-free**: `Dispatcher#onEvent` executes no `new`,
         autoboxing, varargs spread or `String.format`. Violation: any `new`
         expression, boxed-primitive call or `String.format` inside
         `Dispatcher#onEvent`.
```

## Limits
Applies to the clause a reviewer would test an added line against. An invariant whose rule already names the construct (`calls no Socket#read`) and whose `Violation:` adds the consequence is complete; the finding is for an invariant where neither part names a construct. An invariant about a runtime property with no lexical form — a p99 target — names the measurement instead, and that is its forbidden state.

## Validator
Open the config at HEAD and take each numbered invariant the diff adds or changes. Read its `Violation:` clause and its rule. List what each names: a call, expression, import, dependency, annotation, value or measurement — versus a consequence (a regression, an outage, "inconsistency", "churn") or nothing. Validator question: **does neither the rule nor the `Violation:` clause name a construct or measurement that an added line could be matched against?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: META-02`, severity minor, `file` = the config path, `symbol` = `Inv <N>` for the invariant's number, `code` = the invariant line quoted verbatim from the diff, `fix` = the invariant rewritten with a `Violation:` clause naming the construct, `rationale` naming the consequence the clause gives in place of a testable state).

## Source
arXiv:2312.16652 (FASE 2024) §1–2 — repair is driven by two inferred specifications, the good patterns "required for a run to be successful" and ϕ_violated, "the set of likely suspicious invariants (bad patterns) that result in the bug"; a run is faulty when it fails the stated property (Definition 1); "It is important to categorize and distinguish inferred patterns (invariants) into good and bad patterns … to identify … violated invariants to be repaired when modifying code". ArchUnit user guide §What to Check — a rule written as the forbidden dependency, `noClasses().that().resideInAPackage("..source..").should().dependOnClassesThat().resideInAPackage("..foo..")`, evaluated against imported classes. The paper's patterns are runtime predicates over program state, which the card admits as measurements; the construct form follows the ArchUnit rule shape.

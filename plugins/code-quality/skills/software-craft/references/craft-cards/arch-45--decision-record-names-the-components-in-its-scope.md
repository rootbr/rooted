---
title: A decision record of an architectural change makes explicit which components, connectors or other structural elements its decision applies to, or that it governs the whole system
rule_id: ARCH-45
domain: architecture
step: [design, document]
applies_to: [prose]
triggers: ['signal:added_file', '(?i)^\s*#{2,3}\s+(status|context( and problem statement)?|decision( outcome)?|considered options|consequences)\s*$', '(?i)^\s*#\s+(ADR[-\s]?\d*|\d{1,4}[.:]?)\s*\S']
scope: file
check_kind: semantic
severity_default: suggestion
---

# A decision record of an architectural change makes explicit which components, connectors or other structural elements its decision applies to, or that it governs the whole system

## Thesis
A decision record that a change adds for an architectural decision makes the scope of that decision explicit. It does so, for instance, by calling out the structural elements the decision affects — components, connectors and the like — or by pointing at them. A record whose decision adopts a technology, pattern or constraint while naming, pointing at or bounding no part of the system leaves its scope unstated.

## Rationale
An architecture decision affects elements of the architecture description and pertains to one or more concerns, and making it may raise new concerns. Recommendations for documenting a decision list the affected elements of the description beside its statement, the concerns it pertains to, its owner, its rationale, its forces and constraints, its assumptions, and the alternatives considered with their potential consequences. Decisions can be organized by the element they affect, as well as by concern or by architectural level. Another decision template carries a field that lists the architecture, design or scope documents a decision impacts. Filing a decision under an element requires its record to name or point at that element, so a record that names only a technology and points at no element is found under none.

## Example
```java
bad:  String adr = """
          # ADR-7 Adopt PostgreSQL
          ## Decision
          We will use PostgreSQL.
          """;
good: String adr = """
          # ADR-7 Adopt PostgreSQL for the order service
          ## Decision
          order-service and order-history-lib move to PostgreSQL; billing-service keeps its store.
          """;
```

## Limits
The rule asks for an explicit scope, and naming elements is one instance of it: a record that states its decision governs the whole system meets the rule. Pointing meets it as well as naming, so a link to a component diagram, a module list or a scope document that identifies the elements suffices. A component here is a unit of release, build or deployment — a module artifact, a library, a service; a choice confined to one class, import or routine is a design decision outside this rule. A decision about the team's way of working — a commit or review convention, keeping a decision log — governs no part of the system and stays outside the rule too. The rule reaches the decision record a change adds; whether a change needs a record at all, the record's other sections, design documents and change descriptions fall under other rules.

## Validator
Open each file the change adds that carries decision-record headings — Status, Context, Decision, Considered Options, Consequences — or a numbered record title. Read the record whole, the context and decision sections first. List every structural element it names or links to: a component, service, library, module artifact, connector or interface, or a sentence that bounds the decision to the whole system or to a named subsystem. Identify what the decision adopts, removes or constrains, and stop without a finding when that choice is confined to one class, import or routine, or governs the team's way of working and no part of the system — a commit or review convention, the decision log itself. Validator question: **Does the record state a decision while naming, pointing at or bounding no structural element it applies to?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: ARCH-45`, severity suggestion, `file`, `symbol` = the record's title, `code` = the decision statement quoted verbatim from the diff, `fix` = the same statement rewritten to name or link the components and connectors it applies to, or to state that it governs the whole system, `rationale` = names the decision whose scope the record leaves unstated and the elements a reader cannot file it under).

---
title: Behaviour that computes from an object's fields lives on that object, not in another class that reads them through getters
rule_id: MNT-39
domain: maintainability
triggers: ['(\w+)[.]get\w+\(\)[^;]*\1[.]get\w+\(\)[^;]*\1[.]get\w+\(\)', '(\w+)[.]get\w+\(\)[^;]*\1[.]get\w+\(\)', 'class \w+(Ops|Utils|Helper|Calculator|Util)\b', '@Data\b|@Getter\b|@Setter\b']
scope: file
check_kind: semantic
severity_default: minor
---

# Behaviour that computes from an object's fields lives on that object, not in another class that reads them through getters

## Thesis
A method that reads two or more fields of another object (through its getters or record accessors) to compute a result about that object — a total from its lines, a conflict from its start and end, a status from its flags — is a method of that object; a class that consists of fields with getters and setters and no behaviour, while other classes compute from its data, gains that behaviour.

## Rationale
When the computation sits outside the object, every rule about the object's state is enforced in the classes that read it, and a change to the representation — a field renamed, a unit changed, a derived field added — breaks each of them; the data class exposes its internals to make that possible, so encapsulation is gone and the design is brittle. The detection strategy names the shape: a data class reveals most of its state and has few operations of its own, and its behaviour is defined elsewhere. Moving the method to the data puts the rule next to the state it depends on.

## Example
```java
bad:  class ReservationOps {
          boolean conflicts(Reservation a, Reservation b) {
              return !a.getEnd().isBefore(b.getStart()) && !b.getEnd().isBefore(a.getStart()); } }
good: record Reservation(Instant start, Instant end) {
          boolean conflictsWith(Reservation o) { return !end.isBefore(o.start) && !o.end.isBefore(start); } }
```

## Limits
A DTO that crosses a boundary (JSON, a JPA entity, a message) is a data holder by design, and its mapping code reads it legitimately. A method that combines data from several objects of different types (a pricing policy over an order and a customer) has no single home and stays in a service. A class the project context names as an anaemic model by policy is out of scope. Framework-mandated accessors do not make a class a data class on their own.

## Validator
On the triggered hunk find each method that calls two or more accessors of the same parameter or field to compute a result about it. Open the file, and the accessed type where the diff shows it, to see whether the computation belongs to that type. Validator question: **does this method compute a fact about another object from that object's data alone?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: MNT-39`, severity minor, `file`, `symbol`, `code` = the method quoted verbatim from the diff, `fix` = the method moved onto the type, `rationale` naming the representation change that would break the external computation).

## Source
PMD `DataClass` — "Data Classes are simple data holders, which reveal most of their state, and without complex functionality. The lack of functionality may indicate that their behaviour is defined elsewhere, which is a sign of poor data-behaviour proximity. By directly exposing their internals, Data Classes break encapsulation, and therefore reduce the system's maintainability and understandability … Refactoring a Data Class should focus on restoring a good data-behaviour proximity. In most cases, that means moving the operations defined on the data back into the class"; detected by a weight-of-class under 1/3 with many accessors. PMD `GodClass` — ATFD, "a measure of how much external data the class uses", a class-level metric. Caveat: the "two or more fields" threshold is this card's own reading of the shape; PMD's detection is class-level and states no per-method threshold.

---
title: A class does one job and is not a God class whose methods fall into groups that share no fields
rule_id: MNT-11
domain: maintainability
triggers: ['^\s*(public|protected|private)\s+(static\s+)?[\w<>\[\], ?]+\s+\w+\s*\(', '^\s*(public|final|abstract|\s)*class\s+\w+']
scope: file
check_kind: semantic
severity_default: minor
---

# A class does one job and is not a God class whose methods fall into groups that share no fields

## Thesis
A class the diff creates or grows has one responsibility: its methods use a common set of fields, and it does not accumulate unrelated groups — persistence plus notification plus search — that would each change for a different reason. The God-class shape is a class that is large (weighted method count at or above 47), leans on foreign data (more than five accesses to other objects' fields or getters) and is incohesive (tight class cohesion under one third); read by hand, low cohesion shows as methods that split into groups of several methods each, the groups touching disjoint fields, and such a class is split along those groups.

## Rationale
A class that gathers several responsibilities changes whenever any of them changes, so it is edited often, by many people, for unrelated reasons, and each edit risks the other responsibilities; Blob classes have been measured more change-prone than other classes, and classes in mutated anti-patterns more fault-prone. The tool detection strategy names the shape: weighted method count at or above 47, more than five accesses to foreign data, and tight class cohesion under one third — many complex methods that share little state and lean on other objects' data. A long constructor parameter list is the same smell seen from the constructor.

## Example
```java
bad:  class UserService { User load(String id); List<User> search(Query q); void sendWelcome(User u);
                          void sendReset(User u); void block(User u); List<User> blocked(); /* 300+ lines, 12 fields */ }
good: class UserDirectory  { User load(String id) { ... } List<User> search(Query q) { ... } }
      class UserNotifier   { void sendWelcome(User u) { ... } void sendReset(User u) { ... } }
      class UserModeration { void block(User u) { ... } List<User> blocked() { ... } }
```

## Limits
A facade or an application service that only delegates to collaborators is broad by design and cohesive in that role. A JPA entity with many fields and accessors, a configuration-properties class and a DTO are data holders, not God classes. A class the project context names as a deliberate aggregate is tolerated. A class large but with one coherent field set is not this finding.

## Validator
Open the file at HEAD. List the instance fields and, for each method, the fields it reads or writes; group methods by shared fields, and count a group only when it holds several methods — one utility method that shares no field is not a group. Count the accesses to other objects' fields or getters. Validator question: **does the class now show the God-class shape (weighted method count ≥ 47, foreign-data accesses > 5, cohesion < 1/3), or do its methods fall into two or more groups of several methods each that touch disjoint fields?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: MNT-11`, severity minor, `file`, `symbol`, `code` = the class declaration and one method from each disjoint group quoted verbatim from the diff, `fix` = the split classes, `rationale` naming the groups and the reasons they change).

## Source
PMD `GodClass` — "God classes do too many things, are very big and overly complex. They should be split apart to be more object-oriented"; detection thresholds `WMC_VERY_HIGH = 47`, `FEW_ATFD_THRESHOLD = 5`, `TCC_THRESHOLD = 1/3` in the rule source. Kermansaravi, Rahman, Khomh, Jaafar, Guéhéneuc, "Investigating Design Anti-pattern and Design Pattern Mutations and Their Change- and Fault-proneness", arXiv:2104.00058 — Blob/God Class "a class that is too large and not cohesive"; Blob classes more change-prone (relaying Olbrich et al.), classes in mutated anti-patterns more fault-prone. Spring Framework reference, Constructor-based DI — "a large number of constructor arguments is a bad code smell, implying that the class likely has too many responsibilities".

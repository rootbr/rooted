---
title: A change made for one requirement edits the module that owns the requirement and forces no matching edits in modules that serve other concerns
rule_id: DSN-08
domain: design
step: [design, implement, review]
applies_to: [universal]
triggers: ['signal:duplicate_block', '^\s*(case\s+[\w.''"*]|[A-Z]\w*(::|[.])[A-Z]\w*\s*(=>|->|:)|"[^"]*"\s*=>)|\b(elif|else\s+if)\b.*((===?|\bis\b|\bin\b)\s*[\w''"(\[]|[.]equals(IgnoreCase)?\()']
scope: callers
check_kind: semantic
severity_default: major
---

# A change made for one requirement edits the module that owns the requirement and forces no matching edits in modules that serve other concerns

## Thesis
A change made for one requirement, such as a new case of a business rule or a changed record format, is confined to the module that owns that requirement and has minimal impact on the modules that serve other concerns. The requirement's knowledge, such as the list of its cases or the layout of its records, lives in that one module, and the modules that need it call the owner instead of each depending on that knowledge directly. A diff in which one requirement appears as many little matching edits in several modules that serve other concerns is a symptom that the requirement's knowledge may have spread beyond its owner, and a symptom may or may not indicate a design problem.

## Rationale
When a design decision that is likely to change, such as the storage format of shared data, is used by every module, a change to that decision results in changes in every module; when one module hides the decision from all the others, any change to it can be confined to that module, even though that module is used in almost every action of the system. A product-quality model names the property modularity: the capability of a product to limit changes to one component from affecting other components. One architecture anti-pattern detectable from a project's structural relationships and revision history is the modularity violation group, modules that change in tandem even though they have no apparent structural dependencies. Across 19 large-scale projects, files involved in such anti-patterns were more error-prone and change-prone, the more anti-patterns a file was involved in the more error-prone and change-prone it was, and every anti-pattern contributed, with unstable interfaces and crossings contributing the most by far. Shown smells detected from change history, twelve developers of four open-source projects recognized 17 of 24 instances (71%) as design or implementation problems; where a change to one class triggered many little changes to several other classes, 75% of the developers who identified the instance favoured refactoring the class. These results are associations, and a smell found this way is a symptom that may or may not indicate a design problem.

## Example
```typescript
bad:  // adding the plan "team" edits a switch in each of three modules
        case "team": return 50;       // billing.ts
        case "team": return 10;       // seats.ts
        case "team": return "Team";   // labels.ts
good: const plans = { basic: { price: 10, seats: 1, label: "Basic" },   // plans.ts owns every plan
                      team: { price: 50, seats: 10, label: "Team" } };
      type Plan = keyof typeof plans;
      const price = (plan: Plan): number => plans[plan].price;          // billing.ts
      const seats = (plan: Plan): number => plans[plan].seats;          // seats.ts
      const label = (plan: Plan): string => plans[plan].label;          // labels.ts
```

## Limits
Modules that each own one variant of a shared role can change together and still be correctly separate: two trackers that each clean up a data connection for a different protocol changed together, and placing them in one class only to isolate the change could create a class managing heterogeneous responsibilities. A group of modules the project deliberately treats as one unit can be one owner: a developer judged one tightly coupled group of classes best viewed as one unit, with no design problem from that perspective. Edits that only carry a renamed or re-signed symbol into the code that calls it, a mechanical migration, or a dependency upgrade implement no requirement of their own and are outside this rule. A tolerance the project context states for a named group of modules rejects the finding.

## Validator
Name the requirement each added hunk serves: a new case, a new or changed field, a changed format or rule. Group the hunks of different files by requirement, and read the matched lines (a new case label, a new match arm, a new comparison branch) and any duplicated block as candidate copies of one piece of knowledge. For a requirement whose matching edits reach several modules, open those modules and search the repository for the callers of the changed symbols: decide which module owns the requirement, which concern each other module serves, count the modules beyond the owner that carry a matching edit, and check whether they call one owner for the requirement or each depend on its knowledge directly. Skip modules that each implement one variant of a shared role, a group the project treats as one unit, edits that only carry a renamed or re-signed symbol to its callers, mechanical migrations, dependency upgrades, and a group the project context tolerates. Validator question: **does the diff carry one requirement's knowledge, such as the same new case, field or format detail, as matching edits in several modules that serve other concerns, where one module could own it and the others call it?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: DSN-08`, severity major, `file`, `symbol`, `code` = one matching edit from each module, quoted verbatim from the diff with its file path, `fix` = the requirement's knowledge held in one owning module, as a table, a type or a routine, that the other modules call, in the file's language, `rationale` = the requirement, the modules it reached and the concern each serves).

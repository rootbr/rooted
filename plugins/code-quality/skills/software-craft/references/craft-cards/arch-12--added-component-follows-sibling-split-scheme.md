---
title: A component a change adds follows the split scheme its sibling components follow, whether by feature, by layer or by API and implementation, rather than starting a second scheme beside them
rule_id: ARCH-12
domain: architecture
step: [design, review]
applies_to: [universal]
triggers: ['\b(persistence|repositories|controllers|services|models|entities|adapters|infrastructure|handlers|dao)\b', 'signal:added_file']
scope: callers
check_kind: semantic
severity_default: suggestion
---

# A component a change adds follows the split scheme its sibling components follow, whether by feature, by layer or by API and implementation, rather than starting a second scheme beside them

## Thesis
Where the existing components at one level of a project follow one split scheme, a component that a change adds at that level follows the same scheme. Workable schemes include API versus implementation, front end versus back end, core business logic versus UI, vertical feature slices, inputs to source generation versus their consumers, and groups of closely related classes. A layer-named component therefore joins layer-named siblings, and a feature component joins feature siblings.

## Rationale
How best to split source into components varies with every build, because it depends on that build's particulars, and each of the schemes above can work well and make cohesive components. The specific scheme matters less than a split that is logical and consistent, and a component added under a second scheme is the step that turns a consistent split into a mixed one. An official reference layout states the placement its scheme gives new code: a class needed only by one feature module should remain within that module, and a class that is not should be placed into an appropriate core module.

## Example
```rust
bad:  use billing::{Invoice, InvoiceStore};    // feature crate
      use orders::{Order, OrderStore};         // feature crate
      use persistence::ShipmentStore;          // added: a layer crate for one feature
good: use billing::{Invoice, InvoiceStore};    // feature crate
      use orders::{Order, OrderStore};         // feature crate
      use shipping::{Shipment, ShipmentStore}; // added: a feature crate
```

## Limits
Different levels of one project can follow different schemes. The official reference layout splits its top level by role into an application module, feature modules and core modules, and splits each feature into an api submodule holding navigation keys and an impl submodule holding everything else. The comparison therefore runs against the siblings at the level the new component joins. The same layout names the app module, which holds the scaffolding classes that bind the rest of the codebase and depends on all feature modules, as a module type of its own, and lists sync, benchmark and test modules and a catalog application as miscellaneous modules, the fourth of its module types; such an application module and such auxiliary components fall outside the comparison, both as the added component and among the siblings. A component that holds code more than one sibling needs belongs with the components that hold shared code, because the same layout keeps a class that one feature module needs inside that module and places any other class into a core module, a common library module for code shared between the other modules; such a component is compared with the group where the project keeps its shared components, and falls outside the comparison only where the project keeps no such group. The first split of a single component has no siblings to follow and uses whatever natural boundaries the codebase has. The rule takes no side between splitting by layer and splitting by feature, since both appear among the workable schemes. A change whose stated subject is moving the project from one scheme to another is outside the rule, because the choice of scheme depends on the particulars of the build.

## Validator
In the hunk, find each added component: a new entry in a component list (a settings include, a workspace members list, a module element, a workspaces entry) or an added file that opens a new package or module directory. Open the component list at the card's scope and list the siblings at the level the new component joins, leaving out an application module that holds the entry point and the scaffolding binding the other components, and any auxiliary component such as a benchmark, a test fixture or a demo application. Name the scheme those siblings follow from their names and contents, then name the scheme of the added component from its name and the files it holds. When the added component holds code that more than one sibling uses, compare it with the group where the project keeps its shared components: it departs from the scheme when it sits outside that group, and is skipped when the project keeps no such group. Skip the component when the siblings already mix schemes, when it is itself such an application module or auxiliary component, or when the change states that it moves the project to another scheme. Validator question: **Do the siblings at the level where the change adds a component follow one split scheme that the added component departs from?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: ARCH-12`, severity suggestion, `file`, `symbol`, `code` = the line of the diff that adds the component, quoted verbatim, `fix` = the component placed under the siblings' scheme — the content moved into the sibling it belongs to, into the project's group of shared components when more than one sibling uses it, or a new component named and cut the way its siblings are — in the file's language, `rationale` = names the siblings' scheme, the scheme the added component starts and the level both sit at).

## Source
- Build-tool user manual, 'Best Practices for Structuring Builds', § Modularize Your Builds, Explanation (gradle/gradle, master, platforms/documentation/docs/src/docs/userguide/best-practices/best_practices_structuring_builds.adoc) (fetched): "Exactly how to best split your source varies with every build, as it depends on the particulars of that build. Here are some common patterns we found that can work well and make cohesive projects: - API vs. Implementation - Front-end vs. Back-end - Core business logic vs. UI - Vertical slices (e.g., feature modules each containing UI + business logic) - Inputs to source generation vs. their consumers - Or simply closely related classes. Ultimately, the specific scheme matters less than ensuring that your build is split logically and consistently." Same section: "structure your build into multiple projects from the start using whatever natural boundaries exist in your codebase."
- Official reference application, 'Modularization learning journey', § Module types (android/nowinandroid, main, docs/ModularizationLearningJourney.md) (fetched): "The Now in Android app contains the following types of modules: The `app` module … Feature modules … Core modules … Miscellaneous modules … For example, `sync`, `benchmark` and `test` modules, as well as `app-nia-catalog`"; "Feature modules aren't Gradle modules themselves, they are split into two submodules: `api` - contains navigation keys, `impl` - contains everything else"; "If a class is needed only by one feature module, it should remain within that module. If not, it should be placed into an appropriate `core` module."; "These are common library modules containing auxiliary code and specific dependencies that need to be shared between other modules in the app."; § The `app` module: "This contains app level and scaffolding classes that bind the rest of the codebase" and "The `app` module depends on all `feature` modules and required `core` modules."
- Caveat: both sources come from one build ecosystem and state consistency as guidance without a measurement; the card applies the same structural claim to any build system's component list.

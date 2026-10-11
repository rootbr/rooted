---
title: Only the composition root references the concrete types of an infrastructure component, and the rest of the component that holds the root reaches infrastructure through interfaces the core declares, never by instantiating its types or calling them statically
rule_id: ARCH-27
domain: architecture
step: [design, implement, review]
applies_to: [universal]
triggers: ['\b(?:new\s+(?:\w+[.])*|New)\w*(?:Repository|Gateway|Client|Dao|DbContext|Store|Adapter|Sender|Publisher)\s*[(<]|\b[A-Z]\w*(?:Repository|Gateway|Client|Dao|DbContext|Store|Adapter|Sender|Publisher)\s*(?:::|[.])\s*\w+\s*\(', '^\s*(?:return\s+|(?:(?:val|var|let|const)\s+)?\w+\s*(?::\s*[\w.<>\[\]]+\s*)?:?=\s*)(?:\w+[.])*\w*(?:Repository|Gateway|Client|Dao|DbContext|Store|Adapter|Sender|Publisher)\s*\(', '\b(?:infra|infrastructure|persistence|adapters?)\s*[.]\s*\w+\s*\(', '^\s*(?:(?:import|using|from|use)\b|\}\s*from\b|(?:\w+\s+)?"[\w.-]+/)[^;]*?\b(?:[Ii]nfrastructure|[Pp]ersistence|[Aa]dapters?)\b']
scope: file
check_kind: semantic
severity_default: minor
---

# Only the composition root references the concrete types of an infrastructure component, and the rest of the component that holds the root reaches infrastructure through interfaces the core declares, never by instantiating its types or calling them statically

## Thesis
In the component that holds the application's entry point, only the composition root — the startup code that configures the application and wires implementation types to interfaces — references the types of an infrastructure component; the rest of that component interacts with infrastructure strictly through interfaces the application core defines, and it neither instantiates an infrastructure type directly nor calls one statically.

## Rationale
At compile time the entry-point component works with the interfaces the core defines and ideally should not know about the implementation types in the infrastructure component. At run time those implementation types are required for the application to execute, so dependency injection wires them to the core's interfaces. Direct instantiation couples the code to a particular implementation. Because the code outside the composition root then holds no direct dependency on infrastructure types, implementations are easy to swap, either to facilitate testing or in response to changing application requirements.

## Example
```go
bad:  package main
      import infra "example.com/shop/infrastructure"
      func (h *OrderHandler) Place(ctx context.Context, o core.Order) error {
          return infra.NewPostgresOrderRepository(h.db).Save(ctx, o)
      }
good: type OrderHandler struct{ orders core.OrderRepository }
      func (h *OrderHandler) Place(ctx context.Context, o core.Order) error {
          return h.orders.Save(ctx, o)
      }
      // composition root, in main(): h := &OrderHandler{orders: infra.NewPostgresOrderRepository(db)}
```

## Limits
The composition root is where the references belong: the startup code that wires implementation types to interfaces is what lets dependency injection work at run time, so a framework's startup registration that performs this wiring is the composition root, and a type or routine whose collaborators the framework injects complies when it declares them by the core's interfaces. The entry-point component may reference the infrastructure component for that wiring; a container with built-in support for loading implementation types from compiled artifacts can remove the reference altogether, and the rule covers whatever references remain. The rule belongs to a layout in which the application core defines interfaces for the operations performed through infrastructure, such as data access, file system access and network calls, and infrastructure types implement them; a codebase without that split lies outside it. It governs the production code of the entry-point component alone: the infrastructure component, which implements the core's interfaces and references the core, works with those types directly, and tests, among them the integration tests of infrastructure implementations, lie outside the rule.

## Validator
Grep the hunk for a constructor, factory or static call on an infrastructure type — a name ending in Repository, Gateway, Client, Dao, Store, Adapter, Sender or Publisher, a database context, a package-qualified call on an infrastructure, persistence or adapter package — and for an import of an infrastructure package. Open the file and decide which component it belongs to; stop when it belongs to the infrastructure component, to a test, or to a component other than the one that holds the entry point. Stop when the codebase has no core that defines interfaces implemented by infrastructure types. Locate the composition root — the startup code that configures the application and wires implementation types to interfaces — and stop when the hit lies inside it. For each remaining hit, confirm that the referenced type belongs to the infrastructure component, and look in the core for the interface that covers the operation the code performs. Validator question: **Does code of the entry-point component outside the composition root instantiate, statically call or otherwise reference a type declared in the infrastructure component?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: ARCH-27`, severity minor, `file`, `symbol`, `code` = the line that instantiates, statically calls or names the infrastructure type, `fix` = the enclosing type or routine receiving the core's interface through its constructor, fields or parameters while the composition root passes in the infrastructure implementation, in the file's language, `rationale` = names the infrastructure type referenced outside the composition root, the core interface that covers the operation, and the coupling to one implementation that the reference creates).

## Source
- .NET Architecture Guide "Architect Modern Web Applications with ASP.NET Core and Azure", chapter "Common web application architectures", dotnet/docs `docs/architecture/modern-web-apps-azure/common-web-application-architectures.md` (fetched) — § UI Layer: "The user interface layer in an ASP.NET Core MVC application is the entry point for the application."; "its types should interact with infrastructure strictly through interfaces defined in Application Core. No direct instantiation of or static calls to the Infrastructure layer types should be allowed in the UI layer."; its list "UI Layer types": "Controllers", "Custom Filters", "Custom Middleware", "Views", "ViewModels", "Startup"; "The `Startup` class or _Program.cs_ file is responsible for configuring the application, and for wiring up implementation types to interfaces. The place where this logic is performed is known as the app's *composition root*, and is what allows dependency injection to work properly at run time."; its note: "In order to wire up dependency injection during app startup, the UI layer project may need to reference the Infrastructure project. This dependency can be eliminated, most easily by using a custom DI container that has built-in support for loading types from assemblies. [...] developers should limit actual references to types in the Infrastructure project to the app's composition root"; same chapter: "defining abstractions, or interfaces, in the Application Core, which are then implemented by types defined in the Infrastructure layer"; "the UI layer works with interfaces defined in the Application Core at compile time, and ideally shouldn't know about the implementation types defined in the Infrastructure layer. At run time, however, these implementation types are required for the app to execute, so they need to be present and wired up to the Application Core interfaces via dependency injection."; "Since the UI layer doesn't have any direct dependency on types defined in the Infrastructure project, it's likewise very easy to swap out implementations, either to facilitate testing or in response to changing application requirements. ASP.NET Core's built-in use of and support for dependency injection makes this architecture the most appropriate way to structure non-trivial monolithic applications."; "These interfaces include abstractions for operations that will be performed using Infrastructure, such as data access, file system access, network calls, etc."; "These services should implement interfaces defined in the Application Core, and so Infrastructure should have a reference to the Application Core project."; "Figures 5-10 and 5-11 show how tests fit into this architecture.", the Figure 5-10 caption: "Unit testing Application Core in isolation." and the Figure 5-11 caption: "Integration testing Infrastructure implementations with external dependencies."
- .NET documentation "Dependency injection guidelines", dotnet/docs `docs/core/extensions/dependency-injection/guidelines.md` (fetched) — § Design services for dependency injection: "Avoid direct instantiation of dependent classes within services. Direct instantiation couples the code to a particular implementation."
- Caveat: both sources are .NET guidance; the architecture guide states the rule for a monolith split into core, infrastructure and UI projects, and the language-neutral reading rests on that layout.

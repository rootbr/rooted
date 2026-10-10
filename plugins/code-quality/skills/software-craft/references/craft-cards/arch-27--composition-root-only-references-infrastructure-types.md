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

---
title: Code is not split into modules that every client must import together to use either one meaningfully
rule_id: DSN-13
domain: design
step: [design, refactor, review]
applies_to: [universal]
triggers: ['signal:added_file', '^\s*package\s+[\w.]+\s*;?\s*$', '^\s*(pub(\([\w:]+\))?\s+)?(mod\s+\w+\s*;|use\s+(crate|super|self)::)', '(\bfrom\s+|\b(require|import)\(\s*)[''"][.]{1,2}/', '^\s*from\s+[\w.]+\s+import\b|^\s*import\s+(static\s+)?\w+([.][\w*]+)+', '^\s*(import\s+)?(?!return\s)(\w+\s+|[.]\s+)?"[\w.~-]+/[\w./~-]+"\s*$']
scope: callers
check_kind: semantic
severity_default: minor
---

# Code is not split into modules that every client must import together to use either one meaningfully

## Thesis
When two modules cover closely related topics and a client must import both to use either of them in any meaningful way, combining them into one module is usually right.

## Rationale
Code inside a module can use the identifiers that the module does not export. Placed in one module, a few related types whose implementations are tightly coupled can therefore keep that coupling among themselves without polluting the module's public interface with those details. A good test for that coupling imagines a hypothetical client of two modules that cover closely related topics: if the client must import both modules to use either of them in any meaningful way, combining the two is usually the right thing to do. When client code is likely to need values of two different types to interact with each other, having both types in one module may be convenient for that client.

## Example
```typescript
bad:  export interface Handle { id: number }                  // open.ts
      export function open(path: string): Handle { ... }
      import { Handle } from "./open";                        // close.ts
      export function close(handle: Handle): void { ... }
      const handle = open(path); close(handle);  // client imports both modules
good: interface Handle { id: number }                         // file.ts
      export function open(path: string): Handle { ... }
      export function close(handle: Handle): void { ... }
      const handle = open(path); close(handle);  // client imports one module
```

## Limits
The rule asks for no single large module: putting a whole project in one module would likely make that module too large, and a conceptually distinct part can be easier to use in its own small module. The test reaches two modules on closely related topics; a client that imports two modules on unrelated topics is no finding, nor is a module that some client uses in a meaningful way without the other. A split that the project context documents as a tolerance rejects the finding.

## Validator
Find the module boundary the change draws: an added file, an added package or child-module declaration, or an added import of another module of the same project. Name the two modules on either side of it, the one the change adds or moves code into and the one that code depends on or serves. Open the usages of both modules' exported names across the repository and list, for each client, which of the two it imports; where the repository holds no client yet, take the change's own usage. Mark tight coupling where a value one module returns is accepted only by the other, or where one module exports a member that only the other module uses. Skip a pair whose topics are conceptually distinct, and a module that at least one client uses in a meaningful way without the other. Validator question: **Does the change leave two modules on closely related topics that a client must import together to use either of them in any meaningful way?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: DSN-13`, severity minor, `file`, `symbol`, `code` = the added module declaration or import line from the diff that draws the boundary between the two modules, `fix` = the two modules combined into one, with the members that only the other module used no longer exported, in the file's language, `rationale` = a client that must import both modules and what it cannot do with either alone).

## Source
- Google Go Style Guide, best practices, "Package size" (google/styleguide, `go/best-practices.md`): "If *client code* is likely to need two values of different type to interact with each other, it may be convenient for the user to have them in the same package. Code within a package can access unexported identifiers in the package. If you have a few related types whose *implementation* is tightly coupled, placing them in the same package lets you achieve this coupling without polluting the public API with these details. A good test for this coupling is to imagine a hypothetical user of two packages, where the packages cover closely related topics: if the user must import both packages in order to use either in any meaningful way, combining them together is usually the right thing to do. [...] All of that being said, putting your entire project in a single package would likely make that package too large. When something is conceptually distinct, giving it its own small package can make it easier to use." (fetched)
- Module-private members in other languages: Rust Reference, "Visibility and privacy", `vis.access` (rust-lang/reference, `src/visibility-and-privacy.md`): "If an item is private, it may be accessed by the current module and its descendants. These two cases are surprisingly powerful for creating module hierarchies exposing public APIs while hiding internal implementation details."; TypeScript Handbook, "Modules" (microsoft/TypeScript-Website, `packages/documentation/copy/en/handbook-v2/Modules.md`): "variables, functions, classes, etc. declared in a module are not visible outside the module unless they are explicitly exported"; PEP 8, "Public and Internal Interfaces" (python/peps, `peps/pep-0008.rst`): "internal interfaces (packages, modules, classes, functions, attributes or other names) should still be prefixed with a single leading underscore." (fetched)

Caveat: the test and its counterweight come from the Best Practices document of Google's Go style guide, which that guide marks as neither normative nor canonical, and are guidance without a measured cost; the card applies them to the unit a client imports in each language, a package or a module.

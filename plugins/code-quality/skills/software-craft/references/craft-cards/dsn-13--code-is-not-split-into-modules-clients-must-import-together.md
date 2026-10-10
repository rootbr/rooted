---
title: Code is not split into modules that every client must import together to use either one meaningfully
rule_id: DSN-13
domain: design
step: [design, refactor]
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

---
title: A dependency a change adds from one component to another, declared in a build file or module descriptor or made by an import across components, leaves the graph of the repository's components acyclic even where no cycle runs between individual files
rule_id: ARCH-08
domain: architecture
step: [design, implement, review]
applies_to: [universal]
triggers: ['\bproject\s*\(\s*(path\s*[:=]\s*)?[''"]:', '<artifactId>[\w.\-]+</artifactId>', '(\bpath\s*=\s*|=>\s*)[''"]?[.]{1,2}/', '[''"](workspace|file|link):', '^\s*requires\s+((transitive|static)\s+)*[\w.]+\s*;', '[''"]//[\w/.\-]*(:[\w.\-+]+)?[''"]', '^\s*(import|from\s+\S+\s+import|use|using|#include|require)\b|\brequire\s*\(\s*[''"]']
scope: callers
check_kind: semantic
severity_default: major
---

# A dependency a change adds from one component to another, declared in a build file or module descriptor or made by an import across components, leaves the graph of the repository's components acyclic even where no cycle runs between individual files

## Thesis
The components of one repository, meaning its units of build or release such as build modules, workspace packages, build targets and named modules, form a directed acyclic graph. A dependency declared in a build file or module descriptor is an edge of that graph, and so is an import from one component's code into another component's code. After the change, no path of such edges, direct or transitive, leads from a component back to itself, even where the files along that path form no cycle.

## Rationale
Components that take part in a dependency cycle form a set that must be reused and released together. Build and module tools rely on this graph being acyclic. One build tool defines its depends-upon relation as inducing a directed acyclic graph over targets. Another sorts the modules of a multi-module build so that each is built before it is required, and its sorter raises a cycle-detected error. A module system fails resolution when a cycle is detected, such as one module requiring a second that requires the first. A cycle can run between components where none runs between files: a file in one folder depends on a file in a second folder, that file depends on a different file back in the first folder, and no file lies on a cycle while the two folders do. One component-level check forbids a transitive path as well as a direct one; another reports the cycle between two projects together with the chain of files that forms it. A study of six applications classified their software components into cyclic and non-cyclic ones by extended object-oriented metrics and found most defects and defective components concentrated in the cyclic ones, directly or indirectly. Its abstract does not tie those components to units of build or release. An analysis of 19 large-scale projects found files involved in architecture anti-patterns, package cycles among them, more error-prone and change-prone, and the more so the more anti-patterns a file is involved in; every anti-pattern contributed, and two others contributed the most by far.

## Example
```python
bad:  # orders/pyproject.toml declares billing = { path = "../billing" }
      # billing/invoice.py, a file of component billing
      from orders.models import Order
      def bill(order: Order) -> None: ...
good: # billing/invoice.py imports nothing from component orders
      def bill(order_id: str, amount_cents: int) -> None: ...
```

## Limits
A cycle among the files of one component is outside this rule, since a component-level cycle check permits a cycle that stays within the same component. A cycle whose path contains a pair of components that the project's configured cycle check lists as an ignored circular dependency is a documented tolerance. A call over a network between separately deployed services is neither a declared build dependency nor an import between components, so the rule does not reach it.

## Validator
Grep the hunk for added dependency declarations in build files and module descriptors (a project reference, an artifact id, a relative path dependency, a workspace or file protocol, a requires clause, a build-target label) and for added imports whose target lives under another component's source root. Map each touched file to its component: the build module, workspace package, build target or named module whose root contains it. For every new edge from component A to component B, open B's build file or module descriptor and the imports in B's code that reach other components, and follow those edges transitively from B. Skip a cycle whose path contains a pair the configured cycle check lists as ignored, a network call between services, and a cycle that stays among the files of one component. Validator question: **Does an edge this change adds from component A to component B close a path of declared dependencies or cross-component imports, direct or transitive, that leads from B back to A?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: ARCH-08`, severity major, `file`, `symbol`, `code` = the added dependency declaration or cross-component import line, verbatim, `fix` = the edge that closes the cycle removed, with the code it needed moved into a component both sides may depend on or replaced by plain values or by an interface that the depending component of that edge owns and the other component implements, in the file's language, `rationale` = names the cycle as its chain of components with the file that makes each edge, and that the components on it must be built, reused and released together).

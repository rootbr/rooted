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

## Source
- dependency-cruiser rules reference, doc/rules-reference.md § 'scope' and example rule 'no-circular-dependency-of-modules' (fetched): "when `main/index.js` depends on `utl/helper.js` and `utl/helper.js` depends on `main/utl.js` there is no circular dependency on module level, but there _is_ one between the `main` and `utl` folders"; "This is also forbidden if the dependency is transitive. [...] if there's a cycle, it should stay within the same component".
- JDepend documentation, docs/JDepend.html § 'Identify Package Dependency Cycles' and § 'Interpreting Dependency Cycles' (fetched): "Packages participating in a package dependency cycle are in a deadly embrace with respect to reusability and their release cycle"; "The intent is to identify sets of packages that must be reused and released together."
- Bazel documentation, docs/concepts/dependencies.mdx (fetched): "The _depends upon_ relation induces a [...] (DAG) over targets, and it is called a _dependency graph_."
- Apache Maven, Guide to Working with Multiple Modules § 'Reactor Sorting', and maven-core ProjectSorter (fetched): "the reactor sorts all the projects in a way that guarantees any project is built before it is required"; "public ProjectSorter(Collection<MavenProject> projects) throws CycleDetectedException".
- OpenJDK 21, java.lang.module.Configuration, javadoc of resolve (fetched): "Resolution may fail with ResolutionException if [...] A cycle is detected, say where module m1 requires module m2 and m2 requires m1."
- Nx ESLint rule @nx/enforce-module-boundaries, enforce-module-boundaries.ts (fetched): "Circular dependency between \"{{sourceProjectName}}\" and \"{{targetProjectName}}\" detected: {{path}} [...] Circular file chain"; "!circularPathHasPair(circularPath, expandedIgnoreCircularDependencies)"; "ignoredCircularDependencies: []".
- ArchUnit User Guide, 008_The_Library_API.adoc § 'Modularization Rules' (fetched): "ModuleRuleDefinition.modules().definedByPackages(\"..example.(*)..\").should().beFreeOfCycles();".
- doi:10.1016/j.jss.2013.07.039, Journal of Systems and Software 86(12), 2013, abstract in a ScienceDirect metadata export (fetched): "Can the use of extended object-oriented metrics make us better understand the relationships among cyclic related components and their defect-proneness? [...] we extend such metrics to mine and classify software components into two groups – the cyclic and the non-cyclic ones. Next, we have performed an empirical study of six software applications. [...] most defects and defective components are concentrated in cyclic-dependent components, either directly or indirectly."
- doi:10.1109/TSE.2019.2910856, IEEE TSE 47(5), 2021, the list of the paper's six anti-patterns and the abstract, both in a published review (fetched): list item "Package cycles that violate strictly hierarchical structure"; abstract "Through our analyses of 19 large-scale software projects [...] files involved in these architecture anti-patterns are more error-prone and change-prone; 2) the more anti-patterns a file is involved in, the more error-prone and change-prone it is; and 3) while all of our defined architecture anti-patterns contribute to file's error-proneness and change-proneness, Unstable Interface and Crossing contribute the most by far."
- Caveat: the two studies measure files and components inside systems and report associations with defects and changes; the binding of build and release components rests on the tool and module-system documentation.

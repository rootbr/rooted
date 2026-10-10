---
title: A component published for others to depend on reaches each component it reuses through a released version, never only through a local path, a git or URL reference, or a replace, patch or override directive that its consumers' builds ignore
rule_id: ARCH-02
domain: architecture
step: [implement, review]
applies_to: [build-config, library]
triggers: ['^\s*(replace\b|[\w.~-]+(/[\w.~-]+)+(\s+v[\w.+-]+)?\s*=>)', '^\s*\[(patch|replace)[.\]]', '^\s*[\w-]+\s*=\s*\{[^}]*\b(path|git)\s*=', '["''](file|link|portal):', '@\s*[\w.+-]+://|^\s*-e\s+[.]{0,2}/']
scope: file
check_kind: semantic
severity_default: major
---

# A component published for others to depend on reaches each component it reuses through a released version, never only through a local path, a git or URL reference, or a replace, patch or override directive that its consumers' builds ignore

## Thesis
A component published for other components to depend on, by a registry upload or a version-control tag, names each component it reuses by a released version, publishing the reused component first as a component of its own when it has no released version yet. A dependency named only by a local path, only by a direct file or URL reference, or only through a replace, patch or override directive fails that condition: crates.io refuses a local path in a published component and the npm documentation advises against one there, crates.io and PyPI refuse a direct URL reference as well, and an override directive takes effect only in the root build, so a consumer that compiles the component as a dependency ignores it. A local path paired with the registry version that the published manifest carries meets the rule.

## Rationale
A registry guards the edge at upload. crates.io does not permit a crate whose dependency is given only by a path and does not allow a published package to depend on code outside crates.io except through a development dependency; PyPI's upload check rejects a distribution whose metadata declares a direct reference, a requirement written as a name, an `@` and an explicit URL. The npm documentation places a local path dependency in local offline development and tests and says it should not be used when publishing to the public registry, and PEP 440 calls direct references a tool for software integrators rather than publishers. Override directives are confined to the root build: a replace directive applies only in the main module and is ignored in other modules, patch and replace settings count only in the workspace root manifest and are ignored in dependencies, and npm overrides count only in a project's root package file. A component that relies on its own override is therefore built by its consumers without it; for the replace directive, the confinement is what lets the main module keep complete control over its own build without being subject to complete control by its dependencies. In the path-plus-version form, the path serves the local build, which checks the version against the local copy, and the published manifest uses the registry version.

## Example
```python
bad:  setup(name="billing", version="2.1.0",
            install_requires=["ledger @ file:///home/dev/ledger"])
good: setup(name="billing", version="2.1.0",
            install_requires=["ledger>=1.4,<2"])
```

## Limits
An override, replace or patch directive at the root of an application or service that no other component depends on takes effect there, since these directives apply in the main module or the workspace root; the rule reaches only a component published for others to depend on. A direct reference or a local path in the requirements of an application that no registry publishes is the integrator use PEP 440 assigns direct references to, and npm names local offline development and tests as the place of a local path. A development dependency lies outside the rule where the registry exempts it, as crates.io does. A published package may also dictate a dependency's resolution by pinning the dependency or by bundling it into its own published artifact, both of which npm documents for that purpose; either meets the rule when the dependency's own entry names a released version, and a bundled dependency whose entry names only a local path fails the rule like any other local path. The rule reads the dependency entries of a published component's manifest; the placement of classes between components and the imports inside one component lie outside it.

## Validator
Grep the hunk for a dependency named by a local path or a git source, a `file:`, `link:` or `portal:` specifier, a direct `@ <url>` reference, an editable local install, or a replace, patch or override directive. Open the manifest at file scope and decide whether it belongs to a component published for others to depend on — a library that other builds require by its package name or module path, at versions that a registry publish or a version-control tag releases — or to an application or service at the root of its own build; stop at the second. For a published component, read the entry the hit sits in and trace what a consumer's build resolves once the path, the direct reference and every root-only override drop out: a path or git source paired with a registry version, an override over a dependency also named by a released version, or a pinned version leaves a released version, whether or not the dependency is bundled; a path or git source alone, a direct reference alone, or an override whose target carries a placeholder version or none leaves no released version. Validator question: **does a component published for others to depend on reach a component it reuses only through a local path, a direct reference or a root-only override, so that a consumer's build resolves no released version of it?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: ARCH-02`, severity major, `file`, `symbol`, `code` = the dependency entry or override directive verbatim from the diff, `fix` = the same dependency named by its released version — alone, or beside the local path or git source in the form the published manifest keeps — in the manifest's own syntax, `rationale` = the registry that refuses or advises against the path or direct reference, or the consumer's root build that ignores the override, so that no released version of the reused component reaches the consumer).

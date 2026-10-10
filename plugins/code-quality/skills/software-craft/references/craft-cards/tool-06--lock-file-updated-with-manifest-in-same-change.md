---
title: A change that edits the dependencies in a manifest updates the committed lock file in the same change
rule_id: TOOL-06
domain: tooling
step: [implement, review]
applies_to: [build-config]
triggers: ['^\s*"[@\w./-]+"\s*:\s*"(\^|~|>=?|<=?|=)?\s*v?\d', '^\s*[\w-]+\s*=\s*("[\^~=<>]?\s*\d|\{[^}]*\bversion\s*=)', '(^\s*["'']?|["''])[A-Za-z][\w.-]*(\[[\w,.-]+\])?\s*(==|>=|~=|<=|!=|<|>)\s*\d', '^\s*(require\s+)?[\w.-]+[.][a-z]{2,}/[\w./-]+\s+v\d+[.]\d+', '<artifactId>[^<]+</artifactId>', '\b(implementation|api|compileOnly|runtimeOnly|testImplementation)\s*\(?\s*["''][\w.-]+:[\w.-]+']
scope: callers
check_kind: mechanical
severity_default: major
---

# A change that edits the dependencies in a manifest updates the committed lock file in the same change

## Thesis
When a change adds, removes or re-constrains a dependency in the manifest of a project that commits a lock file, the same change carries the lock file regenerated from that manifest, so that the lock under review matches the manifest on every dependency.

## Rationale
A lock file describes the exact dependency tree that was resolved, so that teammates, deployments and continuous integration install exactly the same dependencies, and it is committed so that changes to that tree show as readable diffs in source control. When the manifest requires a dependency or a version that the committed lock does not record, a frozen install exits with an error and leaves the lock as it is; where one module file fixes every version, build commands run read-only by default and report an error whenever the file needs changes. A plain install instead compensates from the manifest and installs versions other than those the lock recorded, which can be hazardous for build and production environments: it can pull in unintended versions and render the benefit of the lock futile. A lock that still records a dependency the manifest dropped no longer describes the tree the manifest resolves. Carrying the regenerated lock in the same change keeps the checked-in source the complete record of what a build resolves, and gives each change to the dependency tree the opportunity to go through code review.

## Example
```typescript
bad:  // manifest re-constrained, lock file left as it was
      const manifest = { dependencies: {
        "example-lib": "^2.1.0" } };
      const lock = { packages: { "node_modules/example-lib": { version: "1.4.0" } } };
good: const manifest = { dependencies: {
        "example-lib": "^2.1.0" } };
      const lock = { packages: { "node_modules/example-lib": { version: "2.1.0" } } };
```

## Limits
The rule reaches a project that already commits a lock file; whether a project commits one at all is outside it. A manifest edit that touches no dependency entry, such as a script, a description or the package's own version, is outside the rule. Where one module file both declares the dependencies and fixes every version, there is no separate lock: the update is the module file and its checksum file as the fetch or tidy command writes them, and the tidy command's diff mode, which exits non-zero when either file would change, reports a hand edit left out of step. A lock that records resolved versions only needs no edit when the version it holds already satisfies a re-constrained entry; an unchanged lock that agrees with the new manifest is not a finding. A change whose only manifest edit deletes a dependency entry adds no line to match at review; the rule binds that removal at implement.

## Validator
Grep the hunk for an added, removed or re-constrained dependency entry in a manifest: a quoted package name with a version range, a name with a version specifier or a version table, a module path with a version, an artifact coordinate. Open the repository's tracked files in that manifest's directory and each enclosing directory up to the repository root, since a workspace may keep one lock at its root for all its members, and find the ecosystem's lock file or, where the module file fixes every version, its checksum file. When one is tracked, read it as it stands after the change and check that its entry for each edited dependency agrees with the new manifest entry: an added dependency is present, a re-constrained one resolves to a version the new constraint admits and, where the lock also records the constraint, records the new one, a removed one is no longer required from the root. Where the ecosystem's frozen install or the tidy command's diff mode can run, run it and read its exit status; a frozen install can accept a lock that still records a removed dependency, so a zero exit does not clear a removal. Validator question: **Does the change add, remove or re-constrain a dependency in a manifest whose project tracks a lock file, while that lock file, as it stands after the change, disagrees with the manifest on that dependency?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: TOOL-06`, severity major, `file`, `symbol`, `code` = the manifest line that adds, removes or re-constrains the dependency, `fix` = the lock file regenerated by the ecosystem's install, fetch or tidy command and added to the same change, showing its entry for that dependency, `rationale` = the frozen install that exits with an error on a dependency or version the lock does not record, the plain install that resolves versions the lock never recorded, or, for a removed dependency, the lock that still describes a tree the manifest no longer resolves).

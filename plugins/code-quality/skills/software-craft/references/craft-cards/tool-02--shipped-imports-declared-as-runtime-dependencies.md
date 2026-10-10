---
title: A package that shipped code imports is declared as a runtime dependency, not only as a development or test dependency
rule_id: TOOL-02
domain: tooling
step: [implement]
applies_to: [universal]
triggers: ['^\s*import\b|^\s*from\s+[A-Za-z_][\w.]*\s+import\b|\brequire\s*\(\s*["''][^./"'']', '"(devDependencies|dependencies|peerDependencies|optionalDependencies)"\s*:|"(@[\w.-]+/)?[\w.-]+"\s*:\s*"[~^<>=]*\s*\d|^\s*\[(dev-dependencies|dependencies|project[.]optional-dependencies|dependency-groups|tool[.](poetry|pdm)[.](group[.][\w-]+[.])?(dev-)?dependencies)\]|^\s*"[A-Za-z0-9][\w.-]*(\[[\w,\s-]*\])?\s*(==|>=|<=|~=|!=|>|<)|^\s*[A-Za-z0-9][\w-]*\s*=\s*("[~^<>=]*\s*\d|\{\s*version\s*=)|<scope>\s*(test|provided|compile|runtime)\s*</scope>|\b(testImplementation|compileOnly|runtimeOnly)\b']
scope: callers
check_kind: semantic
severity_default: major
---

# A package that shipped code imports is declared as a runtime dependency, not only as a development or test dependency

## Thesis
Where the ecosystem's manifest keeps runtime dependencies apart from development, test or provided ones, every package imported by code that ships is declared as a runtime dependency, unless the environment the code runs in supplies that package itself. Development and test declarations serve code that never ships, such as tests.

## Rationale
A development declaration is installed for the project's own developers and left out of what a library's consumers install and of a production install, so the code can work in development and fail in production. A provided scope is on the compilation and test path but not on the runtime path, so the build passes and the missing package surfaces only at run time, where the environment does not supply it. Consumers who have the package installed for another reason may see the code appear to work, so the failed import can reach only a small percentage of them and be difficult to reproduce. In a study of 100 projects in one package ecosystem, 28.2% of the dependencies configured as development dependencies were released to production, so the list that declares a package does not by itself decide whether the shipped artifact carries it; whether a development declaration fails depends on how the shipped artifact receives its packages. Moving the declaration to the runtime list makes a consumer's install and a production install receive the package.

## Example
```typescript
bad:  // manifest: "devDependencies": { "yamlx": "^2.0.0" }
      import { parse } from "yamlx"; // src/config.ts, part of the shipped package
good: // manifest: "dependencies": { "yamlx": "^2.0.0" }
      import { parse } from "yamlx"; // src/config.ts, part of the shipped package
```

## Limits
Code that never ships imports development and test dependencies correctly; the tools that check this split take the set of development-only files, such as test files, as configuration. A package the runtime environment or the host application supplies, such as the interfaces a container provides or the host a plugin extends, is correctly declared under a provided scope or as a peer dependency; the finding there is such a package that the target environment does not supply. A package declared as optional may be missing from an install by design, and the shipped code that imports it is expected to handle its absence or to run only for the feature that needs it; the tools that check this split accept that import, so an optional declaration is outside this rule. A shipped artifact that already carries a development-declared package, such as a bundle built in development, does not lose it; the finding needs an install that leaves the development list out. The reverse placement, a runtime declaration of a package that only tests use, is reported by dependency analysis as its own category, compile scoped but only used in tests, and is outside this rule.

## Validator
Grep the hunk for added import lines and for manifest entries added to or moved between the runtime, development, test and provided lists. Stop when the ecosystem's manifest keeps a single dependency list. For each package an added import names, decide whether the importing file ships: test files and the development-only paths named in the project's lint or dependency-check configuration do not. For a shipped file, open the ecosystem's manifest and find the list that declares the package; for an entry moved out of the runtime list, search the shipped sources for imports of it. Open the build or packaging configuration and confirm that the shipped artifact receives its packages by installing the manifest's runtime list rather than carrying them in a bundle built in development; for a provided or peer entry, confirm whether the target environment or the host application supplies the package. Validator question: **Does a file that ships import a package that the manifest declares only in a list the shipped install leaves out?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: TOOL-02`, severity major, `file`, `symbol`, `code` = the import line and the manifest entry that declares the package, `fix` = the manifest entry moved to the runtime dependency list, in the manifest's own format, `rationale` = the shipped file that imports the package and the install that leaves it out).

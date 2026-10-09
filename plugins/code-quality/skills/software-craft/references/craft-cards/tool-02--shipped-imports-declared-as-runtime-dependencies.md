---
title: A package that shipped code imports is declared as a runtime dependency, not only as a development or test dependency
rule_id: TOOL-02
domain: tooling
step: [implement, review]
applies_to: [build-config]
triggers: ['^\s*import\b|^\s*from\s+[A-Za-z_][\w.]*\s+import\b|\brequire\s*\(\s*["''][^./"'']', '"(devDependencies|dependencies|peerDependencies|optionalDependencies)"\s*:|"(@[\w.-]+/)?[\w.-]+"\s*:\s*"[~^<>=]*\s*\d|^\s*\[(dev-dependencies|dependencies|project[.]optional-dependencies|dependency-groups|tool[.](poetry|pdm)[.](group[.][\w-]+[.])?(dev-)?dependencies)\]|^\s*"[A-Za-z0-9][\w.-]*(\[[\w,\s-]*\])?\s*(==|>=|<=|~=|!=|>|<)|^\s*[A-Za-z0-9][\w-]*\s*=\s*("[~^<>=]*\s*\d|\{\s*version\s*=)|<scope>\s*(test|provided|compile|runtime)\s*</scope>|\b(testImplementation|compileOnly|runtimeOnly)\b']
scope: callers
check_kind: mechanical
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

## Source
- DOI 10.1145/3551349.3556896 (ASE 2022), abstract, from a GitHub-hosted ACM bibliographic export (fetched): "We conduct an empirical study on 100 JavaScript projects using the Node Package Manager (npm) to quantify how often project dependencies are released to production" ... "the functionality of a package is not enough to determine if it will be released to production or not. In fact, 59% of the installed dependencies configured as runtime dependencies are not used in production, and 28.2% of the dependencies configured as development dependencies are used in production, debunking two common assumptions of dependency management."
- deptry rule DEP004, osprey-oss/deptry docs/rules-violations.md (fetched): "Project should not use development dependencies in non-development code"; "To fix the issue, `orjson` should be moved from `[tool.pdm.dev-dependencies]` to `[project.dependencies]`".
- eslint-plugin-import rule import/no-extraneous-dependencies, docs/rules/no-extraneous-dependencies.md (fetched): "`devDependencies`: If set to `false`, then the rule will show an error when `devDependencies` are imported."; "the setting will be set to `true` (no errors reported) if the name of the file being linted (i.e. not the imported file/module) matches a single glob in the array".
- eslint-plugin-n rule n/no-extraneous-import, docs/rules/no-extraneous-import.md (fetched): "the transitive dependency could be a dev dependency, meaning your code could work in development but not in production."
- Rush documentation, 'Phantom dependencies', microsoft/rushstack-websites phantom_deps.md (fetched): "The **glob** package is coming from our `devDependencies`, which means it only gets installed for developers who work on the **my-library** project. For other consumers, `require("glob")` should fail immediately"; "most consumers will also have **glob** for some reason (e.g. using **rimraf** themselves), so it may appear to work. Only a small percentage of our consumers will encounter the failed import error, making it seem like they're reporting a weird issue that's difficult to repro."
- npm documentation, npm-install, npm/cli docs/lib/content/commands/npm-install.md (fetched): "With the `--production` flag (or when the `NODE_ENV` environment variable is set to `production`), npm will not install modules listed in `devDependencies`."
- Maven 'Introduction to the Dependency Mechanism', apache/maven-site introduction-to-dependency-mechanism.md (fetched): "provided ... indicates you expect the JDK or a container to provide the dependency at runtime ... A dependency with this scope is added to the classpath used for compilation and test, but not the runtime classpath."
- Maven Dependency Plugin goal dependency:analyze, AbstractAnalyzeMojo.java (fetched): "determines which are: used and declared; used and undeclared; unused and declared; compile scoped but only used in tests."
- Maven guide 'Optional Dependencies', apache/maven-site introduction-to-optional-and-excludes-dependencies.md (fetched): "some of the dependencies are only used for certain features in the project and will not be needed if that feature isn't used"; "If a user wants to use functionality related to an optional dependency, they have to redeclare that optional dependency in their own project."
- npm documentation, package.json, npm/cli docs/lib/content/configuring-npm/package-json.md (fetched): optionalDependencies, "It is still your program's responsibility to handle the lack of the dependency."; peerDependencies, "you want to express the compatibility of your package with a host tool or library"; "In npm versions 3 through 6, `peerDependencies` were not automatically installed".
- eslint-plugin-import, docs/rules/no-extraneous-dependencies.md (fetched): "`optionalDependencies`: If set to `false`, then the rule will show an error when `optionalDependencies` are imported. Defaults to `true`."; "`peerDependencies`: If set to `false`, then the rule will show an error when `peerDependencies` are imported. Defaults to `true`."
- deptry, docs/supported-dependency-managers.md (fetched): regular dependencies come from the `[project]` `dependencies` entry and "groups under `[project.optional-dependencies]` section".
- Caveat: the measured rates come from 100 projects of one ecosystem and count dependencies released to production, not failed imports; each tool rule checks one ecosystem's manifest.

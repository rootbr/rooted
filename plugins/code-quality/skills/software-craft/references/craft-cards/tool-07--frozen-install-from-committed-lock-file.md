---
title: CI and build scripts install dependencies from the committed lock file in a mode that fails on a mismatch instead of re-resolving
rule_id: TOOL-07
domain: tooling
step: [implement]
applies_to: [build-config]
triggers: ['\bnpm\s+(install|i)\b', '\bpnpm\s+(install|i)\b(?!.*--frozen-lockfile)', '\byarn(\s+install)?\s*$|\byarn\s+install\b(?!.*(--frozen-lockfile|--immutable))', '\b(cargo\s+(build|test|run|check)|uv\s+(sync|run))\b(?!.*--(locked|frozen))', '--no-frozen-lockfile|-mod=mod\b', '\bgo\s+(get|mod\s+tidy(?!\s+-diff))\b', '"go",\s*"(get|mod",\s*"tidy)"(?!,\s*"-diff")', '\b(p?npm|yarn)\s+(update|upgrade|up)\b|\bcargo\s+update\b']
scope: callers
check_kind: semantic
severity_default: major
---

# CI and build scripts install dependencies from the committed lock file in a mode that fails on a mismatch instead of re-resolving

## Thesis
A dependency-install step in continuous integration, a container build or a deployment script installs from the ecosystem's committed lock file in the package manager's frozen mode, which installs the versions the lock file records and aborts on an inconsistency between the lock file and the manifest instead of re-resolving and updating the lock file. The same automated steps run no command that adds, upgrades or tidies dependencies and so rewrites the manifest or the lock file.

## Rationale
When the manifest and the lock file disagree, for instance after a manifest change committed without its lock file, a plain install compensates from the manifest: it installs versions other than those the lock file records, and where the lock file is absent or does not satisfy the manifest it looks for the newest versions the manifest's constraints admit and writes them to the lock file. In a build or production environment this can pull in unintended package versions and defeat the purpose of the lock file. The frozen mode adheres to the recorded set and turns any inconsistency into an aborted install: it exits with an error instead of updating the lock file, and where it requires an existing lock file, a missing one fails the step as well. Keeping the commands that change the dependency set out of automated steps means a change to the dependency tree is made deliberately and has the opportunity to go through code review, and the checked-in source stays the complete source of truth for what an automated build builds.

## Example
```go
bad:  var ciSteps = []string{"npm install", "yarn install", "pnpm install --no-frozen-lockfile",
          "uv sync", "npm update", "go build -mod=mod ./...", "go get -u ./..."}
      var tidy = exec.Command("go", "mod", "tidy")
good: var ciSteps = []string{"npm ci", "yarn install --frozen-lockfile", "pnpm install --frozen-lockfile",
          "uv sync --locked", "go build ./..."}
      var tidy = exec.Command("go", "mod", "tidy", "-diff")
```

## Limits
Where the manifest itself fixes the version of every dependency and the build commands act read-only by default, a build already reports an error and suggests a fix when the manifest needs a change; there the rule reaches the commands that add, upgrade or tidy dependencies and an option that tells the build commands to update the manifest automatically. A check that prints the changes the manifest needs and exits non-zero, without modifying the manifest or its checksum file, is the frozen counterpart of a tidy command and satisfies the rule. Where a package manager makes the frozen mode its default in an environment it detects as continuous integration and a lock file is present, a plain install there satisfies the rule unless the step passes the option that allows lock-file updates; a container build or script outside that detection keeps the non-frozen default and needs the explicit option. A mode that installs from the lock file without checking whether it is up to date never re-resolves and satisfies the rule, though it leaves a manifest change without its lock-file update undetected. A job that re-resolves to the newest versions the manifest admits only to test them, or to propose the updated lock file as a change that passes continuous integration and code review before merge, is outside the rule when its re-resolved set reaches neither the committed lock file without review nor what is shipped or deployed. The rule does not reach a developer's local command that adds or upgrades a dependency, whose result is committed and has the opportunity to go through code review with the change.

## Validator
Grep the hunk for a package-manager install, build, test or sync command and for a command that adds, upgrades or tidies dependencies, in a continuous-integration workflow, a container build file, a deployment script or a build script that an automated pipeline runs. Open the file and confirm that the step runs in an automated pipeline, that the job does not re-resolve only to test newer versions or to propose them as a reviewed change, and that the repository commits a lock file, or a manifest that fixes every version, for the manifest the step installs. For an install, look for the package manager's frozen or locked option, or a frozen default in that environment that the step leaves in place, and for an option that allows lock-file or manifest updates; for a dependency-changing command, trace whether it rewrites the manifest or the lock file or only reports the needed changes and exits non-zero. Validator question: **Does an automated install, build or deployment step install dependencies in a mode that can re-resolve or update the committed lock file, or run a command that rewrites the manifest or the lock file?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: TOOL-07`, severity major, `file`, `symbol`, `code` = the install or dependency-changing command line verbatim from the diff, `fix` = the same step with the package manager's frozen or locked option, or the dependency-changing command removed or replaced by its report-only check, in the file's language, `rationale` = names the inconsistency the step would resolve silently by installing versions other than those the lock file records, or the dependency change that would reach the build without going through code review).

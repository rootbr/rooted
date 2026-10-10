---
title: A workflow, container build or build script that a change adds or edits refers to each third-party action and every base image and fetched script it runs by a full commit SHA, an image digest or a recorded checksum, or through a committed lockfile entry recording one, never by a mutable tag, branch or bare URL alone
rule_id: TOOL-48
domain: tooling
step: [implement]
applies_to: [build-config]
triggers: ['^\s*(?:(?:-\s*)?uses:\s*[''"]?(?:(?![.]/|docker://)[\w.-]+/[\w./-]+@(?![0-9a-f]{40}\b)|docker://(?![^\s''"]*@sha256:[0-9a-f]{64}))|(?:-\s*)?image:\s*[''"]?(?![^\s''"]*@sha256:)[\w${}.-]+(?:/[\w${}.-]+)*(?::[\w${}.-]+)?[''"]?\s*$|FROM\s+(?:--platform=\S+\s+)?(?!scratch\b)(?![^\s@]*@sha256:)\S+|(?i:ADD)\s+(?!--checksum)(?:--\S+\s+)*https?://)', '\b(curl|wget|iwr|Invoke-WebRequest)\b[^|]*\|\s*(sudo\s+)?((ba|z|da)?sh|python3?|iex)\b|\b(ba)?sh\s+(-c\s+[''"]?\$\(|<\()\s*(curl|wget)\b', '\b(?:curl|wget|iwr|Invoke-WebRequest)\b[^|\n]*\bhttps?://']
scope: callers
check_kind: semantic
severity_default: major
---

# A workflow, container build or build script that a change adds or edits refers to each third-party action and every base image and fetched script it runs by a full commit SHA, an image digest or a recorded checksum, or through a committed lockfile entry recording one, never by a mutable tag, branch or bare URL alone

## Thesis
Where a CI workflow, container build file or build script that a change adds or edits runs code from outside the repository, it names that code by a reference whose content cannot change: an action or reusable workflow from a third party, meaning a publisher other than the project's own organization and the CI platform's own `actions/` and `github/` owners, by its full 40-character commit SHA, or by a tag whose commit a committed workflow lockfile records; a base, job or service image by its digest, a tag kept beside the digest being allowed; and a downloaded script, archive or binary by a URL that names a commit, or with a checksum recorded in the repository and verified before the download runs. A tag, a branch, an image tag or a URL alone does not meet the rule, a version-numbered tag included.

## Rationale
A branch, or a tag whose release was not published as immutable, can be repointed by whoever controls the upstream repository, and an image tag by whoever publishes to it, so the code a tag reference runs is not guaranteed to be the code the workflow author reviewed. A compromised action has access to every secret configured on the repository and may be able to write to the repository with the workflow's token; when attackers retroactively moved several version tags of one action to a malicious commit, over 23,000 repositories were affected and CI secrets were exposed in workflow logs. Replacing the code behind a commit SHA would take a SHA-1 collision for a valid Git object payload, and the platform requires the full SHA, not an abbreviated one; a digest guarantees the same image even when the publisher replaces its tag. An attacker who controls the server a download is piped from could inject malicious code into the pipe; checking the SHA sum of the returned content verifies its integrity, and hashes recorded for remote data are verified during the build. In a study of GitHub CI workflows, 78.8% of third-party action references named a tag and 1% a commit hash. A pin gives up automatic updates, including bug fixes and security updates, and the platform raises vulnerability alerts only for actions referenced by semantic version, not for SHA-pinned ones; an update tool such as Dependabot or Renovate that raises pull requests bumping the pinned references keeps them current and leaves an audit trail of when and how each one changed.

## Example
```typescript
bad:  const setup = { name: "Set up tool",
        uses: "example-org/setup-tool@v2" };
      execSync("curl -fsSL https://example.com/install.sh | sh");
good: const setup = { name: "Set up tool",
        uses: "example-org/setup-tool@0123456789abcdef0123456789abcdef01234567" }; // v2.4.1
      const script = execSync(`curl -fsSL ${INSTALL_SCRIPT_URL}`);
      if (sha256Hex(script) !== INSTALL_SCRIPT_SHA256) throw new Error("install script checksum mismatch");
      execSync("sh", { input: script });
```

## Limits
- Trusted creators: the platform's guidance allows a tag when the project trusts the action's creators, as it may trust its own organization, its own starter workflows bind its actions by major-version tag, and lint rules for third-party actions exempt local paths and the `actions/` and `github/` owners. The same guidance warns that a tag can still be moved or deleted if a bad actor gains access to the repository storing the action; under an organization policy requiring full-length SHAs, all actions must be pinned to be used, the organization's own and the platform's included; and one workflow auditor's default requires a hash on every action.
- Lockfile: a project that adopts the platform's workflow lockfile, a public-preview feature, needs no SHA inside the workflow file for a dependency the lockfile records. The lockfile pins a commit to every action, transitive action dependencies included, and to every reusable workflow, except the dependencies of reusable workflow calls; a dependency missing from it still needs a full SHA.
- Images: image linters ask for an explicit release tag rather than `latest`, and one auditor reports a tag without a digest only as a pedantic finding. Container supply-chain guidance holds that only digests and notary-signed tags are cryptographically guaranteed to be the same artefact and says to pull only by digest; a multi-architecture build may pin the manifest-list hash instead of a single image hash.
- Update cost: pinning can inhibit updates, including when the pinned version is itself found compromised, and the static check that grades pinning answers this with automated tools that report outdated dependencies and with quick updates. A study of npm packages found that pinning direct dependencies raised the cost of maintaining vulnerable and outdated dependencies and even the risk of exposure to malicious updates in larger dependency graphs; it concerns package dependencies, not CI references. Pinned dependencies are only a candidate requirement for a future build level of the supply-chain levels framework.
- Transitive references: a commit SHA does not fix the code of an action that itself refers to another action by a mutable reference, as when actions built on a compromised setup action were compromised regardless of version or pinning method. The rule covers the references a change adds; transitive ones belong to the lockfile.
- Forks: a SHA can name a commit that exists only in a fork yet looks like a commit of the named repository; the platform says to verify that a chosen SHA is from the action's repository and not a fork.
- Immutable releases: the tag of a release published as immutable is locked to its commit, cannot be deleted while the release exists and cannot be reused once the release is deleted; the reference does not show that its release is immutable, and the static checks in the Source still ask for the commit SHA, so the rule does too.
- Scope: the static check grades workflows, container build files and shell scripts used during the build and release process; a local path inside the repository is not a third-party reference.

## Validator
Grep the added and edited lines of CI workflow, container build and build-script files for action and reusable-workflow references (`uses:`), image references (`FROM`, `image:`, `docker://`), remote `ADD` sources, and downloads (`curl`, `wget` and the like) of a script, archive or binary that the build pipes into a shell or interpreter, unpacks or runs. Take each action reference's publisher from its owner path; set aside local paths and, for actions and reusable workflows only, the project's own organization and the platform's `actions/` and `github/` owners, unless a project policy or auditor configuration requires hashes for every action. Accept a 40-hex commit SHA, an `@sha256:` digest (a manifest-list digest for a multi-architecture image), an `ADD --checksum`, a raw file URL whose ref segment is a 40-hex commit, a download checked against a checksum held in the repository before it runs, or a tag whose commit the committed `.github/workflows/actions.lock` records; open that lockfile when a reference relies on it. For a newly added SHA, confirm the commit belongs to the named repository and not only to a fork. Validator question: **Does an added or edited line run a third-party action or reusable workflow, or fetch any image or downloaded script, archive or binary the build uses, by a tag, branch, image tag or bare URL with no full commit SHA, digest, verified recorded checksum or lockfile entry fixing its content?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: TOOL-48`, severity major, `file`, `symbol`, `code` = the added reference line verbatim, `fix` = the same reference by full commit SHA, image digest or checksum-verified download with the human-readable version kept in a trailing comment, in the file's language, `rationale` = names the publisher, the mutable reference and what a moved tag or replaced download would run with the job's secrets).

---
title: A released component version is never changed, so a release step ships every change as a new version and leaves existing version tags and artifacts in place
rule_id: ARCH-01
domain: architecture
step: [implement, review]
applies_to: [build-config, library]
triggers: ['\bgit\s+tag\b[^\n]*\s(-\w*[fd]\w*\b|--force\b|--delete\b)', '\bgit\s+push\b[^\n]*(--force\b|\s-[fd]\b|--delete\b|\+refs/|\s\+\w|\s:\w)', '\b(npm|yarn|pnpm)\s+unpublish\b', '\bgh\s+release\s+(delete\b|upload\b[^\n]*--clobber\b)']
scope: file
check_kind: semantic
severity_default: major
---

# A released component version is never changed, so a release step ships every change as a new version and leaves existing version tags and artifacts in place

## Thesis
Once a version of a component has been released, the contents of that version stay as released and every modification is released as a new version: a release step tags and publishes the change under a new version identifier, and leaves each version tag that has been pushed, or that others could read, undeleted at the revision it was created on, with that version's published artifacts as they were published. A version found broken after publication is superseded by a new version or retracted, and stays available in version control and on the proxies that serve it, so that builds that depend on it are not broken.

## Rationale
A version identifies an immutable snapshot. Once a tag has been pushed, others have already seen it, and keeping the same name for new contents may leave two people who both have "version X" but different contents. Git does not change tags behind a user's back: a user who already got the old tag keeps it, because updating one's own tag cannot change it for them. A module system that authenticates versions for safe, repeatable builds may show clients a security error when a tag is modified, and a deleted tag's content may remain available on its proxies, so deleting a tag may not withdraw what it released. One package manager's registry fails a publish whose name and version already exist, never lets that name and version be used again even after removal, and accepts the package again only under a new version number. The content rule is a requirement of the versioning scheme; the tag rule and the retraction rule are recommendations.

## Example
```java
bad:  void release(String releasedVersion, String fixRev) {
          shell.run("git tag -f v" + releasedVersion + " " + fixRev);
          shell.run("git push --force origin v" + releasedVersion);
          shell.run("gh release upload v" + releasedVersion + " app.jar --clobber");
          shell.run("npm unpublish web-client@" + releasedVersion);
      }
good: void release(String nextVersion, String fixRev) {
          shell.run("git tag v" + nextVersion + " " + fixRev);
          shell.run("git push origin v" + nextVersion);
      }
```

## Limits
A tag that was never pushed, in a repository others cannot read, may be re-created in place with force: the re-tagging problem begins once others could have seen the old tag. An alias tag that the project documents as tracking the most recent stable release of a major version is moved to each new release by design, while a release for each specific version lets users bind back to that version if an issue is encountered with the latest one. A branch head, which receives commits as development proceeds, is unstable to bind to and is not a released version. The rule reaches pre-release versions too, since a pre-release version also identifies an immutable snapshot. It governs release steps and the version identifiers they write; which classes belong together in one component is a design question outside this check.

## Validator
Grep the added lines for a tag command that forces or deletes (`tag -f`, `tag -d`, `--force`, `--delete`), a push that forces or deletes refs (`--force`, ` -f`, ` -d`, `--delete`, a `+` or `:` refspec), a registry `unpublish`, and a release-asset delete or overwrite (`release delete`, `--clobber`). For each hit, read the file for the tag or version it names and trace where that name comes from: a value read from an existing release (the current version, the last tag, a released version parameter) marks an in-place change, and a newly computed version marks a new release. Set aside a tag created earlier in the same unpushed step and an alias tag the project documents as tracking the most recent stable release of a major version. Validator question: **Does the added step delete, move or overwrite a version tag or artifact that identifies an already pushed or published version?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: ARCH-01`, severity major, `file`, `symbol`, `code` = the added line that deletes, moves or overwrites the released version's tag or artifact, `fix` = the release step that leaves the released version's tag and artifacts in place and publishes the change, or the supersession or retraction of a broken version, under the next computed version, in the file's language, `rationale` = for a moved or overwritten version, that users who already fetched it keep the old contents while later fetches get the new ones and that authenticated fetches may fail with a security error; for a deleted version, that builds that depend on it may break and that its name and version may never be published again).

## Source
- Semantic Versioning 2.0.0, item 3 (semver/semver, `semver.md`) (fetched): "Once a versioned package has been released, the contents of that version MUST NOT be modified. Any modifications MUST be released as a new version."
- Semantic Versioning 2.0.0, FAQ "What do I do if I accidentally release a backward incompatible change as a minor version?" (fetched): "fix the problem and release a new patch version that corrects the problem and restores backward compatibility. Even under this circumstance, it is unacceptable to modify versioned releases."
- Go Modules Reference, § Versions (golang/website, `_content/ref/mod.md`) (fetched): "A version identifies an immutable snapshot of a module, which may be either a release or a pre-release."
- Go Modules Reference, § Mapping versions to commits (fetched): "Once a tag is created, it should not be deleted or changed to a different revision. Versions are authenticated to ensure safe, repeatable builds. If a tag is modified, clients may see a security error when downloading it. Even after a tag is deleted, its content may remain available on module proxies."
- Go Modules Reference, § retract directive (fetched): "A `retract` directive is useful when a version was published prematurely or a severe problem was discovered after the version was published. Retracted versions should remain available in version control repositories and on module proxies to ensure that builds that depend on them are not broken."
- Git documentation, git-tag § On Re-tagging (git/git, `Documentation/git-tag.adoc`) (fetched): "If you never pushed anything out, just re-tag it. Use `-f` to replace the old one."; "if you have pushed things out (or others could just read your repository directly), then others will have already seen the old tag"; "you may be in the situation that two people both have "version X", but they actually have 'different' "X"'s"; "Git does *not* (and it should not) change tags behind users back"; "If somebody got a release tag from you, you cannot just change the tag for them by updating your own one."
- npm CLI documentation, npm-publish and npm-unpublish (npm/cli, `docs/lib/content/commands/`) (fetched): "The publish will fail if the package name and version combination already exists in the specified registry."; "that specific name and version combination can never be used again, even if it is removed with npm unpublish"; "In order to publish the package again, you must use a new version number."
- Actions toolkit, action-versioning (actions/toolkit, `docs/action-versioning.md`) (fetched): "Move the major version tag (v1, v2, etc.) to point to the ref of the current release."; "You should keep this tag updated to the most recent stable minor/patch release."; "Creating a release like v1.0.0 allows users to bind back to a specific version if an issue is encountered with the latest major version."; "The `main` branch has the latest code and is unstable to bind to since changes get committed to main".
- Caveat: the tag and retraction statements come from one module system's and one version-control tool's documentation, phrased as "should", and the registry statements from one package manager's documentation; the content rule is the versioning specification's requirement.

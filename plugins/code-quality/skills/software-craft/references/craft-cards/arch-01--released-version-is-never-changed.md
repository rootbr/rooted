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

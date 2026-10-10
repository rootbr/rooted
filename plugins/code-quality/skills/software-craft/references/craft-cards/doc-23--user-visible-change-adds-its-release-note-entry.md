---
title: In a project whose documented workflow collects release-note entries per change, a change with a user-visible effect that the project's policy does not exempt adds its own entry in that change, in the form the project uses
rule_id: DOC-23
domain: docs
step: [implement, document, review]
applies_to: [universal]
triggers: ['\badd_argument\s*\(|\bflag[.](String|Bool|Int|Int64|Uint|Float64|Duration|Var)\w*\s*\(|#\[(arg|command)\b|@(Option|Parameters?|Command)\s*\(|[.]option\s*\(\s*[\x22\x27]-', '\b(os[.]environ|os[.]getenv|os[.]Getenv|os[.]LookupEnv|System[.]getenv|process[.]env|env::var)\b', '^\s*export\s+(default\s+)?(async\s+)?(function|class|const|interface|type|enum)\b|^\s*pub\s+(async\s+)?(fn|struct|enum|trait|mod|const|type)\b|^\s*public\s+(static\s+|final\s+|abstract\s+)*(class|interface|enum|record)\b|^func\s+(\([^)]*\)\s*)?[A-Z]\w*\s*[(\[]', '\b(DeprecationWarning|FutureWarning)\b|#\[deprecated\b|@[Dd]eprecated\b|\bDeprecated:']
scope: callers
check_kind: semantic
severity_default: minor
---

# In a project whose documented workflow collects release-note entries per change, a change with a user-visible effect that the project's policy does not exempt adds its own entry in that change, in the form the project uses

## Thesis
In a project whose documented workflow collects release-note entries per change, a change with a user-visible or operator-visible effect that the project's policy does not exempt adds its own entry in that same change, in the form the project uses: a file in the project's release-notes or news-fragment directory, a note in the release-notes file for the coming release, a release-note block in the pull-request body, or a changelog trailer on the commit. A comment in the change description that only flags the change as needing a note is not an entry.

## Rationale
Release notes are one of the most important reference points for users about to install or upgrade a release, and a project's NEWS file holds a list of user-visible changes worth mentioning. Generating the release notes of a project by an individual is challenging, because it is not feasible for one person to know all fixed issues or the integrated new features of the project. In 909 release-note issues from 722 GitHub repositories, notes were more likely to miss information than to include incorrect information, especially for breaking changes; the two main reasons found for incomplete notes were a lack of manpower or time to conduct thorough inspections and the difficulty for a limited number of developers to understand all changes between versions, and among the practices issue participants suggest that may make notes more likely to be complete is to distribute the workload of creating notes among all contributors, as some projects do by requiring each pull request to contain a release-notes section in its body. Manually producing release notes is time-consuming and is sometimes neglected: of 1,924 releases of 13 GitHub projects, 711 (37%) had empty release notes. Across 4,377 security advisories in seven package ecosystems, 61.5% of the security releases came with a release note that documents the corresponding security fix. An entry that travels in the change is within reach of code review, where reviewers are encouraged to request a release note when they think one is warranted, and of a check on the pull request or branch: a bot fails the status when the news directory holds no entry and no skip label is set, a bot labels the pull request until its release-note block is populated, and a fragment check tests whether a feature branch adds at least one news fragment.

## Example
```java
bad:  // change contains: ExportCommand.java
      public final class ExportCommand {
        @Option(names = "--format") String format = System.getenv("EXPORT_FORMAT");
        @Deprecated(forRemoval = true) public static final String DEFAULT = "csv"; }
good: // change contains: ExportCommand.java, changes/next/export-format.md: "export
      // takes --format, default $EXPORT_FORMAT; ExportCommand.DEFAULT is deprecated."
      public final class ExportCommand {
        @Option(names = "--format") String format = System.getenv("EXPORT_FORMAT");
        @Deprecated(forRemoval = true) public static final String DEFAULT = "csv"; }
```

## Limits
The rule holds where the project's contributor documentation or CI declares per-change collection: a news-fragment directory with a check, a release-note block a bot requires in the pull-request body, a changelog trailer from which the changelog is generated, or a checklist that asks for a note in the release-notes file. Where the releaser collects the commits since the last release into the changelog, where the hosting platform generates notes from the list of merged pull requests, or where a release tool generates the changelog from the type and subject that every commit message carries under the project's commit convention, a change carries no separate entry and the rule does not apply; a changelog trailer that the policy requires only on commits with a user-facing effect is an entry, and the rule applies to it. Where the policy leaves notes for user-facing changes to the author's or reviewer's discretion, only what it requires is in scope; one such policy asks that information about a potentially breaking change be added to the Potentially Breaking Changes section of the release notes when the change is committed. Documented exemptions are not findings: documentation changes, test changes, build infrastructure, strictly internal or developer-facing changes such as refactoring with no user-visible effect, trivial changes and changes that do not affect the documented behaviour, changes that already have an entry, a fix to an earlier unreleased change whose entry remains valid, a fix for a bug that was never released, a bug fix applied only to the main branch where the policy exempts it, a change with little impact on users that a maintainer marks with the project's skip label, and a revert of a change not yet included in any formal release, which removes that change's entry. A release branch that modifies the main news file is expected to carry no news fragments. Where the policy accepts a placeholder, such as a file holding a TODO that ideally names the person responsible for completing the note, that file in the change is the entry.

## Validator
Grep the hunk for an added or changed user-visible surface: a public type or exported function, a command-line option, an environment-variable read, a deprecation marker, a line in an API listing file. When the changed symbol is internal, open its callers to decide whether the change reaches a public interface, a command-line option, configuration, or output that users or operators see. Open the project's contributor documentation, pull-request template and CI configuration to find the release-note workflow: a fragment directory and its check, a release-notes file for the coming release, a required release-note block in the pull-request body, or a changelog trailer. Look in the same change for an entry in that form, and check the change against the policy's exemptions and its skip label. Validator question: **Does the project's documented workflow collect release-note entries per change, does this change have a user-visible or operator-visible effect its policy does not exempt, and does the change carry no entry in the project's form?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: DOC-23`, severity minor, `file`, `symbol`, `code` = the added or changed declaration, option, configuration read or deprecation marker that carries the user-visible effect, quoted verbatim from the diff, `fix` = the missing entry in the project's form, with its path or block marker and one sentence that tells users what changed, `rationale` = names the user-visible effect, the project's documented per-change workflow and the form the entry takes there).

---
title: An installation or getting-started section added or changed in a change states the prerequisites a user needs before its first step
rule_id: DOC-17
domain: docs
step: [document]
applies_to: [universal]
triggers: ['(?i)^\s*(//[/!]?\s*)?#{1,4}\s+(install(ation|ing)?|getting started|quick ?start|set ?up|setup|prerequisites|requirements)\b', '^\s*(//[/!]?\s*)?(\$\s+)?(sudo\s+)?(python3?\s+-m\s+pip|pip3?|pipx|poetry|uv(\s+pip)?|npm|npx|yarn|pnpm|cargo|go|brew|apt(-get)?|dnf|mvn|gradle|[.]/gradlew)\s+(install|i|add|get|build|sync)\b']
scope: file
check_kind: semantic
severity_default: minor
---

# An installation or getting-started section added or changed in a change states the prerequisites a user needs before its first step

## Thesis
An installation or getting-started section that a change adds or edits states, ahead of its first step or in a prerequisites or requirements section that precedes it in the same document, what must already be in place for its steps to work: the supported versions of the runtime and tools the steps invoke, the libraries they require, and the configuration they assume.

## Rationale
Installation-related instructions are crucial for users to start with a software project. Documentation is incomplete when it does not contain the information about the system needed by practitioners or users to perform their tasks; among the 162 documentation issue types identified in 878 artifacts mined from mailing lists, question-and-answer discussions, issue repositories and pull requests, the taxonomy lists missing supported versions, missing compatibility information, missing required libraries and missing configuration instructions, and the study's example of missing compatibility information asks to state which compiler versions are supported. In the same artifacts, installation guidelines were the documentation type second most often affected by correctness issues: 20% of the cases with a labelled documentation type, after code examples at 50%. Among surveyed practitioners, inappropriate installation instructions were the most frequently encountered correctness issue and, together with faulty tutorials, the one most of them considered relevant (65%); the lack of installation, deployment and release instructions was considered important by 68%. Participants suggested, among other solutions, reviews of the installation instructions by both internal team members and external users. Maintainers' changes to installation-related README sections fall into six categories, among them pre-installation, installation and post-installation instructions, and readers found documents augmented from a template covering those sections generally of better quality.

## Example
```go
bad:  // # Installation
      //
      //	go install example.com/tool/cmd/tool@latest
      package tool
good: // # Installation
      //
      // Requires Go 1.22 or later, libfoo-dev and TOOL_CONFIG set to a config file.
      //
      //	go install example.com/tool/cmd/tool@latest
      package tool
```

## Limits
The rule reaches installation and getting-started sections the change adds or edits; a section the change leaves untouched is outside it. A section preceded in the same document by a prerequisites or requirements section that states the versions, libraries and configuration, or one that names before its first step the section or document where they are stated, meets the rule. The evidence counts how often installation issues occur in open-source artifacts and how practitioners rate them, and the template result comes from a reader survey of template-augmented documents; no cited study compares installation success with and without a stated list of prerequisites.

## Validator
Grep the hunk for a heading that opens an installation, getting-started, quick-start, setup, prerequisites or requirements section, and for an added or changed install, get or build command. Open the file and read the section from its heading through its last step. Trace each runtime, tool, library and configuration value the steps invoke or read, and look for its statement before the first step, in the section, in a prerequisites or requirements section that precedes it in the same document or in a section or document the section names there, or for an earlier step of the section that installs or sets it. Validator question: **Does an installation or getting-started section that the change adds or edits contain a step whose required runtime or tool version, library or configuration is neither stated before the section's first step nor installed or set by an earlier step of the section?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: DOC-17`, severity minor, `file`, `symbol`, `code` = the section heading and the first step that relies on the unstated prerequisite, quoted verbatim from the diff, `fix` = a prerequisites line placed before the section's first step naming the version, library or configuration the step needs, `rationale` = the prerequisite the step assumes and that the section leaves unstated).

## Source
- DOI 10.1145/3377811.3380405, § 4 (RQ1), Correctness and Completeness (fetched): "inappropriate installation instructions was the most frequently encountered issue and, together with faulty tutorial, the one considered relevant by most practitioners (65% of them)"; "the lack of installation, deployment, & release instructions [...] were considered important by a majority (respectively 68%, 65% and 60%)"; "performing reviews on the installation instructions by both internal team members and external users".
- DOI 10.1109/ICSE.2019.00122, abstract, § IV.A Correctness and Completeness, Fig. 1 (fetched): "categorized 878 documentation-related artifacts stemming from four different sources, namely mailing lists, [...] discussions, issue repositories, and pull requests"; "followed by installation guidelines (20%, e.g., [66])"; "Documentation is incomplete if it does not contain the information about the system or its modules needed by practitioners/users to perform their tasks"; "lack of compatibility information (e.g., 'Explicitly mention if clang 4.x, 5.x are supported' [73])"; Fig. 1 taxonomy of "the 162 documentation issue types", Completeness branch, under "Missing/Poor documentation": "Missing supported versions", "Missing compatibility information", and "Missing configuration instructions" with its child "Missing required libraries".
- arXiv:2312.03250 (v2; published in IEEE Transactions on Software Engineering, 2025, DOI 10.1109/TSE.2025.3552614), abstract (fetched, arXiv listing mirror): "installation-related instructions, which are crucial for users to start with a software project"; "six major categories of changes in the README commits, namely pre-installation instructions, installation instructions, post-installation instructions, help information updates, document presentation, and external resource management"; "documentation readers find the augmented documents based on our template are generally of better quality".
- Caveat: the evidence measures issue frequency and practitioner ratings in open-source documentation, plus one reader survey of template-augmented documents; it does not measure the effect of a prerequisites list.

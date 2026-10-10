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

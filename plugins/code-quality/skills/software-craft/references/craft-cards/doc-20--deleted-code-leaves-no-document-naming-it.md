---
title: A change that deletes or renames a code element or command leaves no current document in the repository that still names it
rule_id: DOC-20
domain: docs
step: [implement, refactor, document, review]
applies_to: [universal]
triggers: ['^\s*((export\s+)?(default\s+)?(pub(\([\w:]+\))?\s+)?((public|protected|private|static|final|abstract|sealed|async|const|unsafe)\s+)*(def|fn|func|class|struct|interface|enum|trait|type|function)\s+(\([^)]*\)\s*)?[A-Za-z_]\w*|((public|protected|private|static|final|abstract|synchronized|override|async)\s+)+([\w<>\[\],.?]+\s+)?[A-Za-z_]\w*\s*\(|(export\s+)?const\s+[A-Za-z_]\w*\s*=\s*(async\s*)?(\(|function\b|[A-Za-z_]\w*\s*=>))', '`[A-Za-z_][\w.:]*\(\)`', '(?i)\b(remove[sd]?|rename[sd]?|delete[sd]?|drop(ped|s)?)\b.{0,40}\b(command|flag|option|function|class|method|module|package|endpoint|setting)(e?s)?\b']
scope: callers
check_kind: semantic
severity_default: minor
---

# A change that deletes or renames a code element or command leaves no current document in the repository that still names it

## Thesis
When a change deletes or renames a function, class, command, option or setting so that no source instance of the old name remains, each document in the repository that describes the current system and names the old name is updated in the same change, and such a document whose whole subject is gone is deleted.

## Rationale
One proposed reason documentation falls out of sync so easily is that developers are unaware when their source changes render a document obsolete. References to code elements survive in repository documentation after every source instance has been deleted: of over 3,000 GitHub projects analysed, most contained at least one such outdated reference at some point in their history, and more than a quarter of the 1,000 most popular GitHub projects contained at least one. A rename that keeps no alias leaves no source instance of the old name, the same state a deletion leaves. Mined documentation issues include documented code that does not exist in the system anymore, such as routines the documentation still mentions after they became unavailable, and code-documentation inconsistency, the survey item that groups behaviour described in the documentation but not implemented, was rated an important issue by 59% of surveyed practitioners. Documentation is changed in the same change as the code. A dead document misinforms its reader and slows the reader down. A change to how users build, test, interact with or release code is checked for updating its associated documentation, READMEs and generated reference docs included, and a change that deletes or deprecates code raises whether its documentation is deleted too. A scan for outdated code element references can run whenever a pull request is submitted.

## Example
```python
bad:  def load_settings(path): ...
      # CHANGELOG.md: Renamed function `read_settings()` to `load_settings()`.
      # README.md: Call `read_settings()` to load the file.
good: def load_settings(path): ...
      # CHANGELOG.md: Renamed function `read_settings()` to `load_settings()`.
      # README.md: Call `load_settings()` to load the file.
```

## Limits
The rule reaches documents that describe the system as it is now: a README, guide, how-to, tutorial, installation instruction or reference page. It depends on whether the document describes the current system or records history. On the current side, dead documentation is deleted and a change that alters how users interact with code updates its documentation. On the history side, an accepted proposal is a historical document rather than a living specification and is no longer substantially modified, a substantial change becomes a new proposal with a note added to the original, a decision record's status reads superseded with a pointer to the record that replaced it, and release notes summarise what changed in each published release; such a record keeps the old name. While a kept alias or shim still holds the old name in the source, a document naming it refers to an existing element, and the reference becomes outdated when the last source instance is deleted. Where it is unclear whether a passage still applies, the passage is left and what is certainly wrong is deleted first. Where the project's documented workflow accepts documentation in a separate change and the change description links that change, the linked change meets the rule. A design document whose code has been implemented is an archive of the decisions it records and keeps the old name, as an accepted proposal does.

## Validator
Grep the hunk for removed definition lines and for removed or renamed command, flag, option or setting names, and record each old name, including the old half of every rename. Search the source for each old name and drop any name that still has a source instance. Search the repository's documents for the remaining names: README files, documentation trees, guides, how-tos, tutorials, examples, installation instructions and reference pages. Skip hits in changelogs, release notes, accepted decision records, accepted proposals and design documents whose code is implemented. When the project's documentation build warns on every reference whose target cannot be found or on every link that fails to resolve, read its output for the old names too. Open each hit and check whether the document still names the old name once the change is applied. Validator question: **Does a document in the repository that describes the current system still name, once this change is applied, a function, class, command, option or setting that this change removed from every source location?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: DOC-20`, severity minor, `file`, `symbol`, `code` = the removed or renamed definition line from the diff and the document line that still names the old name, `fix` = the document line rewritten to the new name in the document's own markup, or the document deleted when its whole subject is gone, `rationale` = names the outdated reference and the change that removed the last source instance of its name).

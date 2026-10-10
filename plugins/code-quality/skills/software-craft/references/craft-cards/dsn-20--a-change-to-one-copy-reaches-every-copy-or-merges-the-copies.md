---
title: A change to one copy of duplicated code is made in every other copy meant to do the same thing, or the copies are merged into one
rule_id: DSN-20
domain: design
step: [implement, refactor, review]
applies_to: [universal]
triggers: []
scope: callers
check_kind: semantic
severity_default: major
---

# A change to one copy of duplicated code is made in every other copy meant to do the same thing, or the copies are merged into one

## Thesis
When the change alters the logic or functionality of a block of four or more lines, not counting blank and comment lines (a fix, for instance), and the repository holds another copy of that block meant to do the same thing, the change makes the same edit in every such copy, or merges the copies into one routine that every place calls. A copy is a block whose lines equal the edited block's pre-change lines once leading and trailing white space, blank lines and comments are set aside, or differ from them only in names. An edit that reaches one copy and leaves another copy meant to do the same thing unchanged is an inconsistent change.

## Rationale
When duplicated blocks are supposed to do the same thing, a future change needs to be made in all locations, and any refactoring, even a simple one, has to be duplicated too. Whoever changes the logic or functionality of duplicated code has to identify all the places that need the change, which can be time-consuming and error-prone, and has to test each copy. Having to make the change in every location opens the door to mistakes and to the change not being made in the same way in each instance: a programmer might fix a weakness in one copy while forgetting to fix the same weakness in another, and code duplicated in the branches of one conditional can potentially introduce bugs if one instance is changed but the others are not. In a large-scale case study of commercial and open-source systems, inconsistent changes to clones were very frequent, and the study identified a significant number of faults induced by such changes. Copies not kept in sync may no longer be recognised as duplicates by automated tools, so finding them falls to the maintainer, and segments of code initially supposed to do the same thing may grow apart undetected. A copy that nothing checks against its source after copying can fall behind it: of 153 clones copied from open-source projects to a programming Q&A site, 100 (66 percent) were outdated, and 10 of those were buggy and harmful for reuse. Identical or nearly identical copies also confuse the reader, who can skim them and think them identical when they are not, particularly during review. The documented mitigation is to merge the common functionality into a single routine and call it from every place, and a duplicate detector is advised as a means to remove duplicates, not to keep them in sync. A common duplicate-code check sets its minimum similarity to four lines by default and reports a match only when more than four of the matched lines contain code; it compares lines with leading and trailing white space removed, skips lines left empty, and leaves comments, docstrings, imports and signatures out. A detector option that replaces every identifier with one placeholder before comparing finds code that is structurally identical and differs only in naming.

## Example
```go
bad:  func create(u User) error { if u.Name == "" || len(u.Name) > maxLen { return errName }
          if u.Age < 0 { return errAge }
          if u.Email == "" { return errEmail }
          return save(u) }
      func rename(u User) error { if u.Name == "" { return errName } // not updated
          if u.Age < 0 { return errAge }
          if u.Email == "" { return errEmail }
          return save(u) }
good: func validate(u User) error { if u.Name == "" || len(u.Name) > maxLen { return errName }; if u.Age < 0 { return errAge }; if u.Email == "" { return errEmail }; return nil }
      func create(u User) error { if err := validate(u); err != nil { return err }; return save(u) } // rename likewise
```

## Limits
The rule holds for copies supposed to do the same thing, the copies for which any change has to be duplicated; a copy kept on purpose that is still meant to do the same thing receives the same edit. Cloning is also used as a principled engineering tool: in a case study of two medium-sized open-source systems, as many as 71% of the clones could be considered to have a positive impact on maintainability, and boiler-plating, replicate-and-specialize and cross-cutting concerns were found to be mostly good patterns. A block replicated in order to be specialized, or a variant kept for another platform, is outside the rule where its copy is made to diverge; a documented project tolerance that names copies kept apart on purpose rejects the finding for those copies. An edit that adds a new feature to an experimental copy of a subsystem, tried there as in a sandbox, is outside the rule too: the feature reaches the stable code once it matures and is migrated there. The finding is the inconsistent edit, not the existence of copies: one study found the great majority of bugs not significantly associated with clones.

## Validator
Read every hunk, since no added-line pattern marks an edit to one copy of a block. Take each hunk that removes or replaces lines inside existing code, or inserts lines between existing ones, and so alters what that code does; skip an added file, a hunk that only appends new routines, and a hunk that only renames, re-indents or edits comments. Rebuild the pre-change text of the edited block: the removed lines together with the unchanged context lines around the edit, four or more lines in all once blank and comment lines are dropped. Search the repository at HEAD or in the working tree for each removed line of the hunk that is neither a brace nor a bare return (when there is none, as for a pure insertion, the nearest such unchanged line above the edit and the one below it), longest first, once verbatim and once with its identifiers replaced by a wildcard. For each hit outside the edited span, compare the four or more lines around it with the pre-change block, apart from indentation, blank lines, comments and names. For each copy found, check whether the diff gives it the same edit, or replaces it with a call to one routine that now holds the edited block. Judge whether the copy is meant to do the same thing: it plays the same role for the same kind of data, and the reason for the edit (the bug fixed, the case added, the value changed) applies to it as well. Treat it as made to diverge when its comments or a documented project tolerance say so, or when the edit adds a new feature inside an experimental or sandbox copy of a subsystem and the copy is the stable code that feature is migrated to once it matures. Validator question: **Does the change alter the logic or functionality of a block of four or more lines while another copy of that block, meant to do the same thing, keeps the pre-change text and receives neither the same edit nor a call to one shared routine?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: DSN-20`, severity major, `file`, `symbol`, `code` = the edited lines of the changed copy, quoted verbatim from the diff, `fix` = the same edit applied to each copy left unedited, or one routine holding the edited block that every copy's place calls, in the file's language, `rationale` = names the file and symbol of each copy left unedited and the edit it lacks).

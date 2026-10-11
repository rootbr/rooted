---
title: A change that removes or reverses a guard, special case or workaround whose comment, issue reference or dedicated test records why it exists shows that the recorded reason no longer applies
rule_id: DOC-03
domain: docs
step: [refactor, implement, review]
applies_to: [universal]
triggers: ['^\s*([}]\s*)?(if|elif|else\s+if|unless|guard|when|case|match|switch)\b', '(?i)\b(workaround|work-around|hack|special[- ]?case|quirk|legacy|compat(ibility)?)\b', '(?i)\b(no longer (needed|required|necessary)|not needed|unnecessary|obsolete|redundant)\b']
scope: base-compare
check_kind: semantic
severity_default: minor
---

# A change that removes or reverses a guard, special case or workaround whose comment, issue reference or dedicated test records why it exists shows that the recorded reason no longer applies

## Thesis
A change that deletes or inverts a guard, special case or workaround whose comment, linked issue or dedicated test records why it exists shows that this recorded reason no longer applies, in the change's description or in the test for that case, which the change keeps.

## Rationale
Source code may reveal what the software is doing but may not reveal why it exists, which can make it harder for a later developer to know whether a guard can be removed or changed. Later developers search for a change by its description, and after finding it they look to understand why the change was made. In an observational study of seventeen developers at a large software company, the most often deferred searches included knowledge of why code was written a particular way and of what a program was supposed to do. To judge whether a value was wrong, those developers had to consider whether the designer had anticipated it and explicitly ignored it or had overlooked it, and they did so by investigating the code's change history or by looking for bug reports that held hints about its current design. In git, blame annotates each line with the revision that last modified it and tells nothing about lines deleted or replaced; the pickaxe tracks when a snippet was added, moved or copied, and deleted or replaced. Fed iteratively with the earlier block, `-S` reaches the very first version of that block, and `-G` finds changes whose added or removed lines match a pattern. `log -L` traces the evolution of a line range, or of a function found by a name pattern, within a file, and `blame --ignore-rev` assigns blame as if a chosen revision never happened, giving the lines it changed or added to the previous commit that changed those lines or nearby lines.

## Example
```typescript
bad:  // change "Remove unnecessary empty-body check" deletes its test and this line from read:
      if (body === "") return emptyItem; // workaround for the linked parser issue
      function read(body: string): Item { return parse(body); }
good: // change description: "Remove the empty-body check: parse returns emptyItem
      // for an empty body now that the linked issue is fixed; its test is kept"
      function read(body: string): Item { return parse(body); }
      test("read returns emptyItem for an empty body", () => {
        assert.deepEqual(read(""), emptyItem);
      });
```

## Limits
Code whose reason was never recorded in a comment, a linked issue or a test is outside the rule, and so is a guard that the change moves, together with its comment, to the code that now handles the case, and so is a condition that the change inverts while swapping its branches, so that the case still takes the path the guard gave it. The histories of even simple bugs are strongly dependent on social, organizational and technical knowledge that cannot be extracted from electronic repositories by automation alone, and such automation gives incomplete and often erroneous accounts of coordination, so an empty search of those repositories is no proof that code is unneeded, and the rule asks the change to answer only a reason that is on record. In the observational study of seventeen developers, developers also sought the design rationale from the code's author through face-to-face conversation or other means, and in one case the author was unavailable.

## Validator
Read the hunk's deleted lines and the lines that replace them for a condition, an early return or throw, or a branch that the change deletes or inverts, and grep the hunk and the nearby base comments for workaround, hack, special case, quirk, legacy, compatibility, no longer needed, unnecessary, obsolete or redundant. Open the base version of the file and read the comment above or beside that code for a stated reason, an issue reference or a link; grep the base's test files for a test named for that case; when the reason is still unclear, run `git log -S'<deleted snippet>'` or `git log -L:<function>:<path>` on the base and read the commit that added the code, stepping past a commit that only reformatted with `git blame --ignore-rev`. Then read the change's commit messages, the comments it adds and its test files. Count the reason as answered when the description states why the recorded reason no longer applies, for example that the linked issue is resolved, that the condition the comment names no longer occurs, or where the case is now handled, or when the test for that case stays unchanged; a guard moved together with its comment to the code that now handles the case is no deletion, and a condition inverted with its branches swapped, so that the case still takes the same path, is no inversion. Validator question: **Does the change delete or invert code whose base-version comment, linked issue or dedicated test records why it exists, with neither its description nor a kept test for that case showing that the recorded reason no longer applies?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: DOC-03`, severity minor, `file`, `symbol`, `code` = the deleted or inverted line quoted verbatim from the diff together with the base-version comment, issue reference or test name that records its reason, `fix` = a description line stating why the recorded reason no longer applies, or the test for that case restored in the file's language, `rationale` = names the recorded reason and the case the deleted code handled).

## Source
- Google Engineering Practices, "Writing good CL descriptions" (google/eng-practices, review/developer/cl-descriptions.md): "Reading source code may reveal what the software is doing but it may not reveal why it exists, which can make it harder for future developers to know whether they can move [...] fence."; "Future developers will search for your CL based on its description."; "after they find the CL, will they be able to understand *why* the change was made?" (fetched)
- "Information Needs in Collocated Software Development Teams", ICSE 2007, DOI 10.1109/ICSE.2007.45, Abstract and §5.6 "Reasoning about Design": "We observed seventeen developers at a large software company"; "The most often deferred searches included knowledge about design and program behavior, such as why code was written a particular way, what a program was supposed to do, and the cause of a program state."; "developers had to consider whether the value was anticipated by the designer and explicitly ignored or whether it was overlooked. They would do this by investigating the code's change history [...] or by looking for bug reports that contained hints about its current design"; "Developers would seek this design rationale from the author of the code through face-to-face conversation or some other means [...], but in one case the author was unavailable" (fetched)
- "The secret life of bugs: Going past the errors and omissions in software repositories", ICSE 2009, DOI 10.1109/ICSE.2009.5070530, Abstract: "the histories of even simple bugs are strongly dependent on social, organizational, and technical knowledge that cannot be solely extracted through automation of electronic repositories, and that such automation provides incomplete and often erroneous accounts of coordination" (fetched)
- Git documentation, git-blame(1) DESCRIPTION: "Annotates each line in the given file with information from the revision which last modified the line."; "The report does not tell you anything about lines which have been deleted or replaced"; "track when a code snippet was added to a file, moved or copied between files, and eventually deleted or replaced" (fetched)
- Git documentation, diff options `-S<string>`: "use the feature iteratively to feed the interesting block in the preimage back into `-S`, and keep going until you get the very first version of the block"; `-G<regex>`: "Look for differences whose patch text contains added/removed lines that match <regex>." (fetched)
- Git documentation, git-log(1) `-L`: "Trace the evolution of the line range given by <start>,<end>, or by the function name regex <funcname>, within the <file>."; git-blame(1) `--ignore-rev <rev>`: "Ignore changes made by the revision when assigning blame, as if the change never happened. Lines that were changed or added by an ignored commit will be blamed on the previous commit that changed that line or nearby lines." (fetched)
- Caveat: the 2007 study observed seventeen developers at one company; the 2009 finding concerns repository accounts of coordination around bug fixes, read here as a limit on what a history search shows.

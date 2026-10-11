---
title: The first line of a change description is a short summary of what the change does that reads on its own without the rest of the description, followed by a blank line
rule_id: DOC-06
domain: docs
step: [document, review]
applies_to: [universal]
triggers: ['\b(def|fn|func|function|class|struct|interface|trait|enum|impl)\s+\w+', '\b(if|elif|else|switch|match|case|for|while|return|throw|raise)\b', 'signal:added_file']
scope: base-compare
check_kind: semantic
severity_default: suggestion
---

# The first line of a change description is a short summary of what the change does that reads on its own without the rest of the description, followed by a blank line

## Thesis
The first line of a change description is a short summary of specifically what the change does, informative enough to stand alone, so that a reader skimming the history learns what the change did and how it differs from other changes without opening the change or its whole description; a blank line follows it.

## Rationale
The first line is what appears in version-control history summaries, and a version-control tool's own documentation treats the text up to the first blank line of a commit message as the commit title, the line it puts on the subject line when it turns a commit into an e-mail. A reader going through perhaps thousands of changes in history tools two or three months later may quickly see this line and nothing else, so a first line that stands alone lets readers skim the history much faster. A first line such as "Fix bug" is inadequate (what bug, and what was done to fix it?), and so are "Fix build.", "Add patch." and "Phase 1.": although short, they do not provide enough useful information. In that tool the title runs up to the first blank line, so the blank line is what keeps the summary apart from the rest of the description.

## Example
```typescript
bad:  const description = "Fix bug\nparse returned [''] for empty input.";
      function parse(s: string): string[] {
        if (s === "") throw new Error("empty input");
        return s.split(",");
      }
good: const description = "Reject empty input in parse\n\nparse returned [''] for empty input.";
      function parse(s: string): string[] { ... }
```

## Limits
The first line's grammatical form, its length limit and any prefix come from the project's documented commit-message convention, and the documented conventions differ. One review guide asks for a complete sentence written as though it were an order (an imperative sentence). One language project's contribution guide asks, as a rule of thumb, for a phrase that completes "This change modifies [the project] to ___", prefixed by the primary affected package, that does not start with a capital letter and is not a complete sentence. A version-control tool's own documentation advises, though not as a requirement, a line of no more than 50 characters, calls 50 characters a soft limit, asks to skip the full stop, and calls an "area: " prefix conventional in most cases. One kernel's process documentation sets the summary at no more than 70-75 characters and asks it to describe both what the patch changes and why the patch might be necessary. One review tool's documentation calls the title's maximum length, its period and its voice or tense probably not really all that important, and structurally asks for a title briefly describing the change in one line. Every one of these conventions asks for a short one-line summary of the change, and three of them ask for a blank line after it; the rule carries only that shared content.

## Validator
Open the change description that accompanies the diff (the commit message, or the pull- or merge-request title and description); when the review carries no description, answer no. Take its first line and the line after it. Grep the hunks for the routines, types and files the diff adds or changes, and read the first line against them: it names what this diff does in terms that tell it apart from other changes in the history. Compare it with lines that name nothing the diff does, such as "Fix bug", "Fix build", "Add patch" or "Phase 1". Where the description is one text with a body, check that the second line is blank. Leave the first line's grammatical form, length and prefix unflagged: the project's documented convention sets them, and this rule does not check them. Validator question: **Does the first line of the change description fail to summarise on its own what this diff does, or run on into the body without a blank line?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: DOC-06`, severity suggestion, `file`, `symbol`, `code` = the description's first line and the line after it, quoted verbatim, `fix` = a first line that names what the diff does, in the project's documented form, followed by a blank line, `rationale` = that history summaries and one-line logs show this line on its own).

## Source
- google/eng-practices, review/developer/cl-descriptions.md, "First Line" (fetched): "The first line of a CL description should be a short summary of specifically what is being done by the CL, followed by a blank line. This is what appears in version control history summaries, so it should be informative enough that future code searchers don't have to read your CL or its whole description to understand what your CL actually did or how it differs from other CLs. That is, the first line should stand alone, allowing readers to skim through code history much faster." / "By tradition, the first line of a CL description is a complete sentence, written as though it were an order (an imperative sentence)."
- google/eng-practices, review/developer/cl-descriptions.md, "Bad CL Descriptions" (fetched): "\"Fix bug\" is an inadequate CL description. What bug? What did you do to fix it? Other similarly bad descriptions include: \"Fix build.\" \"Add patch.\" \"Moving code from A to B.\" \"Phase 1.\" [...] Although short, they do not provide enough useful information."
- golang/website, _content/doc/contribute.html, "Good commit messages" > "First line" (fetched): "The first line of the change description is conventionally a short one-line summary of the change, prefixed by the primary affected package. [...] That means it does not start with a capital letter, is not a complete sentence, and actually summarizes the result of the change." / "Follow the first line by a blank line."
- git/git, Documentation/git-commit.adoc, DISCUSSION (fetched): "Though not required, it's a good idea to begin the commit message with a single short (no more than 50 characters) line summarizing the change, followed by a blank line and then a more thorough description. The text up to the first blank line in a commit message is treated as the commit title, and that title is used throughout Git. For example, linkgit:git-format-patch[1] turns a commit into email, and it uses the title on the Subject line"
- git/git, Documentation/SubmittingPatches (fetched): "The first line of the commit message should be a short description (50 characters is the soft limit, see DISCUSSION in linkgit:git-commit[1]), and should skip the full stop. It is also conventional in most cases to prefix the first line with \"area: \""
- torvalds/linux, Documentation/process/submitting-patches.rst, subject line (fetched): "It will also be the only thing that people may quickly see when, two or three months later, they are going through perhaps thousands of patches using tools such as gitk or git log --oneline." / "the summary must be no more than 70-75 characters, and it must describe both what the patch changes, as well as why the patch might be necessary."
- phacility/phabricator, src/docs/flavor/writing_reviewable_code.diviner (fetched): "Have a title, briefly describing the change in one line." / "Some things that people sometimes feel strongly about but which are probably not really all that important in commit messages include: [...] Maximum length of the title. Whether there should be a period or not in the title. Use of voice/tense"
- Caveat: these are documented project conventions; none of them measures the effect of a first line's quality on readers.

---
title: A context file that states the project's conventions gives the existing code precedence wherever the two disagree
rule_id: R-48
applies_to_target: [context-file]
check_kind: mechanical
severity_default: medium
---

# A context file that states the project's conventions gives the existing code precedence wherever the two disagree

## Thesis
A context file that states how the project's code is written carries one sentence saying that the existing code takes precedence over the file wherever the two disagree, and asking the agent to point out each disagreement it found in its final reply.

## Rationale
The file reaches the model as an instruction and the code only as the output of a file-reading tool, which instruction-hierarchy training ranks lower, so a convention line the code has moved past keeps an instruction's authority. In projects whose file prescribed a convention the code no longer used, coding agents adding a feature followed the file in 90.1% of their convention choices and the code in 4.2%. One agent named the conflict in 79 of 80 runs and still followed the file in 86.2% of its choices in those runs; another rewrote existing code to match the file in 20 of 80 runs, and the project's tests then failed in 17 of them. With the sentence, 91.4% of choices followed the code — 87.2 points more, 95% interval 83.6 to 90.9 — no run rewrote existing code, the tests passed in every run, and both agents pointed out the disagreements they found, which name the lines to correct. The sentence takes effect without anyone first finding the stale line.

## Example
```
bad:  a Conventions section that says "Use print() for progress messages." and nothing on what wins when the code differs
good: the section ends: "When a repository's documentation and its existing code disagree, follow the conventions used in the existing code, and in your final reply point out each inconsistency you found between the documentation and the code."
```

## Limits
Applies to a file that states conventions of the project's code — naming, error handling, logging, test style, formatting, library choices; a file of commands, workflow or tool settings states nothing the code can contradict. The measured sentence stood in the agents' user-level instruction file, loaded in the same message as the project's file and ahead of it, not in the project's own file; the projects were small and constructed, and in every disagreement the file was the outdated side. Where a file deliberately prescribes a convention the code is being moved toward, the sentence works against that line. The sentence ranks the code above the file's account of it; it is not a precedence between two rules of the file.

## Validator
Decide whether the file states conventions of the project's code. If it does not, emit nothing. If it does, look for a sentence that gives the existing code precedence over the file, or over the project's documentation, where the two disagree, and asks for each disagreement to be pointed out. Flag the file when the sentence is absent or carries only one of its two halves. Validator question: should one convention line here go stale, does the file itself tell the agent to follow the code and to report the line?

## Patch output
When a file that states conventions of the project's code lacks the sentence or one of its halves, emit one patch (`rule_id: R-48`, `location.section` = the section that states the conventions, `current` = the half-sentence where one stands, else that section's heading line, severity medium) proposing that text followed by, or replaced with, the sentence "When a repository's documentation and its existing code disagree, follow the conventions used in the existing code, and in your final reply point out each inconsistency you found between the documentation and the code."; set `needs_human: true` when the file prescribes a convention the code is being moved toward.

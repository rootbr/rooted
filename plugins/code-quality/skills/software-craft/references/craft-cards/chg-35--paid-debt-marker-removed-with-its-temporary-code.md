---
title: A change that does the work an existing debt marker records, or meets the condition that ends the need for its temporary code, removes that marker and that temporary code in the same change
rule_id: CHG-35
domain: change
step: [implement, refactor, document]
applies_to: [universal]
triggers: ['signal:todo_marker', '\b(TODO|FIXME|HACK|XXX)\b', '(?i)(legacy|fallback|workaround|temporary|deprecated)']
scope: callers
check_kind: semantic
severity_default: minor
---

# A change that does the work an existing debt marker records, or meets the condition that ends the need for its temporary code, removes that marker and that temporary code in the same change

## Thesis
When a change does the work that a debt marker already in the touched code records, or meets the event or condition that ends the need for the temporary code the marker covers, such as the closing of the issue a workaround waits on, the same change removes the marker together with that temporary code; a marker whose recorded work is still undone after the change stays, such as an on-hold marker whose blocking issue is still open, or one whose condition the change meets while the task that follows the condition remains.

## Rationale
A debt marker is a comment in which developers admit a hack they made consciously, as a reminder; its purpose is to keep track of the debt and to address it when possible. Markers track potential bugs, code that needs improvement and features still to implement, and in a survey with 14 responses, developers report removing them mostly while fixing bugs or adding features and seldom as part of refactoring. An on-hold marker records a task halted by a condition outside the scope of the work, such as an open issue that must be closed before a routine can be implemented; a tool study that mines the issue tracker counts an on-hold marker whose referenced issue has been closed, while the marker is still in the code, as superfluous, and original developers confirmed such markers in open source projects. A closed issue ends the wait, not the deferred task: the marker goes once the closing ends the need for the temporary code it covers or the change also does the deferred task, and stays while that task remains, since a marker keeps track of debt until the debt is addressed. In review, it can help to look at the comments that were there before the change: a TODO among them may be removable now. Addressing the debt changes code, not only the comment: most changes that address a marker's debt are complex source changes, and very often the debt is addressed by specific changes to method calls or conditionals.

## Example
```rust
bad:  // TODO: temporary constant; read the timeout from the config
      const TIMEOUT_SECS: u64 = 30;
      fn timeout(cfg: &Config) -> Duration { Duration::from_secs(cfg.timeout_secs) }
good: fn timeout(cfg: &Config) -> Duration { Duration::from_secs(cfg.timeout_secs) }
```

## Limits
A marker whose recorded work is still undone after the change stays as it is, including an on-hold marker whose blocking issue is still open and a marker whose waiting condition the change meets while the task that follows that condition remains; an open issue that tracks the marker's own work, alone or with other markers, does not keep a marker whose work the change has done. An issue reference that documents the code, for example to explain the rationale behind an implementation choice, is a cross-reference rather than an on-hold marker, and the closed-issue test applies to on-hold markers only. The rule reaches the markers in the files a change touches; superfluous markers elsewhere in the codebase are found by mining the issue tracker for closed references, outside any one change.

The finder reaches the card through an added line that carries a marker or a word of temporariness: a rewritten marker, a comment the change edits beside the marker, or a new fallback or workaround; a change that does the marker's work while adding no such line is not dispatched by the diff alone.

## Validator
Grep the touched file, beyond the hunk, for the project's debt marker: a debt keyword in a comment, a workaround note, or an issue reference beside a waiting condition such as once, until or when. Select the markers that predate the change. For each, read the work it records or the event or condition it waits for, then trace the change: an added or changed line that implements that work, or a change that closes the referenced issue, migrates the last caller of the covered path or otherwise meets the condition. Open the code the marker covers, such as a constant, a fallback branch, a shim or a compatibility call, and check whether it is still present and, after the change, unused or unreachable. Leave a marker whose recorded work is undone or only partly done after the change, including an on-hold marker whose blocking issue the change does not close and a marker whose condition the change meets while the task that follows it remains; an open issue that tracks the marker's own work does not keep a marker whose work the change has done. Validator question: **Does the change do the work a pre-existing debt marker in the file records, or meet the event or condition that ends the need for the temporary code it covers, while leaving that marker or that temporary code in place?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: CHG-35`, severity minor, `file`, `symbol`, `code` = the added line that does the recorded work or meets the marker's condition, quoted verbatim from the diff, with the marker or temporary code it leaves in place, `fix` = the same code with the marker and the temporary code it covers removed, in the file's language, `rationale` = the work or condition the marker records and the changed line that does that work or meets that condition).

## Source
- Google Engineering Practices, "What to look for in a code review", section Comments, google/eng-practices review/reviewer/looking-for.md (fetched): "It can also be helpful to look at comments that were there before this CL. Maybe there is a TODO that can be removed now".
- DOI 10.1109/SCAM51674.2020.00011, SCAM 2020, abstract (fetched): "developers consciously perform the hack but also document it in the code by adding comments as a reminder"; "the need to halt an implementation task due to conditions outside of their scope of work (e.g., an open issue must be closed before a function can be implemented)"; "the issue is referenced to document the code, for example to explain the rationale behind an implementation choice"; "mines the issue tracker of the projects to check if the On-hold SATD instances are “superfluous” and can be removed (i.e., the referenced issue has been closed, but the SATD is still in the code)"; "identifying superfluous On-hold SATD instances in open source projects as confirmed by the original developers".
- DOI 10.1109/ICSME.2017.8 (unfetched), ICSME 2017, RQ4 conclusion in the paper's source, maldonado/msr16_td_removal paper/results.tex (fetched): "Developers add self-admitted technical debt to track potential future bugs, code that needs improvements or areas to implement new features. Developers mostly remove self-admitted technical debt when they are fixing bugs or adding new features. Very seldom do developers remove self-admitted technical debt as part of refactoring efforts or dedicated code improvement activities." Caveat: the removal-activity finding rests on a developer survey with 14 responses, whose tally in results.tex reads "The second most frequent reasons is to add a new feature (P1, P4, P6, P12, and P14) and improve the code overall (P7, P8, P9, P10, and P11)", so the card does not carry the conclusion's clause on dedicated code improvement activities.
- MSR 2018, pp. 526–536, IEEE Xplore article 8595236, abstract (fetched): "The purpose of such comments is to keep track of TD and appropriately address it when possible"; "while most of the changes addressing SATD require complex source code changes, very often SATD is addressed by specific changes to method calls or conditionals". Caveat: five Java open source projects.

---
title: A numbered decision record that a change adds takes the next number in its log's sequence, a number no other record in the same log directory holds
rule_id: ARCH-48
domain: architecture
step: [document, review]
applies_to: [prose]
triggers: ['signal:added_file', '(?i)\b(ADR|RFC)[-\s]?\d{1,4}\b']
scope: base-compare
check_kind: mechanical
severity_default: suggestion
---

# A numbered decision record that a change adds takes the next number in its log's sequence, a number no other record in the same log directory holds

## Thesis
Where a project numbers its decision records, a record that a change adds to a log directory, a record it renumbers by a rename included, takes the next number in its log's sequence, and that number is one no other record in the same directory holds, with numbers compared as integers. Where the log is split into category subdirectories that each keep their own sequence, the numbers are unique within each subdirectory.

## Rationale
A record is referred to by its number: a superseding record and a link to an earlier decision name their target by number or by file name, so a reference such as "ADR-12" names exactly one record only while one record in the directory holds 12. Two branches that each take "the next number" add files whose names differ, so no lines conflict and the merge accepts both without complaint; the duplicate surfaces months later, when a reference to that number turns out to be ambiguous. A conflict on a shared counter file is noisy but safe, because the merge refuses it and someone renumbers; the silent duplicate is the dangerous variant. Numbers compare as integers because different padding is how renumbering mistakes look: `007` and `0007` are the same number. A published template writes the number as a consecutive four-digit field, assuming no more than 9,999 records in one repository, and a published log tool computes the next number as the highest number in the directory plus one.

## Example
```go
bad:  records := []string{"0011-use-relational-store.md", "0012-split-billing.md"}
      records = append(records, "0012-adopt-message-queue.md") // ADR-12 names two records
good: records := []string{"0011-use-relational-store.md", "0012-split-billing.md"}
      records = append(records, "0013-adopt-message-queue.md")
```

## Limits
Where each category subdirectory keeps its own sequence, the same number in two subdirectories is correct; a log numbered across all its subdirectories can hold one number in two subdirectories, a duplicate this per-directory comparison does not see. A gap in the sequence, numbers skipped because records were withdrawn or a range was reserved, is usually deliberate and is not a finding; the finding is a number held twice in one directory. Files without a numeric prefix, such as a README, a template or an index, live in a log directory legitimately and fall outside the rule. A project that names its records by title alone, such as `choose-database.md`, carries no number to collide, and a repository without a decision-log directory has not opted into numbered records; the rule reaches neither. Two changes that branch from one base and each take the next number both pass against that base, and the merge of the second is clean; the duplicate becomes visible only once the first has merged, to a review of the second that reads the target branch's current head or to a check of the merged directory. Which of two colliding records moves is a judgement for the authors, and the fix is a one-commit rename.

## Validator
Take each added file under a decision-log directory, a directory such as `docs/decisions/` or `docs/adr/` whose records carry a numeric prefix, and count as added the new path of a record the change renames to a different number. Read the added record's number from its file-name prefix (`0012-title.md`, `0012_title.md`, `0012.md`); an added file without a numeric prefix falls outside the rule. List the files the same directory holds at the change's base revision and, where the review knows the current head of the branch the change merges into, at that head as well, together with every other record the change adds to that directory; skip files without a numeric prefix and every file the change deletes or renames away, and read each number as an integer with leading zeros dropped. Compare within that one directory, never across category subdirectories, and ignore gaps. Where both holders of a number are records the change adds, report the pair once. Validator question: **Does another record in the same log directory, at the base revision, at the target branch's current head or added by the same change, hold the number the added record takes, compared as integers?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: ARCH-48`, severity suggestion, `file`, `symbol`, `code` = the added record's file name and its heading line, verbatim, `fix` = a one-commit rename of one of the two colliding records, normally the added one and as the authors choose, to the highest number held in its log directory by the records at the target branch's current head, or at the base revision where that head is unknown, and by the records the change adds there, plus one, with its heading and every reference to it carrying the new number, `rationale` = the number already held and the file that holds it, so a reference by that number names two records).
